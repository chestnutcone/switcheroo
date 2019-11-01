
function fetchManagerVacation() {
    $.ajax({
        type: "GET",
        url: "/main/manager/vacation",
        dataType: 'json',
        success: function(response) {
            displayManagerVacation(response)
        },
        contentType:'application/json'
    })
}

function displayManagerVacation (response) {
    $("#incoming-vacation-requests").empty()
    let vacationRequest = document.getElementById('incoming-vacation-requests')
    for (r in response) {
        let request = response[r]
        let container = document.createElement('ul')
        let requester_name = document.createElement('h3')
        requester_name.innerText = request['requester_name']
        requester_name = createApproveRejectButton(requester_name, accept_class='acceptVacationRequest(this)', reject_class='rejectVacationRequest(this)')
        container.appendChild(requester_name)
        container.setAttribute('data-requester_employee_id', request['requester_employee_id'])
        container.setAttribute('data-request_date', request['date'])

        let date = document.createElement('li')
        date.innerText = `Request Date: ${request['date']}`
        let schedule_conflict = document.createElement('li')
        schedule_conflict.innerText = `Schedule Conflict: ${request['schedule_conflict']}`
        container.appendChild(date)
        container.appendChild(schedule_conflict)
        vacationRequest.appendChild(container)

    }
}

function fetchSchedules() {
    let date_range = findDateRange()
    $.ajax({
        type: "GET",
        url: "/main/schedule/",
        data: {'action': 'all_employees',
            'date_range':date_range},
        dataType: 'json',
        success: function(response) {
            monthSchedules = response
            highlightCalendar()
        },
        contentType:'application/json'
    })
}

function fetchRequests() {
    $.ajax({
        type: "GET",
        url: "/main/manager/request",
        dataType: 'json',
        success: function(response) {
            displayRequests(response)
        },
        contentType:'application/json'
    })
}

function managerAcceptRequest(param){
    let dataNode = param.parentNode.parentNode
    let data = JSON.parse(dataNode.dataset.request_info)
    let csrftoken = getCookie('csrftoken')
    let send_data = JSON.stringify({"action": "finalize", "data":data})
    $.ajax({
        type: "POST",
        url: "/main/manager/request",
        data: send_data,
        headers: {
            'X-CSRFToken': csrftoken
        },
        dataType: 'json',
        success: function(result) {
            if (result[error_detail]) {
                console.log(result[error_detail])
            }
            fetchRequests()
        },
        contentType:'application/json'
    })
}

function managerRejectRequest(param){
    let dataNode = param.parentNode.parentNode
    let data = JSON.parse(dataNode.dataset.request_info)
    let csrftoken = getCookie('csrftoken')
    let send_data = JSON.stringify({"action": "reject", "data":data})
    $.ajax({
        type: "POST",
        url: "/main/manager/request",
        data: send_data,
        headers: {
            'X-CSRFToken': csrftoken
        },
        success: function(result) {
            alert(result)
            fetchRequests()
        },
        contentType:'application/json'
    })
}
function displayRequests(response) {
    $("#incoming-swap-requests").empty()
    let swap_container = document.getElementById('incoming-swap-requests')
    for (r in response) {
        let swap = response[r]
        let swap_request = document.createElement('ul')
        let swap_title = document.createElement('h3')
        swap_title.innerText = 'Requests'
        swap_title = createApproveRejectButton(swap_title, accept_class='managerAcceptRequest(this)', reject_class='managerRejectRequest(this)')
        swap_title.setAttribute('data-request_info', JSON.stringify(swap))
        swap_request.appendChild(swap_title)

        let requester = document.createElement('li')
        requester.innerText = `Requester: ${swap['requester_name']}`
        let requester_container = document.createElement('ul')
        let requester_shift = document.createElement('li')
        requester_shift.innerText = `Original Schedule: ${swap['requester_shift_start']} to ${swap['requester_shift_end']}`
        requester_container.appendChild(requester_shift)

        let acceptor = document.createElement('li')
        acceptor.innerText = `Acceptor: ${swap['acceptor_name']}`
        let acceptor_container = document.createElement('ul')
        let acceptor_shift = document.createElement('li')
        acceptor_shift.innerText = `Original Schedule: ${swap['acceptor_shift_start']} to ${swap['acceptor_shift_end']}`
        acceptor_container.appendChild(acceptor_shift)

        acceptor.appendChild(acceptor_container)
        requester.appendChild(requester_container)
        swap_request.appendChild(requester)
        swap_request.appendChild(acceptor)
        swap_container.appendChild(swap_request)
    }
}

function displayStats() {
    
}



fetchSchedules()
fetchManagerVacation()
fetchRequests()