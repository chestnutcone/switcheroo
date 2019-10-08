let shift_dates = JSON.parse(document.getElementById('shift_dates').textContent)
let shift_start = JSON.parse(document.getElementById('shift_start').textContent)
let shift_end = JSON.parse(document.getElementById('shift_end').textContent)

// for (d of shift_dates) {
//     console.log(d)
// }
console.log('shift dates', shift_dates)
console.log('most common shifts', shift_start)

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

    let reverseMonthDate = {}
    let cellCount = 0
    let thisMonthCount = 1
    for (let i=0; i<6; i++) {
        for (let j=0; j<7; j++) {
            if (i == 0 && j < startWeekday) {
                cellCount ++
            } else if (cellCount<(dayThisMonth+startWeekday)) {
                reverseMonthDate[thisMonthCount] = [i,j]
                thisMonthCount ++
                cellCount ++
            } else {
                break
            }
        }
    }
    return reverseMonthDate
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
    // $('#calendar-body td').click(checkEvent)
}

function highlightShift (shift_dates) {
    let curYear = parseInt(document.getElementById('curYear').innerHTML)
    let curMonth = parseInt(document.getElementById('curMonth').innerHTML)
    let calendarTable = document.getElementById('calendar-body')
    calendarTable.removeAttribute('highlight')

    reverseLookUp = reverseCellDate(curYear, curMonth)
    for (date in shift_dates) {
        let shiftDate = new Date(shift_dates[date])
        if (shiftDate.getMonth() == curMonth && shiftDate.getFullYear() == curYear) {
            answer = reverseLookUp[shiftDate.getDate()]
            row = answer[0]
            col = answer[1]
            $('#calendar-body tr').eq(row).find('td').eq(col).addClass('highlight')
        }
    }
}

function readWriteDate (row, date, curYear, curMonth, selected_dates, write=false) {
    let nextYear = (curMonth == 11) ? curYear +1: curYear
    let nextMonth = (curMonth+1) % 12
    let prevYear = (curMonth == 0) ? curYear -1: curYear
    let prevMonth = (curMonth == 0) ? 11:curMonth-1
    let date_selected = null

    date = (date < 10) ? `0${date}`: date
    prevMonth = ((prevMonth+1)<10) ? `0${prevMonth+1}`: prevMonth+1
    curMonth = ((curMonth+1)<10) ? `0${curMonth+1}`: curMonth+1
    nextMonth = ((nextMonth+1)<10) ? `0${nextMonth+1}`: nextMonth+1
    if (row==0 & date>=22) {
        date_selected = `${prevYear}/${prevMonth}/${date}`
    } else if (row>=4 & date<=14) {
        date_selected = `${nextYear}/${nextMonth}/${date}`
    } else {
        date_selected = `${curYear}/${curMonth}/${date}`
    }

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
    
        if (next_row < dateRow | ((next_row == dateRow) & (next_col <= dateCol))) {
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
                        if ((dateRow != next_row) & (j >= dateCol)) {
                            selected_dates = readWriteDate(dateRow, date, curYear, curMonth, selected_dates, write=true)
                            $('#calendar-body tr').eq(i).find('td').eq(j).addClass('date-selection')
                        } else if ((dateRow == next_row) & ((j >= dateCol) & (j <= next_col))) {
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

function sendDate (){
    let request_dates = []
    console.log('selected_dates', selected_dates)
    for (date of selected_dates) {
        shift_start_index = getShift(date)
        for (let i=0; i<shift_start_index.length; i++) {
            request_dates.push(shift_start[shift_start_index])
        }
    }
    console.log('request dates', request_dates)
    if (request_dates.length != 0) {

        let send_dates = JSON.stringify(request_dates)
        let csrftoken = getCookie('csrftoken')
        $.ajax({
            type: "POST",
            url: "/main/swap/",
            data: send_dates,
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function(msg){
                alert(`submission succeeded ${msg}`)
            },
            contentType:'application/json'
        })
    } else {
        alert('no dates to be swapped')
    }
    
}
buildCalendar (year, month)

