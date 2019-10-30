let old_approve_all_swap = JSON.parse(document.getElementById('old_approve_all_swap').textContent)

document.getElementById('approve_all_swap').checked = old_approve_all_swap
$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
});

function updateSettings() {
    let approve_all_swap = document.getElementById('approve_all_swap').checked
    let csrftoken = getCookie('csrftoken')

    send_data = {'approve_all_swap':approve_all_swap}
    send_data = JSON.stringify(send_data)
    $.ajax({
        type: "POST",
        url: "/main/manager/settings",
        data: send_data,
        headers: {
            'X-CSRFToken': csrftoken
        },
        dataType: 'json',
        success: function(result) {
            location.reload()
        },
        contentType:'application/json'
    })
}