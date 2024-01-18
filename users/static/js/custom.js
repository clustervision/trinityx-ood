var currentLocation = window.location;
var currentUrl = currentLocation.protocol + "//" + currentLocation.host + currentLocation.pathname;

function renderNewUserButton(cell, formatterParams) {
    return "<button class='btn btn-primary' onclick='handle_new_button(\"users\")'>Add new user</button>"
}
function renderUpdateUserButton(cell, formatterParams) {
    return "<button class='btn btn-primary' onclick='handleUpdateButton(\"users\", \"" + cell.getData().name + "\")'>Edit</button>"
}
function renderDeleteUserButton(cell, formatterParams) {
    return "<button class='btn btn-danger' onclick='handleDeleteButton(\"users\", \"" + cell.getData().name + "\")'>Delete</button>"
}
function renderUserButtons(cell, formatterParams) {
    return renderUpdateUserButton(cell, formatterParams) + " " + renderDeleteUserButton(cell, formatterParams)
}

function renderNewGroupButton(cell, formatterParams) {
    return "<button class='btn btn-primary' onclick='handle_new_button(\"groups\")'>Add new Group</button>"
}
function renderUpdateGroupButton(cell, formatterParams) {
    return "<button class='btn btn-primary' onclick='handleUpdateButton(\"groups\", \"" + cell.getData().name + "\")'>Edit</button>"
}
function renderDeleteGroupButton(cell, formatterParams) {
    return "<button class='btn btn-danger' onclick='handleDeleteButton(\"groups\", \"" + cell.getData().name + "\")'>Delete</button>"
}
function renderGroupButtons(cell, formatterParams) {
    return renderUpdateGroupButton(cell, formatterParams) + " " + renderDeleteGroupButton(cell, formatterParams)
}

function renderModalHeader(target, mode, name) {
    var text;
    if (mode == 'delete') {
        text = "Deleting " + target + " " + name;
    } else if (mode == 'update') {
        text = "Editing " + target + " " + name;
    } else if (mode == 'create') {
        text = "Creating new " + target;
    }
    return text;
}   
function renderModalFooter(target, mode, name) {
    var button;
    if (mode == 'delete') {
        button = '<button type="button" class="btn btn-danger" onclick="handleDeleteSubmitButton(\'' + target + '\', \'' + name + '\')">Delete</button>';
    } else {
        button = '<button type="button" class="btn btn-primary" onclick="handleSubmitButton(\'' + target + '\', \'' + name + '\', \'' + mode + '\')">Submit</button>';
    }
    return button;
}
function renderModalBody(target, mode, name, data) {
    if (mode == 'delete') {
        return 'Are you sure you want to delete ' + name + '?';
    } else {
        return data;
    }
}

function loadModal(target, mode, name) {
    var endpointUrl = (name == null) ? currentUrl + 'modal/' + target + '/' + mode : currentUrl + 'modal/' + target + '/' + mode +  '/' + name ;

    $.ajax({
        url: endpointUrl,
        type: 'GET',
        success: function (data) {
            var modalHeader = renderModalHeader(target, mode, name);
            var modalFooter = renderModalFooter(target, mode, name);
            var modalBody = renderModalBody(target, mode, name, data);
            displayModal(modalHeader, modalBody, modalFooter);

            console.log("Displaying modal for " + target + " " + mode + " " + name);
            console.log("Endpoint URL: " + endpointUrl);
            console.log("Modal Header: " + modalHeader);
            console.log("Modal Footer: " + modalFooter);
        },
        error: function (request) {
            message = JSON.parse(request.responseText).message
            displayAlert('danger', "Error while loading modal: " + message);
        }
    });
}

function handle_new_button(target) {
    loadModal(target, 'create', null);
}
function handleUpdateButton(target, name) {
    loadModal(target, 'update', name);
}
function handleDeleteButton(target, name) {
    loadModal(target, 'delete', name);
}
function handleDeleteSubmitButton(target, name) {
    $.ajax({
        url: currentUrl + 'action/' + target + '/' + name + '/_delete',
        type: 'POST',
        success: function (data) {
            $('#modal').modal('hide');
            tables[target].setData(currentUrl + target);
            displayAlert('success', data.message);
        },
        error: function (request) {
            message = JSON.parse(request.responseText).message
            displayAlert('danger', message);
        }
    });
}
function handleSubmitButton(target, name, mode) {
    var url;
    var formdata = {};

    $("#modal-form input.form-entry").map(function () { formdata[$(this).attr('id')] = $(this).val() })
    if (target == 'groups') {
        formdata['users'] = [];
        $('#modal-form select.form-entry option:selected').each(function () {
            formdata['users'].push($(this).val());
        })
    }

    if (target == 'users') {
        formdata['groups'] = [];
        $('#modal-form select.form-entry option:selected').each(function () {
            formdata['groups'].push($(this).val());
        })
    }

    if (mode == 'update') {
        url = currentUrl + 'action/' + target + '/' + name + '/_update';
    } else if (mode == 'create') {
        url = currentUrl + 'action/' + target + '/_create';
    }

    $.ajax({
        url: url,
        type: 'POST',
        data: JSON.stringify(formdata),
        success: function (data) {
            $('#modal').modal('hide');
            tables[target].setData(currentUrl + target);
            displayAlert('success', data.message);
        },
        error: function (request) {
            message = JSON.parse(request.responseText).message
            displayAlert('danger', message);
        }
    });
    return false;
}




var tables = {}
window.onload = function () {

    tables['users'] = new Tabulator("#users-table", {
        ajaxURL: currentUrl + '/users',
        columns: [
            { formatter:"responsiveCollapse", width:"10%", hozAlign:"center", headerSort:false},
            { title: "Name", field: "name", sorter:"string", width:"40%", responsive: 0},
            { title: "UID", field: "uid", sorter: "string",width:"10%", responsive: 0},
            { title: "Actions", field: "actions", formatter: "html", width: 200, align: "center",width:"40%", responsive: 0, formatter: renderUserButtons },
            { title: "GID", field: "gid", sorter: "string", responsive: 1},
            { title: "Home", field: "homedir", sorter: "string", responsive: 1},
            { title: "Shell", field: "shell", sorter: "string", responsive: 1},
            { title: "Groups", field: "groups", sorter: "string", responsive: 1},
            { title: "Password", field: "password", sorter: "string", responsive: 1},
            { title: "Surname", field: "surname", sorter: "string", responsive: 1},
            { title: "Given Name", field: "givenname", sorter: "string", responsive: 1},
            { title: "Email", field: "email", sorter: "string", responsive: 1},
            { title : "Expire", field: "expire", sorter: "string", responsive: 1},
            { title: "Last Change", field: "last_change", sorter: "string", responsive: 1},
        ],
        layout: "fitData",
        responsiveLayout:"collapse",
        pagination: "local",
        paginationSize: 10,
        paginationSizeSelector: [10, 20, 50, 100],
        initialSort: [
            { column: "name", dir: "asc" },
        ],
        responsiveLayoutCollapseStartOpen:false,
    });

    tables['groups'] = new Tabulator("#groups-table", {
        ajaxURL: currentUrl + '/groups',
        columns: [
            { formatter:"responsiveCollapse", width:"10%", hozAlign:"center", headerSort:false},
            { title: "Name", field: "name", sorter:"string", width:"40%", responsive: 0},
            { title: "GID", field: "gid", sorter: "string",width:"10%", responsive: 0},
            { title: "Actions", field: "actions", formatter: "html", width: 200, align: "center",width:"40%", responsive: 0, formatter: renderGroupButtons },
            { title: "Users", field: "users", sorter: "string", responsive: 1}
        ],
        layout: "fitData",
        responsiveLayout:"collapse",
        pagination: "local",
        paginationSize: 10,
        paginationSizeSelector: [10, 20, 50, 100],
        initialSort: [
            { column: "name", dir: "asc" },
        ],
        responsiveLayoutCollapseStartOpen:false,
    });

    $("#new-user-wrapper").html(renderNewUserButton());
    $("#new-group-wrapper").html(renderNewGroupButton());
}