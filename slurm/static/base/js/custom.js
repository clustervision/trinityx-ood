function clearAlerts() {
    document.getElementById('alerts').innerHTML = '';
}
function displayAlert(type, message) {
    clearAlerts();
    alert_types = ['success', 'info', 'warning', 'danger'];
    if (alert_types.indexOf(type) == -1) {
        console.log(`Alert type ${type} is not valid`);
    }
    else {
        alert_div = document.createElement('div');
        alert_div.innerHTML = 
            `<div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
                </button>
            </div>`;
        document.getElementById('alerts').appendChild(alert_div);
    }
    
}


function showModal() {
    $('#modal').modal('show');
}

function hideModal() {
    $('#modal').modal('hide');
}

function displayModal(title, body, footer) {
    document.querySelector('#modal .modal-title').innerHTML = title;
    document.querySelector('#modal .modal-body').innerHTML = body;
    document.querySelector('#modal .modal-footer').innerHTML = footer;
    showModal();
}
function confirmationButton(text, type) {
    return `<button type="button" id="modal-confirm-button" class="btn btn-${type}">${text}</button>`;
}

function displayConfirmationModal(title, body, footer, callback, button_text, button_type) {
    if (title == undefined) {
        title = 'Confirmation required';
    }
    if (body == undefined) {
        body = '';
    }
    if (footer == undefined) {
        footer = '';
    }
    if (button_text == undefined) {
        button_text = 'Confirm';
    }
    if (button_type == undefined) {
        button_type = 'primary';
    }

    document.querySelector('#modal .modal-title').innerHTML = title;
    document.querySelector('#modal .modal-body').innerHTML = body;
    document.querySelector('#modal .modal-footer').innerHTML = footer + confirmationButton(button_text, button_type);
    
    // wrap the callback to hide the modal
    confirmationCallback = function() {
        callback();
        hideModal();
    }

    document.getElementById('modal-confirm-button').onclick = confirmationCallback;
    showModal();
}
