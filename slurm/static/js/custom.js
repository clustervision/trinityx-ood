const tables = {};
const nameRegexValidator = "regex:^[a-zA-Z0-9_]+$";
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
const NodesColumnValidator = function(cell, value, parameters) {
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
const HWPresetColumnValidator = function(cell, value, parameters) {
    if (!value || value.length == 0) {
        return true;
    }
    var hw_presets = tables.hw_presets.getData().map(function(row) {
        return row.name;
    });
    return hw_presets.includes(value);
}
const NodesRowIsEditable = function(row) {
    return (!row.getData().group_name) || (row.getData().group_name == "");
}

window.onload = function() {
    // Initialize hardware presets table
    tables.hw_presets = new Tabulator("#hw-presets-table", {
        responsiveLayout:"collapse",
        // height:"311px",
        layout:"fitColumns",
        placeholder:"No Data Set",
        columns:[
            {formatter:"rowSelection", titleFormatter:"rowSelection", hozAlign:"center", headerSort:false, width:15, cellClick:function(e, cell){
                cell.getRow().toggleSelect();
              }},
            {title:"Name", field:"name", sorter:"string", width:200,  editor: "input", validator:[ "unique", "required", nameRegexValidator]},
            {title: "Properties", columns:[
                {title:"# Boards", field:"properties.Boards", sorter:"number",  editor:"input", validator:[ "integer", "min:0", "required"]},
                {title:"# Sockets", field:"properties.Sockets", sorter:"number",  editor:"input", validator:[ "integer", "min:0", "required"]},
                {title:"# CoresPerSocket", field:"properties.CoresPerSocket", sorter:"number",  editor:"input", validator:[ "integer", "min:0", "required"]},
                {title:"# ThreadsPerCore", field:"properties.ThreadsPerCore", sorter:"number",  editor:"input", validator:[ "integer", "min:0", "required"]},
                {title:"RealMemory (MB)", field:"properties.RealMemory", sorter:"number",  editor:"input", validator:[ "integer", "min:0", "required"]},
                {title:"TmpDisk (MB)", field:"properties.TmpDisk", sorter:"number",  editor:"input", validator:[ "integer", "min:0", "required"]},
            ]},
        ],
        reactiveData:true,
        ajaxURL: "/json/configuration/hw_presets"
    });
    document.getElementById("add-hw-preset-button").addEventListener("click", function(){
        tables.hw_presets.addRow({
            "name": undefined,
            "properties": {
                "Boards": 1,
                "Sockets": 1,
                "CoresPerSocket": 1,
                "ThreadsPerCore": 1,
                "RealMemory": 1,
                "TmpDisk": 1,
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

    // Initialize the nodes table
    tables.nodes = new Tabulator("#nodes-table", {
        responsiveLayout:"collapse",
        // height:"311px",
        layout:"fitColumns",
        placeholder:"No Data Set",
        columns:[
            {formatter:"rowSelection", titleFormatter:"rowSelection", hozAlign:"center", headerSort:false, width:15, cellClick:function(e, cell){
                cell.getRow().toggleSelect();
              }},
            {title:"Name", field:"name", sorter:"string", width:200,  editor: "input", validator:[ "unique", "required", nameRegexValidator], editable: NodesRowIsEditable},
            {title:"Group", field:"group_name", sorter:"string"},
            {title:"HWPreset", field:"hw_preset_name", sorter:"string", editor:"list", editorParams:HWPresetEditorParams, validator:[HWPresetColumnValidator]},
            {title:"Properties", columns:[
                {title: "State", field:"properties.State", sorter:"string",  editor:"list", editorParams:{values:["DRAIN", "UNKNOWN", "IDLE"], clearable: true}},
            ]},
        ],
        reactiveData:true,
        ajaxURL: "/json/configuration/nodes"
    });
    document.getElementById("add-node-button").addEventListener("click", function(){
        tables.nodes.addRow({});
        tables.nodes.validate();
        displayAlert("success", "Added new empty node");
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
        responsiveLayout:"collapse",
        // height:"311px",
        layout:"fitColumns",
        placeholder:"No Data Set",
        columns:[
            {formatter:"rowSelection", titleFormatter:"rowSelection", hozAlign:"center", headerSort:false, width:15, cellClick:function(e, cell){
                cell.getRow().toggleSelect();
              }},
            {title:"Name", field:"name", sorter:"string", width:200,  editor: "input", validator:[ "unique", "required", nameRegexValidator]},
            {title:"Nodes", field:"node_names", sorter:"string", editor:"list", editorParams:NodesEditorParams, validator:[NodesColumnValidator]},
            {title:"HWPreset", field:"hw_preset_name", sorter:"string", editor:"list", editorParams:HWPresetEditorParams, validator:[HWPresetColumnValidator]},
            {title:"Properties", columns:[
                {title: "Exclusive", field:"properties.ExclusiveUser", sorter:"string",  editor:"list", editorParams:{values:["YES","NO"], clearable: true}},
                {title: "PowerDownOnIdle", field:"properties.PowerDownOnIdle", sorter:"string",  editor:"list", editorParams:{values:["YES","NO"], clearable: true}},
                {title: "MaxTime", field:"properties.MaxTime", sorter:"number",  editor:"input", validator:[ "integer", "min:0"]},
                {title: "OverTimeLimit", field:"properties.OverTimeLimit", sorter:"number",  editor:"input", validator:[ "integer", "min:0"]},
            ]},
        ],
        reactiveData:true,
        ajaxURL: "/json/configuration/partitions"
    });
    document.getElementById("add-partition-button").addEventListener("click", function(){
        tables.partitions.addRow({});
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

}


function _getConfiguration() {
    var hw_presets = tables.hw_presets.getData();
    var nodes = tables.nodes.getData();
    var partitions = tables.partitions.getData();
    var configuration = {
        hw_presets: hw_presets,
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
        url: "/json/configuration/preview",
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
        url: "/json/configuration/test",
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
        url: "/json/configuration/save",
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
    var configuration = _getConfiguration();
    displayConfirmationModal(
        "Save Configuration", 
        "Are you sure you want to save the current configuration?", 
        "", 
        () => {_saveConfigurationAction(configuration)}, 
        "Save");
}


function _loadConfigurationBackupAction() {
    var targetUrl = "/?load_from_backup=true&message=Configuration%20backup%20loaded%20successfully";
    window.location.href = targetUrl;
}
function loadConfigurationBackup(){
    $.ajax({
        type: "POST",
        url: "/json/configuration/preview?load_from_backup=true",
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