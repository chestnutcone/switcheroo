function cancelRequest(param) {
    // for applicant
    let data_element = param.parentNode.parentNode.parentNode
    let created_time = data_element.dataset.created_time
    let requester_shift_start = data_element.dataset.applicant_shift_start
    let data = {'created':created_time, 'requester_shift_start':requester_shift_start}

    let send_data = JSON.stringify({"action": "cancel", "data":data})
    let csrftoken = getCookie('csrftoken')
    $.ajax({
        type: "POST",
        url: "/main/swap/request",
        data: send_data,
        headers: {
            'X-CSRFToken': csrftoken
        },
        dataType: 'json',
        success: function(result) {
            if (result['status']) {
                alert('Request Removed')
                fetchSwapResult()
                fetchRequestResult()
            } else {
                alert(result['error_detail'])
            }
        },
        contentType:'application/json'
    })
}
