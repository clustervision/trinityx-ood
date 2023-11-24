function handleNodesDeleteButton(event) {
    console.log('handle node delete button');
    event.preventDefault();
    console.log(dragSelect.getSelection());
}
function handleNodesImportButton(event) {
    console.log('handle luna import button');   
    importLunaNodes();
}
function handleSaveConfigurationButton(event) {
    console.log('handle save configuration ');
    displayConfirmationModal("Saving Configuration", "Do you want to save the current configuration to file system ?", '', saveConfiguration)
}
function handleRestoreConfigurationButton(event) {
    console.log('handle preview restore button');
    renderConfigurationPreview('backup_configuration');
}
function handleTestConfigurationButton(event) {
    console.log('handle test configuration button');
    testConfiguration();
}

function handlePreviewConfigurationButton(event) {
    console.log('handle preview button');
    renderConfigurationPreview('configuration');
}
function handleDownloadConfigurationButton(event) {
    console.log('handle download button');
    downloadConfiguration();
}

function handleCreatePartitionForm(event) {
    console.log('handle create partition');


    partitionName = document.getElementById('new-partition-name').value;
    // check that partition name is not empty
    if (partitionName.length == 0) {
        displayAlert('danger', 'Partition name cannot be empty');
        return;
    }
    // check that partition name is alphanumeric
    allowedChars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_';
    for (let i = 0; i < partitionName.length; i++) {
        if (allowedChars.indexOf(partitionName[i]) == -1) {
            displayAlert('danger', 'Partition name can only contain alphanumeric characters, dashes and underscores');
            return;
        }
    }
    // check that partition name is not already taken
    existing_partitions = document.querySelectorAll('.partition-card');
    for (let i = 0; i < existing_partitions.length; i++) {
        if (existing_partitions[i].id == `partition-${partitionName}`) {
            displayAlert('danger', `Partition name '${partitionName}' already exists`);
            return;
        }
    }
    createPartition(partitionName);
}

function handleShowSettingsButton(event) {
    console.log('handle show settings');
    event.preventDefault();
    target = event.target;
    while (!target.classList.contains('partition-card')) {
        target = target.parentElement;
    }
    partitionName = target.id.split('-').slice(1).join('-');
    togglePartitionSettings(partitionName);   
}
function handleShowSettingsAdvancedButton(event) {
    console.log('handle show settings advanced');
    event.preventDefault();
    target = event.target;
    while (!target.classList.contains('partition-card')) {
        target = target.parentElement;
    }
    partitionName = target.id.split('-').slice(1).join('-');
    togglePartitionAdvancedSettings(partitionName);   
}
function handleHideSettingsButton(event) {
    console.log('handle hide settings');
    event.preventDefault();
    target = event.target;
    while (!target.classList.contains('partition-card')) {
        target = target.parentElement;
    }
    partitionName = target.id.split('-').slice(1).join('-');
    hidePartitionSettings(partitionName);
}
function handleDeletePartitionButton(event) {
    console.log('handle delete partition');
    event.preventDefault();
    target = event.target;
    while (!target.classList.contains('partition-card')) {
        target = target.parentElement;
    }
    partitionName = target.id.split('-').slice(1).join('-');
    deletePartition(partitionName);
}



