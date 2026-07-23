const tables = {};
const baseUrl = window.location.href.split("?")[0];
const nameRegexValidator = "regex:^[a-zA-Z0-9_\-]+$";
const HWPresetEditorParams = {
    valuesLookup: function(){
        return tables.hw_presets.getData().map(function(row) {
            return row.name;
        });
    },
    clearable: true,
};
const NodesEditorParams = {
    valuesLookup: function(){
        var groupedNodes = {};
        var spareNodes = [];
        var values = [];
        
        // Collect and sort nodes by group
        tables.nodes.getData().forEach(function(row) {
            if ((row.group_name==undefined) || (row.group_name == "")) {
                spareNodes.push(row.name);
            } else {
                if (groupedNodes[row.group_name] == undefined) {
                    groupedNodes[row.group_name] = [];
                }
                groupedNodes[row.group_name].push(row.name);
            }
        });
        // Build the group objects
        Object.keys(groupedNodes).forEach(function(group) {
            values.push({
                label: group,
                options: groupedNodes[group].map(function(node) {
                    return {label: node, value: node}
                })
            });
        });
        // Add the spare nodes
        values.push({
            label: "Spare Nodes",
            options: spareNodes.map(function(node) {
                return {label: node, value: node}
            })
        });
        return values;
    },

    clearable: true,
    multiselect: true,
};
function resetLocation() {
    // Remove any query parameters from the url
    window.history.replaceState({}, document.title, baseUrl);
}

function NodesColumnValidator(cell, value, parameters) {
    if (!value || value.length == 0) {
        return false;
    }
    var nodes = value
    var allNodes = tables.nodes.getData().map(function(row) {
        return row.name;
    });
    var isValid = true;

    nodes.forEach(function(node) {
        if (!allNodes.includes(node)) {
            isValid = false;
        }
    });
    return isValid;
}
function HWPresetColumnValidator(cell, value, parameters) {
    if (!value || value.length == 0) {
        return true;
    }
    var hw_presets = tables.hw_presets.getData().map(function(row) {
        return row.name;
    });
    return hw_presets.includes(value);
}
function HWPresetCellEdited(cell) {
    console.log(cell.getValue())

    if (cell.getValue() === ""){
        cell.setValue(undefined)
    }

    console.log(cell.getValue())
}
function GresValidator(cell, value, parameters) {
    // format: <name>[:<type>][:no_consume]:<number>[K|M|G]

    if (!value) {
        return true;
    }

    var gresRegex = /^[a-zA-Z0-9_\-]+(:[a-zA-Z0-9_\-]+)?(no_consume)?:[0-9]+[KMGTP]?$/;
    var gresList = value.split(",");
    var isValid = true;

    gresList.forEach(function(gres) {
        if (!gresRegex.test(gres)) {
            isValid = false;
        }
    }
    );

    return isValid;
}

// ── HW Preset formatter ────────────────────────────────────────────────────
function HWPresetFormatter(cell, formatterParams, onRendered) {
    var val = cell.getValue();
    if (!val) return "";
    return '<span class="badge badge-hwpreset">' + val + '</span>';
}

// ── GRES Preset helpers ────────────────────────────────────────────────────
const GresPresetEditorParams = {
    valuesLookup: function() {
        return tables.gres_presets.getData().map(function(row) {
            return row.name;
        });
    },
    clearable: true,
    multiselect: true,
};
function GresPresetColumnValidator(cell, value, parameters) {
    // value is null/undefined (no GRES) or an array of preset names
    if (!value || value.length === 0) {
        return true;
    }
    var presetNames = tables.gres_presets.getData().map(function(row) {
        return row.name;
    });
    var isValid = true;
    value.forEach(function(pname) {
        if (!presetNames.includes(pname)) {
            isValid = false;
        }
    });
    return isValid;
}
function GresPresetCellEdited(cell) {
    if (cell.getValue() === "") {
        cell.setValue(undefined);
    }
}
// Formatter: render multi-select gres preset list as comma-separated badges
function GresPresetFormatter(cell, formatterParams, onRendered) {
    var val = cell.getValue();
    if (!val || val.length === 0) return "";
    if (!Array.isArray(val)) val = [val];
    return val.map(function(v) {
        return '<span class="badge badge-gres">' + v + '</span>';
    }).join(" ");
}

function GetManager() {
    var manager
    $.ajax({
	async: false,
        type: "GET",
        url: `${baseUrl}/get_manager`,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            manager = data.config.manager
        },
        error: function(data) {
            console.log(data);
            displayAlert("danger", `Failed to get manager: <br>${data.responseJSON.message}`);
        }
    });
    return manager;
}

function SetManager(OOD) {
    var manager="default";
    if (OOD) {
	manager="OOD";
    }
    $.ajax({
	async: false,
        type: "GET",
        url: `${baseUrl}/set_manager?manager=${manager}`,
        contentType: "application/json; charset=utf-8",
//        success: function(data){
//            manager = data.config.manager
//        },
        error: function(data) {
            console.log(data);
            displayAlert("danger", `Failed to set manager to ${manager}: <br>${data.responseJSON.message}`);
        }
    });
}

function WhoIsManager() {
    var manager
    $.ajax({
	async: false,
        type: "GET",
        url: `${baseUrl}/whois_manager`,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            manager = data.config.manager
        },
        error: function(data) {
            console.log(data);
            displayAlert("danger", `Failed to get manager: <br>${data.responseJSON.message}`);
        }
    });
    return manager;
}

function NodesRowIsEditable(row) {
    return (!row.getData().group_name) || (row.getData().group_name == "");
}
function NodesImport(){
    $.ajax({
        type: "GET",
        url: `${baseUrl}/json/luna/nodes`,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            changes = [];
            lunaNodes = data.config.node;
            tableNodes = Object.assign({}, ...tables.nodes.getData().map(function(row) {
                return {[row.name]: {group: row.group_name}}
            }));

            for (var idx in Object.keys(lunaNodes)) {
                var nodename = Object.keys(lunaNodes)[idx];
                var groupname = lunaNodes[nodename].group;
                
                // Add the nodes that are not in the table
                if (!tableNodes[nodename]) {
                    tables.nodes.addRow({
                        "name": nodename,
                        "group_name": groupname,
                    });
                    changes.push(`Added node <span class="font-weight-bold">${nodename}</span>`);
                }

                // Update the group of nodes that are in the table
                else if (tableNodes[nodename].group != groupname) {
                    var row = tables.nodes.searchRows("name", "=", nodename)[0];
                    var rowData = row.getData();
                    rowData.group_name = groupname;
                    row.update(rowData);
                    changes.push(`Updated group of node <span class="font-weight-bold">${nodename}</span>`);
                }
            }

            // Remove the group for nodes that are not in the luna configuration
            for (var idx in Object.keys(tableNodes)) {
                var nodename = Object.keys(tableNodes)[idx];
                var groupname = tableNodes[nodename].group;
                if (!lunaNodes[nodename]) {
                    var row = tables.nodes.searchRows("name", "=", nodename)[0];
                    var rowData = row.getData();
                    rowData.group_name = "";
                    row.update(rowData);
                    changes.push(`Removed group from node <span class="font-weight-bold">${nodename}</span> (not present in luna)`);
                }
            }

            if (changes.length == 0) {
                displayAlert("success", "No changes were made to the nodes table");
            } else {
                displayAlert("warning", `Imported nodes from luna configuration:<br>${changes.join("<br>")}`);
            }
        },
        error: function(data) {
            console.log(data);
            displayAlert("danger", `Failed to import nodes: <br>${data.responseJSON.message}`);
        }
    });
}

window.onload = function() {
    // Initialize hardware presets table
    tables.hw_presets = new Tabulator("#hw-presets-table", {
        // responsiveLayout:"collapse",
        // height:"311px",
        layout:"fitDataFill",
        placeholder:"No Data Set",
        columns:[
            {formatter:"rowSelection", titleFormatter:"rowSelection", hozAlign:"center", headerSort:false, width:15, cellClick:function(e, cell){
                cell.getRow().toggleSelect();
              }},
            {title:"Name", frozen:true, field:"name", sorter:"string",  editor: "input", validator:[ "unique", "required", nameRegexValidator]},
            {title: "Properties", columns:[
                {title:"# Boards", field:"properties.Boards", sorter:"number",  editor:"input", validator:[ "integer", "min:0", "required"]},
                {title:"# SocketsPerBoard", field:"properties.SocketsPerBoard", sorter:"number",  editor:"input", validator:[ "integer", "min:0", "required"]},
                {title:"# CoresPerSocket", field:"properties.CoresPerSocket", sorter:"number",  editor:"input", validator:[ "integer", "min:0", "required"]},
                {title:"# ThreadsPerCore", field:"properties.ThreadsPerCore", sorter:"number",  editor:"input", validator:[ "integer", "min:0", "required"]},
                {title:"RealMemory (MB)", field:"properties.RealMemory", sorter:"number",  editor:"input", validator:[ "integer", "min:0", "required"]},
                {title:"TmpDisk (MB)", field:"properties.TmpDisk", sorter:"number",  editor:"input", validator:[function(cell, value) {
                    if (value === "" || value === null || value === undefined) return true;
                    return Number.isInteger(Number(value)) && Number(value) >= 0;
                }]},
                // Generic Resources (Gres=) removed — now managed exclusively via the GRES tab.
                // Gres= is auto-derived from GRES preset assignments at save time.
                {title:"CpuBind", field:"properties.CpuBind", sorter:"string",  editor:"list", editorParams:{values:["socket", "ldom", "core", "thread"], clearable: true}},
            ]},
        ],
        reactiveData:true,
        ajaxURL: `${baseUrl}/json/configuration/hw_presets`
    });
    document.getElementById("add-hw-preset-button").addEventListener("click", function(){
        tables.hw_presets.addRow({
            "name": null,
            "properties": {
                "Boards": 1,
                "SocketsPerBoard": 1,
                "CoresPerSocket": 1,
                "ThreadsPerCore": 1,
                "RealMemory": 1,
                "TmpDisk": "",
            }
        });
        tables.hw_presets.validate();
        displayAlert("success", "Added new empty hardware preset");
    });
    document.getElementById("delete-hw-presets-button").addEventListener("click", function(){
        selectedRows = tables.hw_presets.getSelectedRows();
        console.log(selectedRows);
        selectedRows.forEach(function(row) {
            row.delete();
        });
        displayAlert("success", "Deleted selected hardware presets");
        _validateTables();

    })

    // Initialize the GRES presets table
    tables.gres_presets = new Tabulator("#gres-presets-table", {
        layout: "fitDataFill",
        placeholder: "No GRES Presets defined",
        columns: [
            {formatter: "rowSelection", titleFormatter: "rowSelection", hozAlign: "center",
             headerSort: false, width: 15,
             cellClick: function(e, cell){ cell.getRow().toggleSelect(); }},
            {title: "Preset Name", frozen: true, field: "name", sorter: "string",
             editor: "input", validator: ["unique", "required", nameRegexValidator]},
            {title: "GRES Properties", columns: [
                {title: "Name", field: "properties.Name", sorter: "string",
                 editor: "input", validator: ["required", nameRegexValidator],
                 tooltip: "GRES type name, e.g. gpu, fpga, nic"},
                {title: "Type", field: "properties.Type", sorter: "string",
                 editor: "input",
                 tooltip: "Optional subtype, e.g. A100, H100, MIG-3g.20gb"},
                {title: "Count", field: "properties.Count", sorter: "number",
                 editor: "input", validator: ["integer", "min:1", "required"],
                 tooltip: "Number of resources on each node"},
                {title: "File", field: "properties.File", sorter: "string",
                 editor: "input",
                 tooltip: "Device file path, e.g. /dev/nvidia[0-3]",
                 hozAlign: "left", headerHozAlign: "center", width: 160, minWidth: 300},
                {title: "no_consume", field: "properties.no_consume", sorter: "boolean",
                 formatter: function(cell) {
                     var val = cell.getValue();
                     if (val) {
                         return '<span class="toggle-pill toggle-on"><i class="fas fa-check"></i> on</span>';
                     } else {
                         return '<span class="toggle-pill toggle-off"><i class="fas fa-times"></i> off</span>';
                     }
                 },
                 hozAlign: "center", headerHozAlign: "center", width: 160, minWidth: 200,
                 tooltip: "Click to toggle — shared/non-consumable resource",
                 cellClick: function(e, cell) {
                     cell.setValue(!cell.getValue());
                 }},
            ]},
        ],
        reactiveData: true,
        ajaxURL: `${baseUrl}/json/configuration/gres_presets`
    });
    document.getElementById("add-gres-preset-button").addEventListener("click", function(){
        tables.gres_presets.addRow({
            "name": null,
            "properties": {
                "Name": "",
                "Type": "",
                "Count": 1,
                "File": "",
                "no_consume": false,
            }
        });
        tables.gres_presets.validate();
        displayAlert("success", "Added new empty GRES preset");
    });
    document.getElementById("delete-gres-presets-button").addEventListener("click", function(){
        selectedRows = tables.gres_presets.getSelectedRows();
        selectedRows.forEach(function(row) { row.delete(); });
        displayAlert("success", "Deleted selected GRES presets");
        _validateTables();
    });

    // Initialize the nodes table
    tables.nodes = new Tabulator("#nodes-table", {
        // responsiveLayout:"collapse",
        // height:"311px",
        layout:"fitDataFill",
        placeholder:"No Data Set",
        columns:[
            {formatter:"rowSelection", titleFormatter:"rowSelection", hozAlign:"center", headerSort:false, width:15, cellClick:function(e, cell){
                cell.getRow().toggleSelect();
              }},
            {title:"Name", frozen:true, field:"name", sorter:"string",  editor: "input", validator:[ "unique", "required", nameRegexValidator], editable: NodesRowIsEditable},
            {title:"Luna Group", field:"group_name", sorter:"string"},
            {title:"HWPreset", field:"hw_preset_name", sorter:"string", editor:"list", editorParams:HWPresetEditorParams, formatter:HWPresetFormatter, validator:[HWPresetColumnValidator]},
            {title:"GRES Preset(s)", field:"gres_preset_names", sorter:"string", editor:"list",
             editorParams:GresPresetEditorParams, formatter:GresPresetFormatter,
             validator:[GresPresetColumnValidator], cellEdited:GresPresetCellEdited,
             tooltip:"Select one or more GRES presets to assign to this node"},
            {title:"Properties", columns:[
                {title: "State", minWidth:200, field:"properties.State", sorter:"string",  editor:"list", editorParams:{values:["DRAIN", "IDLE"], clearable: true}},
            ]},
        ],
        reactiveData:true,
        ajaxURL: `${baseUrl}/json/configuration/nodes`
    });
    document.getElementById("add-node-button").addEventListener("click", function(){
        tables.nodes.addRow({name:null, group_name:null, properties:{}});
        tables.nodes.validate();
        displayAlert("success", "Added new empty node");
    });
    document.getElementById("import-nodes-button").addEventListener("click", function(){
        NodesImport();
    });
    document.getElementById("delete-nodes-button").addEventListener("click", function(){
        selectedRows = tables.nodes.getSelectedRows();
        console.log(selectedRows);
        selectedRows.forEach(function(row) {
            row.delete();
        });
        displayAlert("success", "Deleted selected nodes");
        _validateTables();

    })

    // Initialize the partitions table
    tables.partitions = new Tabulator("#partitions-table", {
        // responsiveLayout:"collapse",
        // height:"311px",
        layout:"fitDataFill",
        placeholder:"No Data Set",
        columns:[
            {formatter:"rowSelection", titleFormatter:"rowSelection", hozAlign:"center", headerSort:false, width:15, cellClick:function(e, cell){
                cell.getRow().toggleSelect();
              }},
            {title:"Name", frozen:true, field:"name", sorter:"string",  editor: "input", validator:[ "unique", "required", nameRegexValidator]},
            {title:"Nodes", field:"node_names", sorter:"string", editor:"list", width:300, editorParams:NodesEditorParams, validator:[NodesColumnValidator]},
            {title:"HWPreset", field:"hw_preset_name", sorter:"string", editor:"list", editorParams:HWPresetEditorParams, formatter:HWPresetFormatter, validator:[HWPresetColumnValidator]},
            {title:"GRES Preset(s)", field:"gres_preset_names", sorter:"string", editor:"list",
             editorParams:GresPresetEditorParams, formatter:GresPresetFormatter,
             validator:[GresPresetColumnValidator], cellEdited:GresPresetCellEdited,
             tooltip:"Select GRES presets that apply to nodes in this partition"},
            {title:"Properties", columns:[
                {title: "State", field:"properties.State", sorter:"string",  editor:"list", editorParams:{values:["UP", "DOWN", "DRAIN", "INACTIVE"], clearable: true}},
                {title: "Default", field:"properties.Default", sorter:"string",  editor:"list", editorParams:{values:["YES","NO"], clearable: true}},
                {title: "MaxNodes", field:"properties.MaxNodes", sorter:"number",  editor:"input", validator:[ "integer", "min:0"]},
                {title: "Shared", field:"properties.Shared", sorter:"string",  editor:"list", editorParams:{values:["YES","NO"], clearable: true}},
                // {title: "PowerDownOnIdle", field:"properties.PowerDownOnIdle", sorter:"string",  editor:"list", editorParams:{values:["YES","NO"], clearable: true}},
                {title: "MaxTime", field:"properties.MaxTime", sorter:"number",  editor:"input", validator:[ "integer", "min:-1"]},
                {title: "OverTimeLimit", field:"properties.OverTimeLimit", sorter:"number",  editor:"input", validator:[ "integer", "min:0"]},
                {title: "AllowAccounts", field:"properties.AllowAccounts", sorter:"string",  editor:"input", validator:[ nameRegexValidator]},
            ]},
        ],
        reactiveData:true,
        ajaxURL: `${baseUrl}/json/configuration/partitions`
    });
    document.getElementById("add-partition-button").addEventListener("click", function(){
        tables.partitions.addRow({name: null, node_names: [], gres_preset_names: [], properties:{}});
        tables.partitions.validate();
        displayAlert("success", "Added new empty partition");
    });
    document.getElementById("delete-partitions-button").addEventListener("click", function(){
        selectedRows = tables.partitions.getSelectedRows();
        console.log(selectedRows);
        selectedRows.forEach(function(row) {
            row.delete();
        });
        displayAlert("success", "Deleted selected partitions");
        _validateTables();

    })

    // Register handlers for the configuration menu buttons
    document.getElementById("configuration-preview-button").addEventListener("click", function(){
        previewConfiguration();
    });
    document.getElementById("configuration-test-button").addEventListener("click", function(){
        testConfiguration();
    });
    document.getElementById("configuration-save-button").addEventListener("click", function(){
        saveConfiguration();
    });
    document.getElementById("configuration-load-backup-button").addEventListener("click", function(){
        loadConfigurationBackup();
    }); 

    //GetManager();
    manager = WhoIsManager();
    ToggleButtons(manager);
    document.getElementById("functionality-manager-toggle").addEventListener("click", function(){
	SetManager(document.getElementById("functionality-manager-toggle").checked)
        manager = WhoIsManager();
	ToggleButtons(manager);
        //if (manager != 'OOD') {
        //    NodesImport();
        //}
    }); 
    resetLocation();

}

function ToggleButtons(manager) {
        if (manager == 'OOD') {
            document.getElementById("add-node-button").disabled = false;
            document.getElementById("delete-nodes-button").disabled = false;
            document.getElementById("add-partition-button").disabled = false;
            document.getElementById("delete-partitions-button").disabled = false;
            document.getElementById("functionality-manager-toggle").checked = true;
        } else {
            document.getElementById("add-node-button").disabled = true;
            document.getElementById("delete-nodes-button").disabled = true;
            document.getElementById("add-partition-button").disabled = true;
            document.getElementById("delete-partitions-button").disabled = true;
            document.getElementById("functionality-manager-toggle").checked = false;
        }
        // GRES preset buttons are always enabled — same behaviour as HW preset buttons,
        // GRES presets are independent of whether OOD manages nodes/partitions.
        document.getElementById("add-gres-preset-button").disabled = false;
        document.getElementById("delete-gres-presets-button").disabled = false;
}

function _getConfiguration() {
    var hw_presets = tables.hw_presets.getData();
    var gres_presets = tables.gres_presets.getData();
    var nodes = tables.nodes.getData();
    var partitions = tables.partitions.getData();
    var configuration = {
        hw_presets: hw_presets,
        gres_presets: gres_presets,
        nodes: nodes,
        partitions: partitions,
    };
    return configuration;
}

function _validateTables() {
    var validationResults = {};

    Object.keys(tables).forEach(function(table) {
        validationResults[table] = tables[table].validate() == true;
    });

    if (Object.values(validationResults).every(function(result) {return result})) {
        return [0, "All tables are valid"]
    } else {
        invalidTables = Object.keys(validationResults).filter(function(table) {
            return !validationResults[table];
        });
        errorsList = invalidTables.map(function(table) {
            return `<li>${table}</li>`
        }).join("");
        return [1, `The following tables are invalid:<br>${errorsList}`]
    }
}

function previewConfiguration(){
    var configuration = _getConfiguration();

    $.ajax({
        type: "POST",
        url: `${baseUrl}/json/configuration/preview`,
        data: JSON.stringify(configuration),
        contentType: "application/json; charset=utf-8",
        success: function(previewHTML){
            displayModal("Configuration Preview", previewHTML, '')
        },
        error: function(data) {
            console.log(data);
            displayAlert("danger", `Failed to load configuration preview: <br>${data.responseJSON.message}`);
        }
    });
}

function testConfiguration(){
    // First validate the tables
    var [result, message] = _validateTables();
    if (result != 0) {
        displayAlert("danger", `${message}<br>Please fix the errors and try again.`);
        return
    }
    // If the tables are valid, then test the configuration with the slurm linter and display the results
    var configuration = _getConfiguration();
    $.ajax({
        type: "POST",
        url: `${baseUrl}/json/configuration/test`,
        data: JSON.stringify(configuration),
        contentType: "application/json; charset=utf-8",
        success: function(testResults){
            if (testResults.status == "success") {
                // Slurm linter succeeded
                displayAlert("success", "Configuration is valid");
            } else {
                // Slurm linter failed
                errorsList = testResults.errors.map(function(error) {
                    return `<li>${error}</li>`
                }).join("");
                displayAlert("danger", `Configuration is invalid: \n${errorsList}<br>Please fix the errors and try again.`)
            }
        },
        error: function(data) {
            // Error occurred while running slurm linter
            console.log(data);
            displayAlert("danger", `Failed to test configuration: <br>${data.responseJSON.message}`);
        }
    });
}

function _saveConfigurationAction(configuration) {
    $.ajax({
        type: "POST",
        url: `${baseUrl}/json/configuration/save`,
        data: JSON.stringify(configuration),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(data){
            window.location.href = data.redirect;
        },
        error: function(data) {
            console.log(data);
            displayAlert("danger", `Failed to save configuration: <br>${data.responseJSON.message}`);
        }
    });
}
function saveConfiguration(){
    // Block the save when any table has invalid input (e.g. an empty required
    // Preset/GRES Name, a duplicate name or a non-numeric Count) — the same gate
    // testConfiguration() already applies. Without this the backend silently
    // persists an incomplete preset.
    var [result, message] = _validateTables();
    if (result != 0) {
        displayAlert("danger", `${message}<br>Please fix the errors and try again.`);
        return
    }
    var configuration = _getConfiguration();
    displayConfirmationModal(
        "Save Configuration", 
        "Are you sure you want to save the current configuration?", 
        "", 
        () => {_saveConfigurationAction(configuration)}, 
        "Save");
}

function _loadConfigurationBackupAction() {
    var nodesBackupUrl      = `${baseUrl}/json/configuration/nodes?load_from_backup=true`;
    var partitionsBackupUrl = `${baseUrl}/json/configuration/partitions?load_from_backup=true`;
    var hwPresetsBackupUrl  = `${baseUrl}/json/configuration/hw_presets?load_from_backup=true`;
    var gresPresetsBackupUrl = `${baseUrl}/json/configuration/gres_presets?load_from_backup=true`;

    tables.nodes.setData(nodesBackupUrl);
    tables.partitions.setData(partitionsBackupUrl);
    tables.hw_presets.setData(hwPresetsBackupUrl);
    tables.gres_presets.setData(gresPresetsBackupUrl);
}
function loadConfigurationBackup(){
    $.ajax({
        type: "POST",
        url: `${baseUrl}/json/configuration/preview?load_from_backup=true`,
        contentType: "application/json; charset=utf-8",
        success: function(previewHTML){
            displayConfirmationModal(
                "Load Configuration Backup", 
                previewHTML, 
                "Are you sure you want to load the configuration backup?",
                _loadConfigurationBackupAction,
                "Load");
        },
        error: function(data) {
            console.log(data);
            displayAlert("danger", `Failed to load backup configuration preview: <br>${data.responseJSON.message}`);
        }
    });
}
