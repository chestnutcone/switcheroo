let monthSchedules = {}

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
    let pageDate = document.getElementById('pageDate')
    let curYear = parseInt(pageDate.dataset.year)
    let curMonth = parseInt(pageDate.dataset.month)
    nextYear = (curMonth == 11) ? curYear +1: curYear
    nextMonth = (curMonth+1) % 12
    buildCalendar(nextYear, nextMonth)
}

function prev() {
    let pageDate = document.getElementById('pageDate')
    let curYear = parseInt(pageDate.dataset.year)
    let curMonth = parseInt(pageDate.dataset.month)
    prevYear = (curMonth == 0) ? curYear -1: curYear
    prevMonth = (curMonth == 0) ? 11:curMonth-1
    buildCalendar(prevYear, prevMonth)
}


function buildCalendar (year, month) {
    let calendarTable = document.getElementById('calendar-body')
    $('#calendar-body').empty()

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
    resetDateSelectionVariable()
    $('#calendar-body td').click(selectDate)
    highlightCalendar()
}



function highlightCalendar() {
    let pageDate = document.getElementById('pageDate')
    let curYear = parseInt(pageDate.dataset.year)
    let curMonth = parseInt(pageDate.dataset.month)
    let cellLookup = reverseCellDate(curYear, curMonth)

    for (date in monthSchedules) {
        let split_date = date.split('-')
        let format_month = formatMonth(split_date[1], add_one=false)
        let format_day = formatDate(split_date[2])
        let format_date = `${split_date[0]}-${format_month}-${format_day}`
        let cellNum = cellLookup[format_date]
        if (cellNum) {
            switch (monthSchedules[date]['daily_bin']) {
                case 0:
                    $('#calendar-body tr').eq(cellNum[0]).find('td').eq(cellNum[1]).addClass('highlight-level1')
                case 1:
                    $('#calendar-body tr').eq(cellNum[0]).find('td').eq(cellNum[1]).addClass('highlight-level2')
                case 2:
                    $('#calendar-body tr').eq(cellNum[0]).find('td').eq(cellNum[1]).addClass('highlight-level3')
                case 3:
                    $('#calendar-body tr').eq(cellNum[0]).find('td').eq(cellNum[1]).addClass('highlight-level4')
            }
        }
        

    }

}


function formatMonth (month_variable, add_one=true) {
// will add one to the js 0-indexed months. Also, 8 => 09. return as str
    if (add_one) {
        mod_month = ((month_variable+1)<10) ? `${month_variable+1}`: `${month_variable+1}`
    } else {
        mod_month = ((month_variable)<10) ? `${month_variable}`: `${month_variable}`
    }
    
    return mod_month
}

function formatDate (date_variable) {
    // Also, 9 => 09. return as str
    mod_date = (date_variable < 10) ? `${date_variable}`: `${date_variable}`
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
        date_selected = `${prevYear}-${str_prevMonth}-${str_date}`
    } else if (row>=4 && date<=14) {
        date_selected = `${nextYear}-${str_nextMonth}-${str_date}`
    } else {
        date_selected = `${curYear}-${str_curMonth}-${str_date}`
    }
    return date_selected
}

let dateRow = 0
let dateCol = 0
let selected_dates = ''

function readWriteDate (row, date, curYear, curMonth, selected_dates, write=false) {
    let date_selected = null

    date_selected = formatDateTime(row, date, curYear, curMonth)
    if (write) {
        selected_dates = date_selected
        return selected_dates
    } else {
        return date_selected
    }
    
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
    $('#calendar-body tr').eq(dateRow).find('td').eq(dateCol).addClass('date-selection')
    checkEvent()
}

function checkEvent () {
    // check on selected_dates. Only one date for now
    $("#today-summary").empty()
    let daily_schedules = monthSchedules[selected_dates]
    let daily_summary = document.getElementById('today-summary')
    for (p in daily_schedules) {
        let person = daily_schedules[p]

        if (typeof(person) !== 'number') {
            let personList = document.createElement('ul')
            let personName = document.createElement('h3')
            personName.innerText = `${person['first_name']} ${person['last_name']}`
            personList.appendChild(personName)
    
            let shift_start = person['shift_start']
            let shift_end = person['shift_end']
            for (shift in shift_start) {
                
                let shiftList = document.createElement('li')
                shiftList.innerText = `From ${shift_start[shift]} to ${shift_end[shift]}`
                personList.appendChild(shiftList)
            }
            daily_summary.appendChild(personList)
        }

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






buildCalendar (year, month)

