/*
 * This code is part of the TrinityX software suite
 * Copyright (C) 2023  ClusterVision Solutions b.v.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>
 * 
 * 
 * Control Application Main JavaScript File.
 * Arthur       = 'Sumit Sharma'
 * Copyright    = 'Copyright 2025, TrinityX [OOD]'
 * License      = 'GPL'
 * Version      = '2.0'
 * Maintainer   = 'Sumit Sharma'
 * Email        = 'sumit.sharma@clustervision.com'
 * Status       = 'Production'
 * 
 */ 


function getBaseUrl(fullUrl) {
    const url = new URL(fullUrl);
    const pathSegments = url.pathname.split('/');
    const punIndex = pathSegments.findIndex(segment => segment === 'pun');
    if (punIndex !== -1) {
        const basePath = pathSegments.slice(0, punIndex + 3).join('/');
        return `${url.origin}${basePath}`;
    }
    return url.origin;
}

const url = getBaseUrl(window.location.href);


function color_status(message=null){
    if (message){
        if ((message.includes('ON')) || (message.includes('OK'))){
            message = `<strong style="color:green;">${message}</strong>`;
        } else if (message.includes('OFF')){
            message = `<strong style="color:orange;">${message}</strong>`;
        } else {
            message = `<strong style="color:red;">${message}</strong>`;
        }
    } else {
        message = `<strong style="color:red;">${message}</strong>`;
    }
    
    return message
}


function create_row(count, node, impi, sel, chassis){
    row = `
    <tr>
        <td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top;"><input type="checkbox" name="node" value="${node}" id="${count}" /></td>
        <td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top;">${node}</td>
        <td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top;">${color_status(impi)}</td>
        <td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top;">${color_status(sel)}</td>
        <td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top;">${color_status(chassis)}</td>
        <td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top;">
            <a id="actions" href="${url}/power/status/${node}" data-bs-toggle="tooltip" data-bs-offset="0,4" data-bs-placement="top" data-bs-html="true" data-bs-original-title="<i class=\'bx bxs-arrow-from-left bx-xs\' >
                </i> <span>Current Status of ${node}</span>"><i class="bx bx-md bx-stats" style="color: #03c3ec;"></i>
            </a>
            <a id="actions" href="${url}/power/on/${node}" data-bs-toggle="tooltip" data-bs-offset="0,4" data-bs-placement="top" data-bs-html="true" data-bs-original-title="<i class=\'bx bxs-arrow-from-left bx-xs\' >
                </i> <span>Power ON ${node}</span>"><i class="bx bx-md bx-power-off" style="color: #71dd37;"></i>
            </a>&nbsp;
            <a id="actions" href="${url}/power/off/${node}" data-bs-toggle="tooltip" data-bs-offset="0,4" data-bs-placement="top" data-bs-html="true" data-bs-original-title="<i class=\'bx bxs-arrow-from-left bx-xs\' >
                </i> <span>Power OFF ${node}</span>"><i class="bx bx-md bx-power-off bx-flip-vertical" style="color: #ff3e1d;"></i>
            </a>
            <a id="actions" href="${url}/power/reset/${node}" data-bs-toggle="tooltip" data-bs-offset="0,4" data-bs-placement="top" data-bs-html="true" data-bs-original-title="<i class=\'bx bxs-arrow-from-left bx-xs\' >
                </i> <span>Power Reset ${node}</span>"><i class="bx bx-md bx-repost bx-flip-vertical" style="color: #e83e8c;"></i>
            </a>
        </td>
        <td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top;">
            <a id="actions" href="${url}/sel/list/${node}" data-bs-toggle="tooltip" data-bs-offset="0,4" data-bs-placement="top" data-bs-html="true" data-bs-original-title="<i class=\'bx bxs-arrow-from-left bx-xs\' >
                </i> <span>Sel List ${node}</span>"><i class="bx bx-md bx-list-ol" style="color: #20c997;"></i>
            </a>
            <a id="actions" href="${url}/sel/clear/${node}" data-bs-toggle="tooltip" data-bs-offset="0,4" data-bs-placement="top" data-bs-html="true" data-bs-original-title="<i class=\'bx bxs-arrow-from-left bx-xs\' >
                </i> <span>Sel Clear ${node}</span>"><i class="bx bx-md bx-message-alt-minus" style="color: #fd7e14;"></i>
            </a>
        </td>
        <td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top;">
            <a id="actions" href="${url}/chassis/identify/${node}" data-bs-toggle="tooltip" data-bs-offset="0,4" data-bs-placement="top" data-bs-html="true" data-bs-original-title="<i class=\'bx bxs-arrow-from-left bx-xs\' >
                </i> <span>Chassis Identify ${node}</span>"><i class="bx bx-md bx-shield-alt-2" style="color: #696cff;"></i>
            </a>
            <a id="actions" href="${url}/chassis/noidentify/${node}" data-bs-toggle="tooltip" data-bs-offset="0,4" data-bs-placement="top" data-bs-html="true" data-bs-original-title="<i class=\'bx bxs-arrow-from-left bx-xs\'>
                </i> <span>Chassis No Identify ${node}</span>"><i class="bx bx-md bx-error-alt" style="color: #007bff;"></i>
            </a>
        </td>
        <td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top;">
            <a id="actions" href="${url}/redfish/upload/${node}" data-bs-toggle="tooltip" data-bs-offset="0,4" data-bs-placement="top" data-bs-html="true" data-bs-original-title="<i class=\'bx bxs-arrow-from-left bx-xs\' >
                </i> <span>Redfish Upload ${node}</span>"><i class="bx bx-md bx-upload" style="color: #ffab00;"></i>
            </a>
            <a id="actions" href="${url}/redfish/setting/${node}" data-bs-toggle="tooltip" data-bs-offset="0,4" data-bs-placement="top" data-bs-html="true" data-bs-original-title="<i class=\'bx bxs-arrow-from-left bx-xs\' >
                </i> <span>Redfish Setting ${node}</span>"><i class="bx bx-md bx-cog" style="color: black;"></i>
            </a>
        </td>
    </tr>`;
    return row
}

var row_data = {};
var real_data = {};


function control_table(data, count){
    var row = '';
    
    for (var i=0; i<data.length; i++) {
        
        if (data[i].control.hasOwnProperty("power")){
            for (const [key, value] of Object.entries(data[i].control.failed)) { if (!row_data.hasOwnProperty(key)) { row_data[key] = {} } row_data[key]['ipmi'] = value; }
            for (const [key, value] of Object.entries(data[i].control.power.on)) { if (!row_data.hasOwnProperty(key)) { row_data[key] = {} }  row_data[key]['ipmi'] = 'ON'; }
            for (const [key, value] of Object.entries(data[i].control.power.off)) { if (!row_data.hasOwnProperty(key)) { row_data[key] = {} }  row_data[key]['ipmi'] = 'OFF'; }
            for (const [key, value] of Object.entries(data[i].control.power.ok)) { if (!row_data.hasOwnProperty(key)) { row_data[key] = {} }  row_data[key]['ipmi'] = value; }
        }

        if (data[i].control.hasOwnProperty("sel")) {
            for (const [key, value] of Object.entries(data[i].control.failed)) { if (!row_data.hasOwnProperty(key)) { row_data[key] = {} }  row_data[key]['sel'] = value; }
            for (const [key, value] of Object.entries(data[i].control.sel.on)) { if (!row_data.hasOwnProperty(key)) { row_data[key] = {} }  row_data[key]['sel'] = 'ON'; }
            for (const [key, value] of Object.entries(data[i].control.sel.off)) { if (!row_data.hasOwnProperty(key)) { row_data[key] = {} }  row_data[key]['sel'] = 'OFF'; }
            for (const [key, value] of Object.entries(data[i].control.sel.ok)) { if (!row_data.hasOwnProperty(key)) { row_data[key] = {} }  row_data[key]['sel'] = 'OK'; }
        }

        if (data[i].control.hasOwnProperty("chassis")) {
            for (const [key, value] of Object.entries(data[i].control.failed)) { if (!row_data.hasOwnProperty(key)) { row_data[key] = {} }  row_data[key]['chassis'] = value; }
            for (const [key, value] of Object.entries(data[i].control.chassis.on)) { if (!row_data.hasOwnProperty(key)) { row_data[key] = {} }  row_data[key]['chassis'] = 'ON'; }
            for (const [key, value] of Object.entries(data[i].control.chassis.off)) { if (!row_data.hasOwnProperty(key)) { row_data[key] = {} }  row_data[key]['chassis'] = 'OFF'; }
            for (const [key, value] of Object.entries(data[i].control.chassis.ok)) { if (!row_data.hasOwnProperty(key)) { row_data[key] = {} }  row_data[key]['chassis'] = 'OK'; }
        }
    }
    
    for (const [key, value] of Object.entries(row_data)) {
        if(value.ipmi && value.sel && value.chassis){
            var ipmi = [];
            var sel = [];
            var chassis = [];
            var n = 20;
            if (value.ipmi.length >= 20){
                for(i = 0, len = value.ipmi.length; i < len; i += n) {
                    ipmi.push(value.ipmi.substr(i, n));
                }
                ipmi = ipmi.join("<br>");
            } else { ipmi = value.ipmi; }

            if (value.sel.length >= 20){
                for(i = 0, len = value.sel.length; i < len; i += n) {
                    sel.push(value.sel.substr(i, n));
                }
                sel = sel.join("<br>");
            } else { sel = value.sel; }

            if (value.chassis.length >= 20){
                for(i = 0, len = value.chassis.length; i < len; i += n) {
                    chassis.push(value.chassis.substr(i, n));
                }
                chassis = chassis.join("<br>");
            } else { chassis = value.chassis; }
            row += create_row(count, key, ipmi, sel, chassis);
            count++
        }
    }

    return row
}


function control_action(system, action){
    $("#alert_messages").empty();
    var node_list = [];
    var form_data = $('form').serialize();
    if  (form_data.includes('&')){
        const myArray = form_data.split("&");
        for (var i=0; i<myArray.length; i++) { node_list.push(myArray[i].replace(/node=/g,'')); }
        var spinner_message = `${system } ${action} performed on Nodes: [${node_list}]. Refreshing the table.`;
        $("#alert_messages").append(`<div class="alert alert-success" role="alert">${spinner_message}</div>`);
    } else {
        var error_message = "Kindly select more then one Node to use this option. To perform operation on only one node kindly use buttons next to the node."
        $("#alert_messages").append(`<div class="alert alert-danger" role="alert">${error_message}</div>`);
    }
    
    if (node_list.length > 0){
        var payload = {"hostlist": node_list};
        payload = JSON.stringify(payload);
        $.ajax({
            url: url+'/perform/'+system+'/'+action,
            type: 'POST',
            data: JSON.stringify(payload),
            dataType: 'json',
            contentType: 'application/json; charset=UTF-8',
            success: function(response_data) {
                var intervalId;
                intervalId = setInterval(function(){
                    $.getJSON(url+'/check_request/'+response_data.control.request_id, function(data){
                        if (data.message){
                            $('[data-bs-toggle="tooltip"]').tooltip();
                            $('#power_table').html();
                            clearInterval(intervalId);
                        }
                    });
                }, 1000); 
                power_table();
                $("#alert_messages").empty();
            }
        });
        
    } else { console.log("No Nodes are available"); }
}


function select_all(){
    if ($('#selectAll').is(':checked')){
        $('#selectAll').closest('table').find('td input:checkbox').prop('checked', true);
    } else{
        $('#selectAll').closest('table').find('td input:checkbox').prop('checked', false);
    }
}


function power_table(){
    $('#spinner').show();
    var payload = $('#payload').text();
    if (payload){
        var response;
        $.ajax({
            url: url+'/get_status',
            type: 'POST',
            data: JSON.stringify(payload),
            dataType: 'json',
            async: false,
            contentType: 'application/json; charset=UTF-8',
            success: function(response_data) { response = response_data; }
        });
        for (var i=0; i<response.length; i++) {
            if (response[i].control.power){ power_request_id = response[i].request_id; }
            if (response[i].control.sel){ sel_request_id = response[i].request_id; }
            if (response[i].control.chassis){ chassis_request_id = response[i].request_id; }
        }

        var row = '';
        var table = `
        <table frame="box" rules="cols" id="datatable" class="table table-bordered table-hover table-striped text-nowrap">
            <thead>
                <tr>
                    <th style="padding-left: 1em; padding-right: 1em; text-align: center"><input type="checkbox" id="selectAll" onClick="select_all();" /></th>
                    <th style="padding-left: 1em; padding-right: 1em; text-align: center">Node Name</th>
                    <th style="padding-left: 1em; padding-right: 1em; text-align: center">IPMI State</th>
                    <th style="padding-left: 1em; padding-right: 1em; text-align: center">Sel</th>
                    <th style="padding-left: 1em; padding-right: 1em; text-align: center">Chassis</th>
                    <th style="padding-left: 1em; padding-right: 1em; text-align: center">Power Actions</th>
                    <th style="padding-left: 1em; padding-right: 1em; text-align: center">Sel Actions</th>
                    <th style="padding-left: 1em; padding-right: 1em; text-align: center">Chassis Actions</th>
                    <th style="padding-left: 1em; padding-right: 1em; text-align: center">Redfish Actions</th>
                </tr>
            </thead>
        <tbody>`;

        $('#power_table').html(table);
        var text = $('#power_table').text();
        row += table;
        var new_rows = control_table(response, 1);
        row += new_rows;
        $('#power_table').html(row);
        var intervalId;
        var stop_me = {"power": false, "sel": false, "chassis": false};
        intervalId = setInterval(function(){
            $.getJSON(url+'/check_status/'+power_request_id+'/'+sel_request_id+'/'+chassis_request_id, function(data){
                if (data[0].message){ stop_me.power = true; }
                if (data[1].message){ stop_me.sel = true; }
                if (data[2].message){ stop_me.chassis = true; }
                if ((stop_me.power === true) && (stop_me.sel === true) && (stop_me.chassis === true)){
                    $('[data-bs-toggle="tooltip"]').tooltip();
                    clearInterval(intervalId);
                    $('#spinner').hide();
                    $('#datatable').dataTable({
                        "columnDefs": [
                            { "orderable": false, "targets": 0 } // Disable sorting on first column (checkboxes)
                        ],
                        "order": [[1, "asc"]] // Default sorting by column index 1 (Node Name) in ascending order
                    });
                } else {
                    text = $('#power_table').html();
                    row = text;
                    var count = (row.match(/<tr>/g) || []).length;
                    var new_data = [];
                    for (var i=0; i<data.length; i++) {
                        if (data[i].hasOwnProperty("control")) { new_data.push(data[i]); }
                    }
                    var new_rows = control_table(new_data, count);
                    row += new_rows;
                    row = row.replace('</tbody></table>','')
                    var arow = table;
                    arow += new_rows;
                    $('#power_table').html(arow);
                } 
            });
        }, 1000);
    } else {
        $('#spinner').hide();
        $('#power_table').html('<div class="alert alert-warning" role="alert">WARNING :: No Nodes are available at this moment.</div>');
    }
    
}


power_table();


