let old_accept_swap = JSON.parse(document.getElementById('old_accept_swap').textContent)

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
});

document.getElementById('accept_swap').checked = old_accept_swap

function getCookie (name) {
    let cookieValue = null
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';')
        for (let i=0; i<cookies.length; i++) {
            let cookie = cookies[i].trim()
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                break
            }
        }
    }
    return cookieValue
}

function updateSettings() {
    let accept_swap = document.getElementById('accept_swap').checked
    let csrftoken = getCookie('csrftoken')

    send_data = {'accept_swap': accept_swap}
    send_data = JSON.stringify(send_data)
    $.ajax({
        type: "POST",
        url: "/main/settings/",
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

