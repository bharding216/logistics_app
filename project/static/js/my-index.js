//let user know that appointment was added to db
function create_appt_popup() {
    alert("Your appointment was successfully added");
}

function delete_appt_popup() {
    alert("Your appointment was successfully deleted");
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
}

function toggle(source) {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    for (var i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i] != source)
            checkboxes[i].checked = source.checked;
    }
}