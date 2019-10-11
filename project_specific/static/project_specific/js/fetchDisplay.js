
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
        let cancelButton = document.createElement('button')
        cancelButton.innerText = 'Cancel'
        cancelButton.setAttribute('onclick', 'cancelRequest(this)')
        shift_item.setAttribute('data-created_time', processing['created'])
        
        
        shift_item.setAttribute('data-applicant_shift_start', processing['applicant_shift_start'])
        shift_item.setAttribute('data-applicant_shift_end', processing['applicant_shift_end'])
        shift_item.setAttribute('data-receiver_shift_start', processing['receiver_shift_start'])
        shift_item.setAttribute('data-receiver_shift_end', processing['receiver_shift_end'])
        shift_item.setAttribute('data-acceptor_employee_id', processing['receiver_employee_id'])

        applicant.innerText = `Own Schedule ${processing['applicant_shift_start']} to ${processing['applicant_shift_end']}`
        receiver.innerText = `Swap Schedule ${processing['receiver_shift_start']} to ${processing['receiver_shift_end']}`
        if (processing['responded']) {
            status = `${processing['accept']}`
            if (processing['accept']) {
                let acceptButton = document.createElement('button')
                acceptButton.innerText = 'Accept'
                acceptButton.setAttribute('onclick', 'finalizeSwap(this)')
                shift_item.innerHTML = status
                shift_item.appendChild(acceptButton)
                shift_item.appendChild(cancelButton)
            } else {
                shift_item.innerHTML = status
                shift_item.appendChild(cancelButton)
            }
        } else {
            status = 'Status: Not Responded'
            shift_item.innerHTML = status
            shift_item.appendChild(cancelButton)
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
        swapDateListContainer.innerText = date
        swapDateListContainer = createCancelButton(swapDateListContainer)

        swapDateListContainer.classList.add('flexbox')
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
                    swaps.setAttribute("data-shift_start", `${shift_start}`)
                    swaps.setAttribute("data-shift_end", `${shift_end}`)
                    swaps.setAttribute("data-employee_id", `${employee['employee_id']}`)
                    
                    let info = document.createTextNode(`${employee_name} ${shift_start} to ${shift_end}`)
                    swaps.appendChild(info)
                    swaps = createAcceptRejectButton(swaps)
                    swaps.classList.add('flexbox')
                    swapDateList.appendChild(swaps)
                }
            } else if (response['available_people']) {
                for (people of response['available_people']) {
                    let swaps = document.createElement('li')
                    swaps.setAttribute("data-shift_start", `${shift_start}`)
                    swaps.setAttribute("data-shift_end", `${shift_end}`)
                    swaps.setAttribute("data-employee_id", `${employee['employee_id']}`)
                    let info = document.createTextNode(people)
                    swaps.appendChild(info)
                    swaps = createAcceptRejectButton(swaps)
                    swaps.classList.add('flexbox')
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
        let vacationDate = document.createTextNode(date)
        vacationList.appendChild(vacationDate)
        for (detail in status) {
            let vacation_detail = document.createElement('li')
            vacation_detail.innerText = `${detail}: ${status[detail]}`
            vacationList.appendChild(vacation_detail)
        }
        vacationResultContainer.appendChild(vacationList)
    }
}

fetchVacationResult()
fetchSwapResult()
fetchRequestResult()