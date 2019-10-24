let units = JSON.parse(document.getElementById('units').textContent)
let positions = JSON.parse(document.getElementById('positions').textContent)
let employees = JSON.parse(document.getElementById('employees').textContent)
let users = JSON.parse(document.getElementById('users').textContent)
let workdays = JSON.parse(document.getElementById('workdays').textContent)

let today = new Date()
month = today.getMonth()
year = today.getFullYear()
let dateRow = 0
let dateCol = 0
let selected_dates = ''

let shift_dates = []
let vacation_date = []
let employee_schedule = {}

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

function findEmployeeId() {
    let employees = $("#employee-table-body input[type='radio']:checked")
    let employees_id = null
    if (employees.length) {
        employees.each(function() {
        employees_id = this.parentNode.parentNode.dataset.employee_id
        })
    }
    return employees_id
}

function findPerson() {
    let employee_id = findEmployeeId()
    fetchSchedule(param=null, employee_id=employee_id)
}
function next() {
    let pageDate = document.getElementById('pageDate')
    let curYear = parseInt(pageDate.dataset.year)
    let curMonth = parseInt(pageDate.dataset.month)
    nextYear = (curMonth == 11) ? curYear +1: curYear
    nextMonth = (curMonth+1) % 12
    buildCalendar(nextYear, nextMonth)
    findPerson()
}

function prev() {
    let pageDate = document.getElementById('pageDate')
    let curYear = parseInt(pageDate.dataset.year)
    let curMonth = parseInt(pageDate.dataset.month)
    prevYear = (curMonth == 0) ? curYear -1: curYear
    prevMonth = (curMonth == 0) ? 11:curMonth-1
    buildCalendar(prevYear, prevMonth)
    findPerson()
}

function employeeTable() {
    document.getElementById('employee-search-bar').value = ''
    $(`#employee-table-body`).empty()
    let employee_table = document.getElementById('employee-table-body')
    for (e in employees) {
        let employee = employees[e]
        let row = document.createElement('tr')
        let checkbox_cell = document.createElement('td')
        row.setAttribute('data-employee_id', employee['employee_id'])
        let checkbox = document.createElement('input')
        checkbox.setAttribute('type', 'radio') 
        checkbox.setAttribute('onclick', 'fetchSchedule(param=this)')
        checkbox_cell.appendChild(checkbox)
        let first_name = document.createElement('td')
        first_name.innerText = employee['first_name']
        let last_name = document.createElement('td')
        last_name.innerText = employee['last_name']
        let unit = document.createElement('td')
        unit.innerText = employee['unit']
        let position = document.createElement('td')
        position.innerText = employee['position']
        let employee_id = document.createElement('td')
        employee_id.innerText = employee['employee_id']
        let workday = document.createElement('td')
        workday.innerText = employee['workday_preference'].join(',')

        row.appendChild(checkbox_cell)
        row.appendChild(first_name)
        row.appendChild(last_name)
        row.appendChild(unit)
        row.appendChild(position)
        row.appendChild(employee_id)
        row.appendChild(workday)

        employee_table.appendChild(row)
    }
}


function findDateRange() {
    let pageDate = document.getElementById('pageDate')
    let curYear = parseInt(pageDate.dataset.year)
    let curMonth = parseInt(pageDate.dataset.month)
    let cellRef = cellDate(curYear, curMonth)

    let start_date = formatDateTime(0,cellRef[[0,0]],curYear, curMonth)
    let end_date = formatDateTime(5,cellRef[[5,6]], curYear, curMonth)

    return {'start_date': start_date, 'end_date': end_date}
}

function fetchSchedule(param=null, employee_id=null) {
    if (param) {
        selectRadio(param)
        employee_id = param.parentNode.parentNode.dataset.employee_id
    }
    
    let date_range = findDateRange()
    $.ajax({
        type: "GET",
        url: "/main/schedule/",
        data: {'action': 'single_person',
                'date_range': date_range,
                'employee_id': employee_id},
        dataType: 'json',
        success: function(response) {
            shift_dates = []
            vacation_date = []
            for (s in response['schedules']) {
                let d = response['schedules'][s]
                shift_dates.push(d['start_date'])
                
                if (d['start_date'] in employee_schedule) {
                    employee_schedule[d['start_date']]['shift_start'].push(d['shift_start'])
                    employee_schedule[d['start_date']]['shift_end'].push(d['shift_end'])
                } else {
                    employee_schedule[d['start_date']] = {"shift_start": [d['shift_start']],
                                                    "shift_end": [d["shift_end"]]}
                }
                
            }
            for (v in response['vacations']) {
                let v_dates = response['vacations'][v]
                vacation_date.push(v_dates)
            }
            highlightShift(shift_dates)
            highlightVacationDates(vacation_date)
        },
        contentType:'application/json'
    })

    
}

function buildCalendar (year, month) {
    let calendarTable = document.getElementById('employee-calendar-body')
    $('#employee-calendar-body').empty()

    let pageDate = document.getElementById('pageDate')
    pageDate.setAttribute('data-month', month)
    pageDate.setAttribute('data-year', year)

    let monthAndYear = document.getElementById('monthAndYear')
    monthAndYear.innerHTML = `${year} ${months[month]}`

    cellRef = cellDate(year, month)
    for (let i = 0; i<6; i++) {
        let row = document.createElement('tr')
        for (let j = 0;  j <7; j++) {
            let cell = document.createElement('td')
            let square_content = document.createElement('div')
            square_content.setAttribute('class', 'square_content')

            cellText = document.createTextNode(cellRef[[i,j]])
            square_content.appendChild(cellText)
            cell.appendChild(square_content)
            row.appendChild(cell)
        }
        calendarTable.appendChild(row)
    }
    highlightShift(shift_dates)
    highlightVacationDates(vacation_date)
    $('#employee-calendar-body td').click(selectDate)
}

function selectDate(){
    // allow only single date selection
    let pageDate = document.getElementById('pageDate')
    let curYear = parseInt(pageDate.dataset.year)
    let curMonth = parseInt(pageDate.dataset.month)
    dateLookUp = cellDate(curYear, curMonth)
    $('td').removeClass('date-selection')

    dateRow = this.parentNode.rowIndex
    dateCol = this.cellIndex
    dateRow = dateRow -1  //minus header row

    date = dateLookUp[[dateRow, dateCol]]

    selected_dates = readWriteDate(dateRow, date, curYear, curMonth, selected_dates, write=true)
    $('#employee-calendar-body tr').eq(dateRow).find('td').eq(dateCol).addClass('date-selection')
    checkEvent()
}

function checkEvent() {
    let event = employee_schedule[selected_dates]
    if (event) {
        let detail_container = $('#event-detail')
        detail_container.empty()
        let chosen_date = new Date(selected_dates)
        $("#event-date").text(`${weekdays[chosen_date.getDay()]} ${chosen_date.getDate()}`)
        for (e in event['shift_start']) {
            let list_item = document.createElement('li')
            let shift_start = event['shift_start']
            let shift_end = event['shift_end']
            let delete_button = document.createElement('button')
            delete_button.setAttribute('class', 'btn btn-default')
            delete_button.setAttribute('onclick', 'deleteShift(this)')
            delete_button.innerText = 'Delete'
            list_item.setAttribute('data-shift_start', shift_start)
            list_item.innerText = `From ${shift_start} to ${shift_end}`
            list_item.appendChild(delete_button)
            detail_container.append(list_item)
        }
    }
}

function deleteShift(param) {
    let shift_start = param.parentNode.dataset.shift_start
    let employee_id = findEmployeeId()
    let csrftoken = getCookie('csrftoken')
    if (shift_start && employee_id) {
        let send_data = {'action': 'delete_employee_shift',
                    'shift_start': shift_start,
                    'employee_id': employee_id}
        send_data = JSON.stringify(send_data)
        $.ajax({
            type: "POST",
            url: "/main/manager/view",
            data: send_data,
            headers: {
                'X-CSRFToken': csrftoken
            },
            dataType: 'json',
            success: function(result) {
                if (result['status']) {
                    location.reload();
                } else {
                    alert(result['error_detail'])
                }
            },
            contentType:'application/json'
        })
    }
}

function highlightShift (shift_dates) {
    let pageDate = document.getElementById('pageDate')
    let curYear = parseInt(pageDate.dataset.year)
    let curMonth = parseInt(pageDate.dataset.month)
    $("#employee-calendar-body *").removeClass('highlight')

    reverseLookUp = reverseCellDate(curYear, curMonth)
    for (date of shift_dates) {
        answer = reverseLookUp[date]
        if (answer) {
            $('#employee-calendar-body tr').eq(answer[0]).find('td').eq(answer[1]).addClass('highlight')
        }
    }
}

function highlightVacationDates (v_dates) {
    $("#employee-calendar-body *").removeClass('vacation-highlight')
    let calendar_date_range = findDateRange()
    let start_date = new Date(calendar_date_range['start_date'])
    let end_date = new Date(calendar_date_range['end_date'])
    let pageDate = document.getElementById('pageDate')
    let curYear = parseInt(pageDate.dataset.year)
    let curMonth = parseInt(pageDate.dataset.month)
    let reverseLookUp = reverseCellDate (curYear, curMonth)
    
    for (v in v_dates)  {
        let vacation_date = new Date(v_dates[v])
        if (start_date <= vacation_date && vacation_date <= end_date) {
            let separated_dates = v_dates[v].split('-')
            let new_month = parseInt(separated_dates[1])
            let new_date = parseInt(separated_dates[2])
            let formatted_date = [separated_dates[0], new_month, new_date].join('-')
            let cellLocation = reverseLookUp[formatted_date]

            $('#employee-calendar-body tr').eq(cellLocation[0]).find('td').eq(cellLocation[1]).addClass('vacation-highlight')
        }

    }
}

employeeTable()
buildCalendar(year, month)