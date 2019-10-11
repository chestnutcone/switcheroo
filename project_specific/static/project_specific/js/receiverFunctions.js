function fetchReceiveRequestResult() {
    // for applicant
    $.ajax({
        type: "GET",
        url: "/main/swap/receive",
        dataType: 'json',
        success: function(response) {
            $("#swapReceiveRequest-container").empty()
            displayReceiverRequestResult(response)
        },
        contentType:'application/json'
    })
}

function displayReceiverRequestResult(response) {
    // for receiver
    let receive_request_container = document.getElementById('ReceiveRequest-container')
    $('#ReceiveRequest-container').empty()
    for (num in response) {
        let processing = response[num]
        let shift_item = document.createElement('ul')
        let applicant = document.createElement('li')
        let receiver = document.createElement('li')

        let rejectButton = document.createElement('button')
        let acceptButton = document.createElement('button')

        rejectButton.innerText = 'Reject'
        acceptButton.innerText = 'Accept'

        rejectButton.setAttribute('onclick', 'rejectRequest(this)')
        acceptButton.setAttribute('onclick', 'acceptRequest(this)')

        shift_item.setAttribute('data-created_time', processing['created'])
        shift_item.setAttribute('data-applicant_shift_start', processing['applicant_shift_start'])
        shift_item.setAttribute('data-applicant_shift_end', processing['applicant_shift_end'])
        shift_item.setAttribute('data-applicant_employee_id', processing['applicant_employee_id'])
        shift_item.setAttribute('data-receiver_employee_id', processing['receiver_employee_id'])
        shift_item.setAttribute('data-receiver_shift_start', processing['receiver_shift_start'])
        shift_item.setAttribute('data-receiver_shift_end', processing['receiver_shift_end'])

        if (processing['receiver_shift_start']) {
            applicant.innerText = `Current Schedule ${processing['receiver_shift_start']} to ${processing['receiver_shift_end']}`
        } else {
            applicant.innerText = `Would you be willing to accept the following shift:`
        }
        receiver.innerText = `Proposed Schedule ${processing['applicant_shift_start']} to ${processing['applicant_shift_end']}`

        shift_item.appendChild(acceptButton)
        shift_item.appendChild(rejectButton)
        shift_item.appendChild(applicant)
        shift_item.appendChild(receiver)
        
        receive_request_container.appendChild(shift_item)
    }
}

function acceptRequest(param) {
    // for receiver
    let parent_element = param.parentNode
    let created_time = parent_element.dataset.created_time
    let applicant_employee_id = parent_element.dataset.applicant_employee_id

    let data = {'created':created_time, 'applicant_employee_id':applicant_employee_id}

    let send_data = JSON.stringify({"action": "accept", "data":data})
    let csrftoken = getCookie('csrftoken')
    $.ajax({
        type: "POST",
        url: "/main/swap/receive",
        data: send_data,
        headers: {
            'X-CSRFToken': csrftoken
        },
        dataType: 'json',
        success: function(result) {
            if (result['status']) {
                alert('Request accepted!')
                fetchReceiveRequestResult()
            } else {
                alert(result['error_detail'])
            }
        },
        contentType:'application/json'
    })

}
function rejectRequest(param) {
    // for receiver
    let parent_element = param.parentNode
    let created_time = parent_element.dataset.created_time
    let requester_shift_start = parent_element.dataset.applicant_shift_start

    let data = {'created':created_time, 'requester_shift_start':requester_shift_start}

    let send_data = JSON.stringify({"action": "reject", "data":data})
    let csrftoken = getCookie('csrftoken')
    $.ajax({
        type: "POST",
        url: "/main/swap/receive",
        data: send_data,
        headers: {
            'X-CSRFToken': csrftoken
        },
        dataType: 'json',
        success: function(result) {
            if (result['status']) {
                alert('Request rejected')
                fetchReceiveRequestResult()
            } else {
                alert(result['error_detail'])
            }
        },
        contentType:'application/json'
    })
}

fetchReceiveRequestResult()