from flask import Flask, render_template, redirect, request 
from sensu_requests import SensuRequestHandler
from config import settings
from utils import prettify_relative_time
import datetime

app = Flask(__name__, static_url_path='/')
handler = SensuRequestHandler(settings=settings)


@app.route("/")
def index():
    return render_template('index.html', settings=settings)


@app.route("/checks")
def checks():
    items = handler.get_checks()
    current_time = datetime.datetime.utcnow()
    return render_template('checks_table.html',
                           items=items,
                           time=current_time)


@app.route("/events")
def events():
    items = handler.get_events()
    current_time = datetime.datetime.utcnow()
    return render_template('events_table.html',
                           items=items,
                           time=current_time)


@app.route("/silenced")
def silenced():
    items = handler.get_silenced()
    current_time = datetime.datetime.utcnow()
    return render_template('silenced_table.html',
                           items=items,
                           time=current_time)

# Kind of a hacky workaround to get the dashboard url 
@app.route("/dashboard")
def dashboard():
    if settings.ood_use_tls:
        schema = 'https'
    else:
        schema = 'http'
    return redirect(f"{schema}://{request.host}")


@app.template_filter('prettify_ts')
def prettify_ts(ts):
    target_date = datetime.datetime.fromtimestamp(ts)
    current_date = datetime.datetime.now()
    delta = (current_date - target_date).seconds
    return prettify_relative_time(delta)


if __name__ == "__main__":
    app.run()
