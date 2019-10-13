
function fetchRequestResult() {
    // for applicant
    $.ajax({
        type: "GET",
        url: "/main/swap/request",
        dataType: 'json',
        success: function(response) {
            $("#swapRequest-container").empty()
            displayRequestResult(response)
        },
        contentType:'application/json'
    })
}


function displayRequestResult(response) {
    // for applicant
    let swap_request_container = document.getElementById('swapRequest-container')
    $('#swapRequest-container').empty()
    for (num in response) {
        let processing = response[num]
        let shift_item = document.createElement('ul')
        let applicant = document.createElement('li')
        let receiver = document.createElement('li')
        let status = ""
        let button_group = document.createElement('div')
        button_group.setAttribute('class', 'pull-right')
        let cancelButton = document.createElement('button')
        let status_title = document.createElement('h4')

        cancelButton.innerText = 'Cancel'
        cancelButton.setAttribute('onclick', 'cancelRequest(this)')
        cancelButton.setAttribute('class', 'btn btn-danger')

        shift_item.setAttribute('data-created_time', processing['created'])
        shift_item.setAttribute('data-applicant_shift_start', processing['applicant_shift_start'])
        shift_item.setAttribute('data-applicant_shift_end', processing['applicant_shift_end'])
        shift_item.setAttribute('data-receiver_employee_id', processing['receiver_employee_id'])

        if (processing['receiver_shift_start']) {
            shift_item.setAttribute('data-receiver_shift_start', processing['receiver_shift_start'])
            shift_item.setAttribute('data-receiver_shift_end', processing['receiver_shift_end'])
            receiver.innerText = `Swap Schedule ${processing['receiver_shift_start']} to ${processing['receiver_shift_end']}`
        } else {
            shift_item.setAttribute('data-receiver_shift_start', '')
            shift_item.setAttribute('data-receiver_shift_end', '')
            receiver.innerText = `No schedule in return`
        }
        

        applicant.innerText = `Own Schedule ${processing['applicant_shift_start']} to ${processing['applicant_shift_end']}`
        
        if (processing['responded']) {
            if (processing['accept']) {
                status = 'Request Accepted'
                status_title.setAttribute('class', 'alert alert-success')
            } else {
                status = 'Request Denied'
                status_title.setAttribute('class', 'alert alert-danger')
            }
            
            if (processing['accept']) {
                let acceptButton = document.createElement('button')
                acceptButton.innerText = 'Finalize'
                acceptButton.setAttribute('onclick', 'finalizeSwap(this)')
                acceptButton.setAttribute('class', 'btn btn-success')
                status_title.innerText = status
                button_group.appendChild(acceptButton)
                button_group.appendChild(cancelButton)
                status_title.appendChild(button_group)
                shift_item.appendChild(status_title)

            } else {
                status_title.innerText = status
                button_group.appendChild(cancelButton)
                status_title.appendChild(button_group)
                shift_item.appendChild(status_title)

            }
        } else {
            status = 'Status: Not Responded'
            status_title.innerText = status
            status_title.setAttribute('class', 'alert alert-info')
            button_group.appendChild(cancelButton)
            status_title.appendChild(button_group)
            shift_item.appendChild(status_title)

        }
        
        
        shift_item.appendChild(applicant)
        shift_item.appendChild(receiver)
        
        swap_request_container.appendChild(shift_item)
    }
}


function fetchSwapResult () {
    // for applicant
    $.ajax({
        type: "GET",
        url: "/main/swap/",
        dataType: 'json',
        success: function(response) {
            $("#swapResult-container").empty()
            displaySwapResult(response)
        },
        contentType:'application/json'
    })
}

function displaySwapResult (result, new_info=false) {
    // for applicant
    let swapResultLists = document.getElementById('swapResult-container')

    for (date in result) {
        response = result[date]
        let swapDateList = document.createElement('ul')
        let swapDateListContainer = document.createElement('div')
        swapDateListContainer.setAttribute('data-shift_start', `${date}`)
        let shift_title = document.createElement('h4')
        shift_title.innerText = date

        shift_title = createCancelButton(shift_title)
        swapDateListContainer.appendChild(shift_title)

        swapDateList.appendChild(swapDateListContainer)
        if (response['success']) {
            let available_shifts = response['available_shifts']
            if (available_shifts) {
                
                for (detail in available_shifts) {
                    let shift_detail = available_shifts[detail]
                    let shift_start = shift_detail['shift_start']
                    let shift_end = shift_detail['shift_end']
                    let employee = shift_detail['employee']
                    let employee_name =  `${employee['first_name']} ${employee['last_name']}`

                    let swaps = document.createElement('li')
                    swaps.setAttribute("data-receiver_shift_start", `${shift_start}`)
                    swaps.setAttribute("data-receiver_shift_end", `${shift_end}`)
                    swaps.setAttribute("data-receiver_employee_id", `${employee['employee_id']}`)
                    swaps.setAttribute("data-datatype", "shift")
                    
                    let info = document.createTextNode(`${employee_name} ${shift_start} to ${shift_end}`)
                    swaps.appendChild(info)
                    swaps = createAcceptRejectButton(swaps)
                    swapDateList.appendChild(swaps)
                }
            } else if (response['available_people']) {
                for (people in response['available_people']) {
                    let swaps = document.createElement('li')
                    person = response['available_people'][people]

                    swaps.setAttribute("data-receiver_first_name", `${person['receiver_first_name']}`)
                    swaps.setAttribute("data-receiver_last_name", `${person['receiver_last_name']}`)
                    swaps.setAttribute("data-receiver_employee_id", `${person['receiver_employee_id']}`)
                    swaps.setAttribute("data-datatype", "people")
                    let info = document.createTextNode(`Available: ${person['receiver_first_name']} ${person['receiver_last_name']}`)
                    swaps.appendChild(info)
                    swaps = createAcceptRejectButton(swaps)
                    swapDateList.appendChild(swaps)
                }
            }
        } else {
            let swaps = document.createElement('li')
            if (response['error']) {
                if (new_info) {
                    alert(response['error_detail'])
                }
                let info = document.createTextNode(response['error_detail'])
                swaps.appendChild(info)
                swapDateList.appendChild(swaps)
            
            } else {
                let info = document.createTextNode('cannot find anyone to swap')
                swaps.appendChild(info)
                swapDateList.appendChild(swaps)
            }
            
        }

        swapResultLists.appendChild(swapDateList)
    }
}

function fetchVacationResult () {
    $.ajax({
        type: "GET",
        url: "/main/vacation/",
        dataType: 'json',
        success: function(response) {
            displayVacationResult(response)
        },
        contentType:'application/json'
    })
}

function displayVacationResult (response) {
    let vacationResultContainer = document.getElementById('vacationResult-container')
    $("#vacationResult-container").empty()
    for (date in response) {
        let status = response[date]
        let vacationList = document.createElement('ul')
        let cancelButton = document.createElement('button')
        cancelButton.innerText = 'Cancel'
        cancelButton.setAttribute('onclick', 'cancelVacation(this)')
        cancelButton.setAttribute('class', 'btn pull-right')
        let vacationDate = document.createElement('h4')
        vacationDate.innerText = date
        vacationDate.appendChild(cancelButton)
        vacationList.appendChild(vacationDate)
        vacationList.appendChild(cancelButton)
        for (detail in status) {
            let vacation_detail = document.createElement('li')
            vacation_detail.innerText = `${detail}: ${status[detail]}`
            vacationList.appendChild(vacation_detail)
        }
        if (status['Approved'] && (status['Rejected'] !== true)) {
            vacationDate.setAttribute('class', 'alert alert-success')
        } else if (status['Rejected'] && (status['Approved'] !== true)) {
            vacationDate.setAttribute('class', 'alert alert-danger')
        } else if (status['Delivered']) {
            vacationDate.setAttribute('class', 'alert alert-info')
        }
        
        vacationResultContainer.appendChild(vacationList)
    }
}

fetchVacationResult()
fetchSwapResult()
fetchRequestResult()