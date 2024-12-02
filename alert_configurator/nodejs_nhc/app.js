const path = require('path');
const express = require('express');
const axios = require('axios');
const fs = require('fs-extra');
const os = require('os');
const jwt = require('jwt-decode');
const ini = require('ini'); 
const app = express();
const port = 3000;

const homeDir = os.homedir();
let TOKEN_FILE;

async function checkDirectory() {
  try {
    await fs.promises.access(homeDir, fs.constants.R_OK | fs.constants.W_OK);
    TOKEN_FILE = path.join(homeDir, '.luna-token.dat');
  } catch (err) {
    TOKEN_FILE = {
      error: `The home directory '${homeDir}' does not exist or lacks read/write permissions.`
    };
  }

  console.log(TOKEN_FILE);
}
checkDirectory();


async function checkIniFile() {
  try {
    await fs.promises.access(INI_FILE, fs.constants.R_OK | fs.constants.W_OK);
    const config = ini.parse(fs.readFileSync(INI_FILE, 'utf-8'));
    const username = config.API.USERNAME || '';
    const password = config.API.PASSWORD || '';
    const secretKey = config.API.SECRET_KEY || '';
    const daemon = `${config.API.PROTOCOL}://${config.API.ENDPOINT}` || '';
    console.log('INI File Data:', config);
    TOKEN_FILE = path.join(os.homedir(), '.luna-token.dat');
    console.log('TOKEN_FILE:', TOKEN_FILE);
  } catch (err) {
    console.error('Error accessing INI file or parsing it:', err.message);
    TOKEN_FILE = {
      error: `Error with the INI file: ${err.message}`
    };
  }
}
checkIniFile();

const INI_FILE = '/trinity/local/ondemand/3.0/config/luna.ini';
const basePath = process.env.PASSENGER_BASE_URI || '/';
const table = 'Monitor'
const table_cap = 'Alert Configurator'
const TRIX_CONFIG = '/trinity/local/etc/prometheus_server/rules/trix.rules'

app.use(express.json());
app.set('views', path.join(__dirname, 'public/views'));
app.set('view engine', 'ejs');  // template engine to EJS
app.use('/pun/dev/nodejs_nhc/static', express.static(path.join(__dirname, 'public/static')));

const router = express.Router();
app.use(process.env.PASSENGER_BASE_URI || '/', router);


router.get('/', (req, res) => {
  res.render('index', {
    basePath: basePath,
    table: table,
    table_cap: table_cap,
    TRIX_CONFIG: TRIX_CONFIG,
  });
});



class Rest {
  constructor() {
    this.logger = console;
    this.errors = [];
    this.getIniInfo();
    this.security = this.security.toLowerCase() === 'y' || this.security.toLowerCase() === 'yes' || this.security.toLowerCase() === 'true';
    this.session = axios.create();
    this.session.defaults.timeout = 5000;
    this.session.defaults.headers.common['Content-Type'] = 'application/json';
  }

  getIniInfo() {
    this.username = '';
    this.password = '';
    this.daemon = '';
    this.secretKey = '';
    this.security = '';
    const iniFileExists = fs.existsSync(INI_FILE);

    if (!iniFileExists) {
      this.errors.push(`Luna Configuration File Not Found. Default Path is: ${INI_FILE}`);
    } else {
      const ini = require('ini');
      const config = ini.parse(fs.readFileSync(INI_FILE, 'utf-8'));
      
      if (config.API) {
        this.username = config.API.USERNAME || '';
        this.password = config.API.PASSWORD || '';
        this.secretKey = config.API.SECRET_KEY || '';
        this.daemon = `${config.API.PROTOCOL}://${config.API.ENDPOINT}` || '';
        this.security = config.API.VERIFY_CERTIFICATE || 'false';
      } else {
        this.errors.push(`API section is not found in ${INI_FILE}.`);
      }
    }
  }

  async token() {
    const data = { username: this.username, password: this.password };
    const daemonUrl = `${this.daemon}/token`;
    try {
      const response = await this.session.post(daemonUrl, data, { headers: { 'x-access-tokens': '' } });
      if (response.data && response.data.token) {
        const token = response.data.token;
        await fs.writeFile(TOKEN_FILE, token, { encoding: 'utf-8' });
        fs.chmodSync(TOKEN_FILE, 0o600);
        return token;
      } else if (response.data.message) {
        this.errors.push(response.data.message);
        return null;
      }
    } catch (error) {
      this.errors.push(`Error getting token: ${error.message}`);
      return null;
    }
  }

  async getToken() {
    let tokenData = '';
    if (fs.existsSync(TOKEN_FILE)) {
      tokenData = await fs.readFile(TOKEN_FILE, 'utf-8');
      try {
        jwt(tokenData);
        return tokenData;
      } catch (e) {
        this.logger.log('Token expired or invalid, getting new token');
        return await this.token();
      }
    } else {
      return await this.token();
    }
  }

  async getRules() {
    const token = await this.getToken();
    const headers = { 'x-access-tokens': token };
    const daemonUrl = `${this.daemon}/export/prometheus_rules`;
    try {
      const response = await this.session.get(daemonUrl, { headers: headers });
      if (response.data.message) {
        this.errors.push(response.data.message);
        return [false, this.errors];
      } else {
        return [true, response.data];
      }
    } catch (error) {
      this.errors.push(`Error fetching rules: ${error.message}`);
      return [false, this.errors];
    }
  }

  async postRules(data) {
    const token = await this.getToken();
    const headers = { 'x-access-tokens': token, 'Content-Type': 'application/json' };
    const daemonUrl = `${this.daemon}/import/prometheus_rules`;
    try {
      const response = await this.session.post(daemonUrl, data, { headers: headers });
      if (response.data.message) {
        return [200, response.data.message];
      } else {
        return [200, response.data];
      }
    } catch (error) {
      this.errors.push(`Error posting rules: ${error.message}`);
      return [400, this.errors];
    }
  }
}

const rest = new Rest();

router.get('/get_rules', async (req, res) => {
  try {
    const [status, data] = await rest.getRules();
    if (status) {
      res.status(200).json(data);
    } else {
      console.error('Error fetching rules:', data);
      res.status(400).json(data);
    }
  } catch (error) {
    console.error('Unexpected error:', error.message);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});


router.post('/save_config', async (req, res) => {
  const configData = req.body;
  const [status, data] = await rest.postRules(configData);
  res.status(status).json(data);
});


app.listen(port, () => {
  console.log(`NHC app listening on port ${port}`);
  console.log(`PASSENGER_BASE_URI  ${basePath}`);
})
