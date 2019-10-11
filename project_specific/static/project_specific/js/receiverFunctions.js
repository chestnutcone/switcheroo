
function displayReceiverRequestResult(response) {
    // for receiver
    let swap_request_container = document.getElementById('swapReceiveRequest-container')
    $('#swapReceiveRequest-container').empty()
    for (num in response) {
        let processing = response[num]
        let shift_item = document.createElement('ul')
        let applicant = document.createElement('li')
        let receiver = document.createElement('li')
        let status = ""
        let cancelButton = document.createElement('button')
        let acceptButton = document.createElement('button')
        cancelButton.innerText = 'Reject'
        acceptButton.innerText = 'Accept'
        cancelButton.setAttribute('onclick', 'rejectRequest(this)')
        acceptButton.setAttribute('onclick', 'acceptRequest(this)')
        shift_item.setAttribute('data-created_time', processing['created'])
        shift_item.setAttribute('data-applicant_shift_start', processing['applicant_shift_start'])
        shift_item.setAttribute('data-applicant_shift_end', processing['applicant_shift_end'])
        shift_item.setAttribute('data-receiver_shift_start', processing['receiver_shift_start'])
        shift_item.setAttribute('data-receiver_shift_end', processing['receiver_shift_end'])
        shift_item.setAttribute('data-acceptor_employee_id', processing['receiver_employee_id'])

        applicant.innerText = `Current Schedule ${processing['receiver_shift_start']} to ${processing['receiver_shift_end']}`
        receiver.innerText = `Proposed Schedule ${processing['applicant_shift_start']} to ${processing['applicant_shift_end']}`

        
        shift_item.appendChild(applicant)
        shift_item.appendChild(receiver)
        
        swap_request_container.appendChild(shift_item)
    }
}

function acceptRequest(param) {
    // for receiver
}
function rejectRequest(param) {
    // for receiver
}
