dragSelect = null;
configuration = {initialized:false, selectedNodes: []};


// 
function _groupExists(groupName) {
    // Check if a group exists
    return $(`#group-${groupName}`).length > 0;
}
function createNodesGroup(groupName, callback=undefined) {
    // Create a new nodes group
    console.log('creating nodes group', groupName);
    // Make an ajax request to /components/nodes_group_card?group_name=<groupName>
    // and place the result in the nodes-col div
    var request = new XMLHttpRequest();
    requestUrl = `/components/nodes_group?group_name=${groupName}`;
    request.open('POST', requestUrl);
    request.setRequestHeader('Content-Type', 'application/json');
    request.onload = function() {
        if (request.status == 200) {
            nodesCardElement = document.querySelector('#nodes-card');

            newElement = $(request.responseText);
            for (let i = 1; i < newElement.length; i++) {
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
function createNode(nodeName, groupNamed) {
    
    // Make an ajax request to /components/node_card?node_name=<nodeName>&group_name=<groupName>
    // and place the result in the nodes-col div
    var request = new XMLHttpRequest();
    requestUrl = `/components/node?node_name=${nodeName}&group_name=${groupName}`;
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

// Nodes - Import from luna
function importLunaNodes(target) {
    // Make an AJAX request to /load/nodes with the contentJSON in the body
    // and display the result in the preview in a modal
    var request = new XMLHttpRequest();
    request.open('GET', `/import/luna/nodes`);
    request.onload = function() {
        if (request.status == 200) {
            // display the result in the preview in a modal
            contentJSON = request.responseText;
            content = JSON.parse(contentJSON);

            _updateNodes(content.config.node);
        } else {
            errorString = _getRequestError(`Error loading ${target}`, request);
            displayAlert('danger', errorString);
        }
    }
    request.send();
}
function _updateNodes(newNodes) {
    // Update the unassigned nodes from the configuration
    oldNodes = parseConfiguration()['nodes'];
    console.log(oldNodes);
    console.log(newNodes);


    // Get the list of nodes to add
    for (const nodeName in newNodes) {
        if (Object.keys(oldNodes).indexOf(nodeName) < 0 ) {
            groupName = newNodes[nodeName]['group'];
            if (!_groupExists(groupName)) {
                createNodesGroup(groupName, () => _updateNodes(newNodes));
                return;
            } 
            createNode(nodeName, groupName);
        }
    }

    // Get the list of nodes to remove
    for (const nodeName in oldNodes) {
        if (Object.keys(newNodes).indexOf(nodeName) < 0 ) {
            $(`#node-${nodeName}`).addClass('deleted');
        }
    }

}


// Partitions
function createPartition(partitionName) {
    // Create a new partition
    console.log('creating partition', partitionName);
    emptyPartition = {properties: {}, nodes: {}};
    // Make an ajax request to /components/partition_card?partition_name=<partitionName>
    // and place the result in the partitions-col div
    var request = new XMLHttpRequest();
    requestUrl = `/components/partition_card?partition_name=${partitionName}`;
    request.open('POST', requestUrl);
    request.setRequestHeader('Content-Type', 'application/json');
    request.onload = function() {
        if (request.status == 200) {
            partitionsColElement = document.querySelector('#partitions-col');
            // partitionsColElement.innerHTML += request.responseText;
            // create a new element from the responseText using jquery
            newElement = $(request.responseText);
            partitionsColElement.appendChild(newElement[0]);
            initializePartitionCard(partitionName);
            updateDragSelect();
        } else {
            errorString =  _getRequestError(`Error creating partition`, request);
            displayAlert('danger', errorString);
        }
    }
    request.send(JSON.stringify(emptyPartition));

    
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
    btn = document.querySelector(`#partition-${partitionName} .button-show-settings`);
    btn.classList.toggle('btn-outline-primary');
    btn.classList.toggle('btn-primary');
}
function togglePartitionAdvancedSettings(partitionName) {
    console.log('toggling partition advanced settings', partitionName);
    settings = document.querySelector(`#settings-advanced-${partitionName}`);
    settings.classList.toggle('show');
    // toggle the btn-outline-primary and btn-primary classes as well
    btn = document.querySelector(`#partition-${partitionName} .button-show-settings-advanced`);
    btn.classList.toggle('btn-outline-primary');
    btn.classList.toggle('btn-primary');
}
function hidePartitionSettings(partitionName) {
    console.log('hiding all settings', partitionName);
    settings = document.querySelector(`#settings-${partitionName}`);
    settings.classList.remove('show');
    settings = document.querySelector(`#settings-advanced-${partitionName}`);
    settings.classList.remove('show');
    // toggle the btn-outline-primary and btn-primary classes as well
    btn = document.querySelector(`#partition-${partitionName} .button-show-settings`);
    btn.classList.add('btn-outline-primary');
    btn.classList.remove('btn-primary');
    btn = document.querySelector(`#partition-${partitionName} .button-show-settings-advanced`);
    btn.classList.add('btn-outline-primary');
    btn.classList.remove('btn-primary');
}


// Load Components Cards from the server
function renderNodesCard() {
    // Make an AJAX request to /components/slurm_nodes_card
    // and place the result in the nodes-col div
    var request = new XMLHttpRequest();
    request.open('POST', '/components/nodes_card');
    request.onload = function() {
        if (request.status == 200) {
            nodesColElement = document.querySelector('#nodes-col');
            nodesColElement.innerHTML += request.responseText;
            initializeNodesCard();
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
    request.open('POST', '/components/partitions_cards');
    request.setRequestHeader('Content-Type', 'application/json');
    request.onload = function() {
        if (request.status == 200) {
            partitionsColElement = document.querySelector('#partitions-col');
            partitionsColElement.innerHTML += request.responseText;
            initializePartitionCards();
            updateDragSelect();
        } else {
            errorString = _getRequestError(`Error loading partitions`, request);
            displayAlert('danger', errorString);
        }
    }
    request.send();
}
function renderConfigurationPreview() {
    var data = {nodes: parseNodes(), partitions: parsePartitions()};
    console.log(data);
    // Fetch and display the preview of the configuration
    var request = new XMLHttpRequest();
    request.open('POST', '/components/configuration_preview');
    request.setRequestHeader('Content-Type', 'application/json');
    request.onload = function() {
        if (request.status == 200) {
            // display the result in the preview in a modal
            modalBody = request.responseText;
            displayModal('Configuration Preview', modalBody, '');
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
function saveConfiguration() {
    var data = parseConfiguration();

    // Make an AJAX request to /save with the contentJSON in the body
    // and reload the page
    var request = new XMLHttpRequest();
    request.open('POST', '/save');
    request.setRequestHeader('Content-Type', 'application/json');
    request.onload = function() {
        if (request.status == 200) {
            // reload the page
            location.reload();
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
    request.open('POST', '/restore');
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
        request.open('POST', `/download/${target}`);
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


// Iniitialize handlers
function initializeMenu() {
    // Initialize the menu
    $('#configuration-restore-button').click(handleRestoreConfigurationButton);
    $('#configuration-preview-button').click(handlePreviewConfigurationButton);
    $('#configuration-download-button').click(handleDownloadConfigurationButton);
    $('#configuration-save-button').click(handleSaveConfigurationButton);
}
function initializePartitionCards() {
    // Initialize the new partition button
    document.querySelector('#new-partition-button').addEventListener('click', (e) => {
        handleCreatePartitionForm(e);
    })
    // Initialize all the partition cards
    partitionCards = document.querySelectorAll('.partition-card');
    for (let i = 0; i < partitionCards.length; i++) {
        initializePartitionCard(partitionCards[i].id.split('-')[1]);
    }
}
function initializePartitionCard(partitionName) {
    
    partittionElement = document.querySelector(`#partition-${partitionName}`);
    // Initialize listeners
    partittionElement.querySelector('.button-close').addEventListener('click', handleDeletePartitionButton)
    partittionElement.querySelector('.button-show-settings').addEventListener('click', handleShowSettingsButton)
    partittionElement.querySelector('.button-show-settings-advanced').addEventListener('click', handleShowSettingsAdvancedButton)
    partittionElement.querySelector('.button-hide-settings').addEventListener('click', handleHideSettingsButton)

}
function initializeNodesCard() {
}
function initializeDragSelect() {
    dragSelect = new DragSelect({
        draggability: true,
    });

    dragSelect.subscribe('DS:end', ({ items, event, isDragging, isDraggingKeyboard, dropTarget }) => {
        if (isDragging){
            if (dropTarget) {
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

    // Initialize handlers
    initializeDragSelect();
    initializeMenu();
    

    // Render missing components
    renderNodesCard();
    renderPartitionsCards();

    updateDragSelect();
};
