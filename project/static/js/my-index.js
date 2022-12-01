
function delete_appt_popup() {
    let confirmDelete = confirm('Are you sure you want to delete?');
    if (confirmDelete) {
        alert("Your appointment was successfully deleted");
        return true;
    } else {
        return false;
    }
}

function new_carrier_popup() {
    alert("New carrier was successfully added");
}

function update_appt_popup() {
    alert("Your appointment was successfully updated");
}

function unauth_popup() {
    alert("You do not have access to this function. " +
        "Please contact your system administrator if " +
        "you require access.");
    return false;
}

function toggle(source) {
    var checkboxes = document.querySelectorAll('input[type="checkbox"].filter');
    for (var i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i] != source)
            checkboxes[i].checked = source.checked;
    }
}