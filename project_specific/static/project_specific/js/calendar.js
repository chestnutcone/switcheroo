let shift_dates = JSON.parse(document.getElementById('shift_dates').textContent)
let shift_start = JSON.parse(document.getElementById('shift_start').textContent)
let shift_end = JSON.parse(document.getElementById('shift_end').textContent)

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
let today = new Date()
month = today.getMonth()
year = today.getFullYear()

function daysInMonth(year, month) {
    return 32 - new Date(year, month, 32).getDate()
}

function cellDate (year, month) {
    dayPrevMonth = daysInMonth(year, month-1)
    dayThisMonth = daysInMonth(year, month)
    thisMonth = new Date(year, month, 1)
    startWeekday = thisMonth.getDay()
    lastMonthStart = dayPrevMonth - startWeekday + 1

    let monthDate = {}
    let cellCount = 0
    let thisMonthCount = 1
    let nextMonthCount = 1
    for (let i=0; i<6; i++) {
        for (let j=0; j<7; j++) {
            if (i == 0 && j < startWeekday) {
                // fill up date from previous month
                monthDate[[i,j]] = lastMonthStart
                lastMonthStart ++
                cellCount ++
            } else if (cellCount<(dayThisMonth+startWeekday)) {
                monthDate[[i,j]] = thisMonthCount
                thisMonthCount ++
                cellCount ++
            } else {
                monthDate[[i,j]] = nextMonthCount
                nextMonthCount ++
                cellCount ++
            }
        }
    }
    return monthDate
}

function reverseCellDate (year, month) {
    dayPrevMonth = daysInMonth(year, month-1)
    dayThisMonth = daysInMonth(year, month)
    thisMonth = new Date(year, month, 1)
    startWeekday = thisMonth.getDay()
    lastMonthStart = dayPrevMonth - startWeekday + 1


    let reversemonthDate = {}
    let cellCount = 0
    let thisMonthCount = 1
    let nextMonthCount = 1
    for (let i=0; i<6; i++) {
        for (let j=0; j<7; j++) {
            if (i == 0 && j < startWeekday) {
                reversemonthDate[formatDateTime(i,lastMonthStart,year,month)] = [i,j]
                lastMonthStart ++
                cellCount ++
            } else if (cellCount<(dayThisMonth+startWeekday)) {
                reversemonthDate[formatDateTime(i,thisMonthCount,year,month)] = [i,j]
                thisMonthCount ++
                cellCount ++
            } else {
                reversemonthDate[formatDateTime(i,nextMonthCount,year,month)] = [i,j]
                nextMonthCount ++
                cellCount ++
            }
        }
    }
    return reversemonthDate
}

function resetDateSelectionVariable () {
    click_count = 0
    dateRow = 0
    dateCol = 0
    selected_dates = []
}

function next() {
    let curYear = parseInt(document.getElementById('curYear').innerHTML)
    let curMonth = parseInt(document.getElementById('curMonth').innerHTML)
    nextYear = (curMonth == 11) ? curYear +1: curYear
    nextMonth = (curMonth+1) % 12
    buildCalendar(nextYear, nextMonth)
}

function prev() {
    let curYear = parseInt(document.getElementById('curYear').innerHTML)
    let curMonth = parseInt(document.getElementById('curMonth').innerHTML)
    prevYear = (curMonth == 0) ? curYear -1: curYear
    prevMonth = (curMonth == 0) ? 11:curMonth-1
    buildCalendar(prevYear, prevMonth)
}


function buildCalendar (year, month) {
    let calendarTable = document.getElementById('calendar-body')
    calendarTable.innerHTML = ''

    let monthAndYear = document.getElementById('monthAndYear')
    monthAndYear.innerHTML = `${year} ${months[month]}`

    let curYear = document.getElementById('curYear')
    let curMonth = document.getElementById('curMonth')
    curYear.innerHTML = year
    curMonth.innerHTML = month

    cellRef = cellDate(year, month)
    for (let i = 0; i<6; i++) {
        let row = document.createElement('tr')
        for (let j = 0;  j <7; j++) {
            let cell = document.createElement('td')
            cellText = document.createTextNode(cellRef[[i,j]])
            cell.appendChild(cellText)
            row.appendChild(cell)
        }
        calendarTable.appendChild(row)
    }
    highlightShift(shift_dates)
    resetDateSelectionVariable()
    $('#calendar-body td').click(selectDate)
}

function highlightShift (shift_dates) {
    let curYear = parseInt(document.getElementById('curYear').innerHTML)
    let curMonth = parseInt(document.getElementById('curMonth').innerHTML)
    let calendarTable = document.getElementById('calendar-body')
    calendarTable.removeAttribute('highlight')

    reverseLookUp = reverseCellDate(curYear, curMonth)
    for (date of shift_dates) {
        answer = reverseLookUp[date]
        if (answer) {
            $('#calendar-body tr').eq(answer[0]).find('td').eq(answer[1]).addClass('highlight')
        }
    }
}

function formatMonth (month_variable) {
// will add one to the js 0-indexed months. Also, 8 => 09. return as str
    mod_month = ((month_variable+1)<10) ? `0${month_variable+1}`: `${month_variable+1}`
    return mod_month
}

function formatDate (date_variable) {
    // Also, 9 => 09. return as str
    mod_date = (date_variable < 10) ? `0${date_variable}`: `${date_variable}`
    return mod_date
}

function formatDateTime (row, date, curYear, curMonth) {
    let nextYear = (curMonth == 11) ? curYear +1: curYear
    let nextMonth = (curMonth+1) % 12
    let prevYear = (curMonth == 0) ? curYear -1: curYear
    let prevMonth = (curMonth == 0) ? 11:curMonth-1

    let str_date = formatDate(date)
    let str_prevMonth = formatMonth(prevMonth)
    let str_curMonth = formatMonth(curMonth)
    let str_nextMonth = formatMonth(nextMonth)

    if (row==0 && date>=22) {
        date_selected = `${prevYear}/${str_prevMonth}/${str_date}`
    } else if (row>=4 && date<=14) {
        date_selected = `${nextYear}/${str_nextMonth}/${str_date}`
    } else {
        date_selected = `${curYear}/${str_curMonth}/${str_date}`
    }
    return date_selected
}

function readWriteDate (row, date, curYear, curMonth, selected_dates, write=false) {
    let date_selected = null

    date_selected = formatDateTime(row, date, curYear, curMonth)
    if (write) {
        selected_dates.push(date_selected)
        return selected_dates
    } else {
        return date_selected
    }
    
}

let click_count = 0
let dateRow = 0
let dateCol = 0
let selected_dates = []

function selectDate(){
    let curYear = parseInt(document.getElementById('curYear').innerHTML)
    let curMonth = parseInt(document.getElementById('curMonth').innerHTML)
    dateLookUp = cellDate(curYear, curMonth)

    selected_dates = []
    if (click_count == 0) {
        $('td').removeClass('date-selection')

        dateRow = this.parentNode.rowIndex
        dateCol = this.cellIndex
        dateRow = dateRow -1  //minus header row
    
        date = dateLookUp[[dateRow, dateCol]]

        selected_dates = readWriteDate(dateRow, date, curYear, curMonth, selected_dates, write=true)
        $('#calendar-body tr').eq(dateRow).find('td').eq(dateCol).addClass('date-selection')

        checkEvent(dateRow, date, curYear, curMonth)
        click_count ++
        click_count = click_count %2
    } else {   
        next_row = this.parentNode.rowIndex
        next_col = this.cellIndex
        next_row = next_row -1  //minus header row
    
        if (next_row < dateRow | ((next_row == dateRow) && (next_col <= dateCol))) {
            $('td').removeClass('date-selection')

            dateRow = this.parentNode.rowIndex
            dateCol = this.cellIndex
            dateRow = dateRow -1  //minus header row
        
            date = dateLookUp[[dateRow, dateCol]]

            selected_dates = readWriteDate(dateRow, date, curYear, curMonth, selected_dates, write=true)
            $('#calendar-body tr').eq(dateRow).find('td').eq(dateCol).addClass('date-selection')
            checkEvent(dateRow, date, curYear, curMonth)
        } else {
            $("#event-container").addClass('hidden')
            date = dateLookUp[[next_row, next_col]]
            
            for (let i=dateRow; i<=next_row; i++) {
                for (let j=0; j<7; j++) {
                    date = dateLookUp[[i, j]]
                    if (i==dateRow) {
                        if ((dateRow != next_row) && (j >= dateCol)) {
                            selected_dates = readWriteDate(dateRow, date, curYear, curMonth, selected_dates, write=true)
                            $('#calendar-body tr').eq(i).find('td').eq(j).addClass('date-selection')
                        } else if ((dateRow == next_row) && ((j >= dateCol) && (j <= next_col))) {
                            selected_dates = readWriteDate(dateRow, date, curYear, curMonth, selected_dates, write=true)
                            $('#calendar-body tr').eq(i).find('td').eq(j).addClass('date-selection')
                        }
                    } else if (i==next_row) {
                        if (j <= next_col) {
                            selected_dates = readWriteDate(dateRow, date, curYear, curMonth, selected_dates, write=true)
                            $('#calendar-body tr').eq(i).find('td').eq(j).addClass('date-selection')
                        }
                    } else {
                        selected_dates = readWriteDate(dateRow, date, curYear, curMonth, selected_dates, write=true)
                        $('#calendar-body tr').eq(i).find('td').eq(j).addClass('date-selection')
                    }
                }

            }
            click_count ++
            click_count = click_count%2
        }
        
    }
}

function checkEvent (dateRow, date, curYear, curMonth) {
    $("#event-detail").empty()
    $("#event-container").removeClass('hidden')
    single_date = readWriteDate(dateRow, date,curYear, curMonth)
    let chosen_date = new Date(single_date)
    $("#event-date").html(`${weekdays[chosen_date.getDay()]} ${date}`)

    if (shift_dates.includes(single_date)) {
        let total_shifts = []
        shift_start_index = getShift(single_date)
        
        for (index of shift_start_index) {
            total_shifts.push(`${shift_start[index]} to ${shift_end[index]}`)
        }
        
        for (shift_detail of total_shifts) {
            $('#event-detail').append(`<li>${shift_detail}</li>`)
        }
    }
}

function getShift (date) {
    let found = false
    let shift_start_index = []
    for (let i=0; i<shift_start.length; i++) {
        if (shift_start[i].startsWith(date)) {
            shift_start_index.push(i)
            found = true
        } else {
            if (found) {
                // shifts are arranged chronologically
                break;
            }
        }
    }
    return shift_start_index
}

function filterDate (dateList) {
    let today = new Date()
    let filtered_date = []
    for (date of dateList) {
        let test_date = new Date(date)
        if (test_date.setHours(0,0,0,0) >= today.setHours(0,0,0,0)) {
            filtered_date.push(date)
        }
    }
    return filtered_date
}

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

function sendSwapDate (){
    let filtered_dates = filterDate(selected_dates)
    let request_dates = []
    for (date of filtered_dates) {
        shift_start_index = getShift(date)
        for (let i=0; i<shift_start_index.length; i++) {
            request_dates.push(shift_start[shift_start_index])
        }
    }
    if (request_dates.length != 0) {

        let send_data = JSON.stringify({"action": "swap", "data":request_dates})
        let csrftoken = getCookie('csrftoken')
        alert(`Swapping the following shifts: ${send_data}`)
        $.ajax({
            type: "POST",
            url: "/main/swap/",
            data: send_data,
            headers: {
                'X-CSRFToken': csrftoken
            },
            dataType: 'json',
            success: function(result) {
                displaySwapResult(result, new_info=true)
            },
            contentType:'application/json'
        })
    } else {
        if (filtered_dates.length != 0) {
            alert('no shifts to be swapped')
        } else {
            alert('cannot swap shifts in the past')
        }
        
    }
    
}

function sendVacationDate(){
    let filtered_dates = filterDate(selected_dates)
    if (filtered_dates.length != 0) {

        let send_data = JSON.stringify({"action": "request_vacation", "data": filtered_dates})
        let csrftoken = getCookie('csrftoken')
        alert(`Asking vaction for the following dates: ${filtered_dates}`)
        $.ajax({
            type: "POST",
            url: "/main/vacation/",
            data: send_data,
            headers: {
                'X-CSRFToken': csrftoken
            },
            dataType: 'text',
            success: function(msg) {
                alert(msg)
                fetchVacationResult()
            },
            contentType:'application/json'
        })
    } else {
        if (selected_dates.length != 0) {
            alert('cannot swap shifts in the past')
        } else {
            alert('no dates to be send')
        }
    }
    
}

function createAcceptRejectButton (parentElement, acceptText='Accept', rejectText='Reject') {
    let acceptButton = document.createElement("button")
    let rejectButton = document.createElement("button")
    acceptButton.innerText = acceptText
    rejectButton.innerText = rejectText
    acceptButton.setAttribute('onclick', 'acceptSwap(this)')
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

function acceptSwap (param) {
    let parent_element = param.parentNode
    let requester_shift_start = parent_element.parentNode.firstChild.dataset.shift_start
    let acceptor_shift_start = parent_element.dataset.shift_start
    let acceptor_employee_id = parent_element.dataset.employee_id

    let data = {'acceptor_shift_start': acceptor_shift_start,
     'acceptor_employee_id': acceptor_employee_id,
    'requester_shift_start': requester_shift_start}

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
    let parent_element = param.parentNode
    parent_element.remove()
}

function fetchRequestResult() {
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

        applicant.innerText = `Own Schedule ${processing['applicant_shift_start']} to ${processing['applicant_shift_end']}`
        receiver.innerText = `Swap Schedule ${processing['receiver_shift_start']} to ${processing['receiver_shift_end']}`
        if (processing['responded']) {
            status = `${processing['accept']}`
            if (processing['accept']) {
                let acceptButton = document.createElement('button')
                acceptButton.innerText = 'Accept'
                acceptButton.setAttribute('onclick', 'acceptRequest(this)')
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

function cancelRequest(param) {
    let parent_element = param.parentNode
    let created_time = parent_element.dataset.created_time
    let requester_shift_start = parent_element.dataset.applicant_shift_start
    console.log(created_time)
    let data = {'created':created_time, 'requester_shift_start':requester_shift_start}

    let send_data = JSON.stringify({"action": "cancel", "data":data})
    console.log(send_data)
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

function acceptRequest(param) {

}

function fetchSwapResult () {
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

buildCalendar (year, month)
fetchVacationResult()
fetchSwapResult()
fetchRequestResult()