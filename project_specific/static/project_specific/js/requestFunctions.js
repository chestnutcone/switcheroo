
function cancelRequest(param) {
    // for applicant
    let parent_element = param.parentNode
    let created_time = parent_element.dataset.created_time
    let requester_shift_start = parent_element.dataset.applicant_shift_start
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
                alert('Request cancelled')
                fetchSwapResult()
                fetchRequestResult()
            } else {
                alert(result['error_detail'])
            }
        },
        contentType:'application/json'
    })
}

function finalizeSwap(param) {
    // for applicant
    let parent_element = param.parentNode
    let created_time = parent_element.dataset.created_time
    let requester_shift_start = parent_element.dataset.applicant_shift_start
    let acceptor_shift_start = parent_element.dataset.acceptor_shift_start
    let acceptor_employee_id = parent_element.dataset.acceptor_employee_id


    let data = {'created':created_time, 'requester_shift_start':requester_shift_start,
'acceptor_shift_start':acceptor_shift_start,'acceptor_employee_id':acceptor_employee_id}

    let send_data = JSON.stringify({"action": "finalize", "data":data})
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
                alert('Shift Swapped!')
                fetchSwapResult()
                fetchRequestResult()
            } else {
                alert(result['error_detail'])
            }
        },
        contentType:'application/json'
    })
}