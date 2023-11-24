dragSelect = null;
configuration = {initialized:false, selectedNodes: []};



function _buildUrl(url){
    var currentUrl = window.location.href;
    var newUrl = currentUrl + url;
    return newUrl;
}


// Node Groups
function _nodesGoupExists(groupName) {
    // Check if a group exists
    return $(`#group-${groupName}`).length > 0;
}
function createNodesGroup(groupName, callback=undefined) {
    // Create a new nodes group
    console.log('creating nodes group', groupName);
    // Make an ajax request to /components/nodes_group_card?group_name=<groupName>
    // and place the result in the nodes-col div
    var request = new XMLHttpRequest();
    requestUrl = _buildUrl(`/components/nodes_group?group_name=${groupName}`);
    request.open('POST', requestUrl);
    request.setRequestHeader('Content-Type', 'application/json');
    request.onload = function() {
        if (request.status == 200) {
            nodesCardElement = document.querySelector('#nodes-card');

            newElement = $(request.responseText);
            for (let i = 0; i < newElement.length; i++) {
                nodesCardElement.appendChild(newElement[i]);
            }

            updateDragSelect();
        } else {
            errorString =  _getRequestError(`Error creating nodes group`, request);
            displayAlert('danger', errorString);
        }
        if (callback) {
            callback();
        }
    }
    request.send();
}


// Nodes
function getNodeNodeName(item) {
        return item.getAttribute('node-name');
}
function getNodeGroupName(item) {
    return $(item).attr('group-name');
}
function setNodeGroupName(item, groupName) {
    $(item).attr('group-name', groupName);
}
function moveNode(item, dropzone_id, itemName=undefined) {
    if (itemName == undefined) {
        itemName = getNodeNodeName(item);
    }
    
    // Get the item name
    itemName = getNodeNodeName(item);
    console.log(`moving ${itemName} to ${dropzone_id}`)
    // Get the dropzone
    dropzone = document.querySelector(`#${dropzone_id}`)
    // get all the items in the dropzone 
    items = dropzone.querySelectorAll('.item');
    // get the index in which to insert the item (based on the content of span.text)
    index = 0;
    for (let i = 0; i < items.length; i++) {
        otherNodeName = getNodeNodeName(items[i]);
        if (itemName > otherNodeName) {
            index++;
        } else {
            break;
        }
    }
    // Append the item to the dropzone
    dropzone.insertBefore(item, items[index]);
    // Reset the item position
    item.style.transform = '';
}
function moveNodes(items, dropzone_id) {
    console.log(`moving  ${items.length} items to ${dropzone_id}`)
    items.forEach(item => {
        moveNode(item, dropzone_id);
    })
}
function resetNode(item) {
    // Read the value of the group-name attribute
    group = item.getAttribute('group-name');
    // Compute the id of the dropzone 
    dropzone_id = `dropzone-group-${group}`;
    // Move the item to the dropzone
    moveNode(item, dropzone_id);
}
function resetNodes(items) {
    console.log(`resetting ${items.length} items`)
    items.forEach(item => {
       resetNode(item);
    })
}
function createNode(nodeName, groupName) {
    
    // Make an ajax request to /components/node_card?node_name=<nodeName>&group_name=<groupName>
    // and place the result in the nodes-col div
    var request = new XMLHttpRequest();
    requestUrl = _buildUrl(`/components/node?node_name=${nodeName}&group_name=${groupName}`);
    request.open('POST', requestUrl);
    request.setRequestHeader('Content-Type', 'application/json');
    request.onload = function() {
        if (request.status == 200) {
            nodesColElement = document.querySelector('#nodes-col');
            // nodesColElement.innerHTML += request.responseText;
            // create a new element from the responseText using jquery
            newElement = $(request.responseText);
            newElement.addClass('new')
            moveNode(newElement[0], `dropzone-group-${groupName}`, nodeName);
            updateDragSelect();
        } else {
            errorString =  _getRequestError(`Error creating node`, request);
            displayAlert('danger', errorString);
        }

    }
    request.send();
    
}
function deleteNodes(nodeNames) {
    // Delete the selected nodes
    console.log('deleting nodes', nodeNames);
    for (let i = 0; i < nodeNames.length; i++) {
        nodeName = nodeNames[i];
        node_element = document.querySelector(`#node-${nodeName}`);
        node_element.remove();    
    }
    updateDragSelect();
}
function getNodePartition(item) {
    // Get the partition of the node
    element = item
    while(!element.classList.contains('dropzone')) {
        element = element.parentElement;
    }
    if (element.id.startsWith('dropzone-partition-')) {
        return element.id.split('-').slice(2).join('-');
    } 
    return undefined;
}

// Nodes - Import from luna
function importLunaNodes(target) {
    // Make an AJAX request to /load/nodes with the contentJSON in the body
    // and display the result in the preview in a modal
    var button = $(`#nodes-import-button`);
    button.attr('disabled', true);
    button.find('.text').addClass('d-none');
    button.find('.spinner').removeClass('d-none');

    var request = new XMLHttpRequest();
    requestUrl = _buildUrl(`/import/luna/nodes`);
    request.open('GET', requestUrl);
    request.onload = function() {
        if (request.status == 200) {
            // display the result in the preview in a modal
            contentJSON = request.responseText;
            content = JSON.parse(contentJSON);
            
            oldNodes = parseConfiguration()['nodes'];
            
            _updateNodes(oldNodes, content.config.node);
        } else {
            errorString = _getRequestError(`Error loading ${target}`, request);
            displayAlert('danger', errorString);
        }
        button.attr('disabled', false);
        button.find('.text').removeClass('d-none');
        button.find('.spinner').addClass('d-none');
    }
    request.send();


}
function _updateNodes(oldNodes, newNodes) {
    // Update the unassigned nodes from the configuration
    

    changes = [];
    var groupName;
    var nodeName;

    // Get the list of nodes to add
    for (const nodeName in newNodes) {
        if (Object.keys(oldNodes).indexOf(nodeName) < 0 ) {
            groupName = newNodes[nodeName]['group'];
            if (!_nodesGoupExists(groupName)) {
                createNodesGroup(groupName, () => _updateNodes(oldNodes, newNodes));
                return;
            } 
            createNode(nodeName, groupName);

            // Register change
            changes.push(`<li>Added node <span class="font-weight-bold">${nodeName}</span> to group <span class="font-weight-bold">${groupName}</span></li>`);
        }
    }

    // Get the list of nodes to remove
    for (const nodeName in oldNodes) {
        if (Object.keys(newNodes).indexOf(nodeName) < 0 ) {
            if (!$(`#node-${nodeName}`).hasClass('deleted')) {

                $(`#node-${nodeName}`).addClass('deleted');
                // Register change
                changes.push(`<li>Deleted node <span class="font-weight-bold">${nodeName}</span> ( Not present in Luna anymore )</li>`);
            }
        }
    }

    // Get the list of nodes to change
    for (const nodeName in newNodes) {
        if (Object.keys(oldNodes).indexOf(nodeName) >= 0 ) {
            if (oldNodes[nodeName]['group'] != newNodes[nodeName]['group']) {
                // Move the node to the new group
                groupName = newNodes[nodeName]['group'];
                if (!getNodePartition($(`#node-${nodeName}`)[0])) {
                    setNodeGroupName($(`#node-${nodeName}`)[0], groupName);
                    resetNode($(`#node-${nodeName}`)[0]);
                }
                $(`#node-${nodeName}`).addClass('changed');
                // Register change
                changes.push(`<li>Move node <span class="font-weight-bold">${nodeName}</span> to group <span class="font-weight-bold">${groupName}</span></li>`);
            }
        }
    }

    if (changes.length > 0) {
        // Display changes
        changesList = `<ul>${changes.join('')}</ul>`;
        displayAlert('warning', `Successfully synched nodes from Luna<br>The following changes were made:<br>${changesList}`);
    } else {
        displayAlert('success', `Successfully synched nodes from Luna<br>No changes were made`);
    }
   
}


// Partitions
function createPartition(partitionName) {
    // Create a new partition
    console.log('creating partition', partitionName);
    configuration = parseConfiguration();
    // Make an ajax request to /components/partition_card?partition_name=<partitionName>
    // and place the result in the partitions-col div
    var request = new XMLHttpRequest();
    requestUrl = _buildUrl(`/components/partition_card?partition_name=${partitionName}`);
    request.open('POST', requestUrl);
    request.setRequestHeader('Content-Type', 'application/json');
    request.onload = function() {
        if (request.status == 200) {
            partitionsColElement = document.querySelector('#partitions-col');
            // partitionsColElement.innerHTML += request.responseText;
            // create a new element from the responseText using jquery
            newElement = $(request.responseText);
            partitionsColElement.appendChild(newElement[0]);
            updateDragSelect();
        } else {
            errorString =  _getRequestError(`Error creating partition`, request);
            displayAlert('danger', errorString);
        }
    }
    request.send(JSON.stringify(configuration));

    
}
function deletePartition(partitionName) {
    // Delete a partition
    console.log('deleting partition', partitionName);
    partition_element = document.querySelector(`#partition-${partitionName}`);
    items = $(`#dropzone-partition-${partitionName} .item`).get();
    resetNodes(items);

    partition_element.remove();
    updateDragSelect();
}


// Partitions - Settings Buttons
function togglePartitionSettings(partitionName) {
    console.log('toggling partition settings', partitionName);
    settings = document.querySelector(`#settings-${partitionName}`);
    settings.classList.toggle('show');
    // toggle the btn-outline-primary and btn-primary classes as well
    var button = $(`#partition-${partitionName} .button-show-settings`);
    var text = button.find('.text');
    button.toggleClass('btn-outline-primary');
    button.toggleClass('btn-primary');
    text.toggleClass('d-none');

    
}
function togglePartitionAdvancedSettings(partitionName) {
    console.log('toggling partition advanced settings', partitionName);
    settings = document.querySelector(`#settings-advanced-${partitionName}`);
    settings.classList.toggle('show');
    // toggle the btn-outline-primary and btn-primary classes as well
    var button = $(`#partition-${partitionName} .button-show-settings-advanced`);
    var text = button.find('.text');
    button.toggleClass('btn-outline-primary');
    button.toggleClass('btn-primary');
    text.toggleClass('d-none');
}


// Load Components Cards from the server
function renderNodesCard() {
    // Make an AJAX request to /components/slurm_nodes_card
    // and place the result in the nodes-col div
    var request = new XMLHttpRequest();
    requestUrl = _buildUrl(`/components/nodes_card`);
    request.open('POST', requestUrl);
    request.onload = function() {
        if (request.status == 200) {
            nodesColElement = document.querySelector('#nodes-col');
            nodesColElement.innerHTML += request.responseText;
            updateDragSelect();
        } else {
            errorString = _getRequestError(`Error loading nodes`, request);
            displayAlert('danger', errorString);
        }
        
    }
    request.send();
}
function renderPartitionsCards() {
    // Make an AJAX request to /components/slurm_partitions_card
    // and place the result in the partitions-col div

    var request = new XMLHttpRequest();
    requestUrl = _buildUrl(`/components/partitions_cards`);
    request.open('POST', requestUrl);
    request.setRequestHeader('Content-Type', 'application/json');
    request.onload = function() {
        if (request.status == 200) {
            partitionsColElement = document.querySelector('#partitions-col');
            partitionsColElement.innerHTML += request.responseText;
            updateDragSelect();
        } else {
            errorString = _getRequestError(`Error loading partitions`, request);
            displayAlert('danger', errorString);
        }
    }
    request.send();
}
function renderConfigurationPreview(target) {
    var data = {nodes: parseNodes(), partitions: parsePartitions()};
    console.log(data);
    // Fetch and display the preview of the configuration
    var request = new XMLHttpRequest();
    requestUrl = _buildUrl(`/components/${target}_preview`);
    request.open('POST', requestUrl);
    request.setRequestHeader('Content-Type', 'application/json');
    request.onload = function() {
        if (request.status == 200) {
            // display the result in the preview in a modal
            modalBody = request.responseText;
            if (target == 'configuration') {
                displayConfirmationModal('Configuration Preview', modalBody, 'Do you want to save this configuration?   ', saveConfiguration, 'Save', 'primary');
            } else if (target == 'backup_configuration') {
                displayConfirmationModal('Backup Configuration Preview', modalBody,  'Do you want to restore this configuration?   ', restoreConfiguration, 'Restore', 'warning');
            }
        } else {
            errorString = _getRequestError(`Error displaying configuration preview`, request);
            displayAlert('danger', errorString);
        }
    }
    request.send(JSON.stringify(data));
}


// Parse and Save Configuration
function parseNodes() {
    var nodes = {};
    var dropzones = document.querySelectorAll('.dropzone');

    for (let i = 0; i < dropzones.length; i++) {
        dropzone = dropzones[i];

        items = dropzone.querySelectorAll('.item');

        for (let j = 0; j < items.length; j++) {
            nodeName = getNodeNodeName(items[j]);
            groupName = getNodeGroupName(items[j]);
            
            nodes[nodeName] = {group: groupName};
        }
    }
    return nodes;
}
function parsePartitions() {
    partitionsElements = document.querySelectorAll('.partition-card');
    partitions = {};
    for (let i = 0; i < partitionsElements.length; i++) {
        
        partition = {properties: {}, nodes: []};

        // parse all the input fields
        inputs = partitionsElements[i].querySelectorAll('input, select');
        for (let j = 0; j < inputs.length; j++) {
            input = inputs[j];
            fieldName = input.id.split('-')[1];
            
            
            if (input.type == 'checkbox') {
                partition.properties[fieldName] = input.checked;
            } else {
                partition.properties[fieldName] = input.value;
            }
        }

        // parse the nodes
        dropzone = partitionsElements[i].querySelector('.dropzone');
        items = dropzone.querySelectorAll('.item') || [];
        for (let j = 0; j < items.length; j++) {
            partition.nodes.push(getNodeNodeName(items[j]));
        }

        partitionName = partitionsElements[i].id.split('-').slice(1).join('-');
        partitions[partitionName] = partition;
    }
    return partitions;
}
function parseConfiguration(){
    return {nodes: parseNodes(), partitions: parsePartitions()};
}
function testConfiguration() {
    var data = parseConfiguration();

    // Set the #configuration-test-button to loading by disabling it and adding the spinner
    document.querySelector('#configuration-test-button').disabled = true;
    document.querySelector('#configuration-test-button .text').classList.add('d-none');
    document.querySelector('#configuration-test-button .spinner').classList.remove('d-none');



    // Make an AJAX request to /test with the contentJSON in the body
    // and display the result in the preview in a modal
    var request = new XMLHttpRequest();
    var response;
    var errorList;
    var errorText;
    requestUrl = _buildUrl(`/test`);
    request.open('POST', requestUrl);
    request.setRequestHeader('Content-Type', 'application/json');
    request.onload = function() {
        if (request.status == 200) {
            // display the result in the preview in a modal
            response = JSON.parse(request.responseText);
            console.log(response)
            if (response.message == 'success'){
                displayAlert('success', 'Configuration test: ok <br>(Slurmctld started)');
            } else if (response.message == 'warning') {
                errorList = response.errors.map(error => `<li>${error}</li>`);
                errorText = `<ul>${errorList.join('')}</ul>`;
                displayAlert('warning', 'Configuration test: warning <br>(Slurmctld started but errors found in the log) <br>' + errorText);
            }
            else {
                errorList = response.errors.map(error => `<li>${error}</li>`);
                errorText = `<ul>${errorList.join('')}</ul>`;
                displayAlert('danger', 'Configuration test: failed<br> (Slurmctld failed on startup)<br>' + errorText);
            }
            // modalBody = request.responseText;

            // displayConfirmationModal('Configuration Test', modalBody, 'Do you want to save this configuration?   ', saveConfiguration, 'Save', 'primary');

        } else {
            errorText = _getRequestError(`Error testing configuration`, request);
            displayAlert('danger', errorText);
        }
        // restore the state of the button
        document.querySelector('#configuration-test-button').disabled = false;
        document.querySelector('#configuration-test-button .text').classList.remove('d-none');
        document.querySelector('#configuration-test-button .spinner').classList.add('d-none');
    }
    request.send(JSON.stringify(data));
}
function saveConfiguration() {
    var data = parseConfiguration();

    // Make an AJAX request to /save with the contentJSON in the body
    // and reload the page
    var request = new XMLHttpRequest();
    requestUrl = _buildUrl(`/save`);
    request.open('POST', requestUrl);
    request.setRequestHeader('Content-Type', 'application/json');
    request.onload = function() {
        if (request.status == 200) {
            // set location to url in the response
            document.location = request.responseText;
        } else {
            errorString = _getRequestError(`Error saving configuration`, request);
            displayAlert('danger', errorString);
        }
    }
    request.send(JSON.stringify(data));
}
function restoreConfiguration() {
    // Make an AJAX request to /restore and reload the page
    var request = new XMLHttpRequest();
    requestUrl = _buildUrl(`/restore`);
    request.open('POST', requestUrl);
    request.onload = function() {
        if (request.status == 200) {
            // reload the page
            location.reload();
        } else {
            errorString = _getRequestError(`Error restoring configuration`, request);
            displayAlert('danger', errorString);
        }
    }
    request.send();
}
function _downloadConfiguration(target) {
    {
        var request = new XMLHttpRequest();
        requestUrl = _buildUrl(`/download/${target}`);
        request.open('POST', requestUrl);
        request.setRequestHeader('Content-Type', 'application/json');
        request.responseType = 'blob';
        request.onload = function() {
            if (request.status == 200) {
                // download the file
                var blob = new Blob([request.response], {type: 'text/plain'});
                var link = document.createElement('a');
                link.href = window.URL.createObjectURL(blob);
                link.download = `${target}.conf`;
                link.click();
            } else {
                errorString = _getRequestError(`Error downloading configuration`, request);
                displayAlert('danger', errorString);
            }
        }

        var data = parseConfiguration()
        request.send(JSON.stringify(data));
    }
}
function downloadConfiguration() {
    // Make an AJAX request to /download and download the file
    targets = ['nodes', 'partitions'];
    for (let i = 0; i < targets.length; i++) {
        target = targets[i];
        _downloadConfiguration(target);
    }
}




function initializeDragSelect() {
    dragSelect = new DragSelect({
        draggability: true,
    });

    dragSelect.subscribe('DS:end', ({ items, event, isDragging, isDraggingKeyboard, dropTarget }) => {
        if (isDragging){
            if (dropTarget && dropTarget.id.startsWith('dropzone-partition-')) {
                moveNodes(dragSelect.getSelection(), dropTarget.id);
            } else {
                resetNodes(dragSelect.getSelection());
            }
        }
    })
}
function updateDragSelect() {
    // Register the dropzones
    dropzone_ids = $(`.dropzone`).map(function() {return this.id;}).get();
    ds_dropzones = dropzone_ids.map(id => ({ element: document.querySelector(`#${id}`), id: id }));
    dragSelect.setSettings({ dropZones: ds_dropzones });

    // Register the items
    items = document.querySelectorAll('.item');
    dragSelect.setSettings({ selectables: items });

}


window.onload = function(e){
    // Remove any variables from the url
    history.replaceState({}, document.title, document.location.href.split('/').slice(0, -1).join('/'));

    // Initialize handlers
    initializeDragSelect();

    // Render missing components
    // renderNodesCard();
    // renderPartitionsCards();

    // Update DragSelect
    updateDragSelect();
};
