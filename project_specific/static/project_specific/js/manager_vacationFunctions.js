
function createApproveRejectButton(parentElement, accept_class, reject_class, acceptText='Accept', rejectText='Reject') {
    let acceptButton = document.createElement("button")
    let rejectButton = document.createElement("button")
    let swap_button_group = document.createElement('div')

    acceptButton.innerText = acceptText
    rejectButton.innerText = rejectText
    acceptButton.setAttribute('onclick', accept_class)
    rejectButton.setAttribute('onclick', reject_class)
    acceptButton.setAttribute('class', 'btn btn-success btn-md')
    rejectButton.setAttribute('class', 'btn btn-danger btn-md')
    swap_button_group.setAttribute('class', 'pull-right')
    swap_button_group.appendChild(acceptButton)
    swap_button_group.appendChild(rejectButton)
    parentElement.appendChild(swap_button_group)
    return parentElement
}

function acceptVacationRequest(param) {
    let data_node = param.parentNode.parentNode.parentNode
    let send_data = JSON.stringify({"action": "accept", 
    "data":{'requester_employee_id': data_node.dataset.requester_employee_id,
    'request_date':data_node.dataset.request_date}})
        let csrftoken = getCookie('csrftoken')
        $.ajax({
            type: "POST",
            url: "/main/manager/vacation",
            data: send_data,
            headers: {
                'X-CSRFToken': csrftoken
            },
            dataType: 'json',
            success: function(result) {
                console.log(result)
                if (result['error_detail']) {
                    alert(`Error has occured ${result['error_detail']}`)
                }
                fetchManagerVacation()
            },
            contentType:'application/json'
        })
}

function rejectVacationRequest(param) {
    let data_node = param.parentNode.parentNode.parentNode
    let send_data = JSON.stringify({"action": "reject", 
    "data":{'requester_employee_id': data_node.dataset.requester_employee_id,
    'request_date':data_node.dataset.request_date}})
        let csrftoken = getCookie('csrftoken')
        $.ajax({
            type: "POST",
            url: "/main/manager/vacation",
            data: send_data,
            headers: {
                'X-CSRFToken': csrftoken
            },
            dataType: 'json',
            success: function(result) {
                if (result['error_detail']) {
                    alert(`Error has occured ${result['error_detail']}`)
                }
                fetchManagerVacation()
            },
            contentType:'application/json'
        })
}