
function createAcceptRejectButton (parentElement, acceptText='Request', rejectText='Reject') {
    let acceptButton = document.createElement("button")
    let rejectButton = document.createElement("button")
    acceptButton.innerText = acceptText
    rejectButton.innerText = rejectText
    acceptButton.setAttribute('onclick', 'applyRequest(this)')
    rejectButton.setAttribute('onclick', 'rejectSwap(this)')
    parentElement.appendChild(acceptButton)
    parentElement.appendChild(rejectButton)
    return parentElement
}

function createCancelButton (parentElement) {
    let cancelButton = document.createElement("button")
    cancelButton.innerText = 'Cancel'
    cancelButton.setAttribute('onclick', 'cancelSwapShift(this)')
    parentElement.appendChild(cancelButton)
    return parentElement
}

function cancelSwapShift (param) {
    let parent_element = param.parentNode
    let swap_shift_start = parent_element.dataset.shift_start
    if (swap_shift_start) {

        let send_data = JSON.stringify({"action": "cancel", "data":swap_shift_start})
        let csrftoken = getCookie('csrftoken')
        $.ajax({
            type: "POST",
            url: "/main/swap/",
            data: send_data,
            headers: {
                'X-CSRFToken': csrftoken
            },
            dataType: 'json',
            success: function(result) {
                if (result['status']) {
                    alert('shift swap cancelled')
                    fetchSwapResult()
                } else {
                    alert(result['error'])
                }
            },
            contentType:'application/json'
        })
    }
}

function applyRequest (param) {
    let parent_element = param.parentNode
    let requester_shift_start = parent_element.parentNode.firstChild.dataset.shift_start
    let acceptor_employee_id = parent_element.dataset.receiver_employee_id
    let dataType = parent_element.dataset.datatype
    if (dataType == 'shift') {
        let acceptor_shift_start = parent_element.dataset.receiver_shift_start
        var data = {'acceptor_shift_start': acceptor_shift_start,
        'acceptor_employee_id': acceptor_employee_id,
        'requester_shift_start': requester_shift_start,}
    } else if (dataType == 'people') {
        var data = {'requester_shift_start':requester_shift_start,
                    'acceptor_employee_id':acceptor_employee_id,}

    }
    data['data_type'] = dataType
    let send_data = JSON.stringify({"action": "request", "data":data})
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
                    alert('Request sent')
                    fetchSwapResult()
                    fetchRequestResult()

                } else if (result['acceptor_error']) {
                    alert(result['acceptor_error'])
                } else if (result['requester_error']) {
                    alert(result['requester_error'])
                } else if (result['already_exist']) {
                    fetchSwapResult()
                    fetchRequestResult()
                    alert(`Request already exist for this shift`)
                }
            },
            contentType:'application/json'
    })
    

}

function rejectSwap (param) {
    // for applicant, rejecting swap result (clearing it for now)
    let parent_element = param.parentNode
    parent_element.remove()
}
