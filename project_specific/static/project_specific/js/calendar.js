let shift_dates = JSON.parse(document.getElementById('shift_dates').textContent)
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

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
    $('#calendar-body td').click(selectDate)

}

function highlightShift (shift_dates) {
    let curYear = parseInt(document.getElementById('curYear').innerHTML)
    let curMonth = parseInt(document.getElementById('curMonth').innerHTML)
    let calendarTable = document.getElementById('calendar-body')
    calendarTable.removeAttribute('highlight')
    shift_dates_arr = shift_dates[0]

    reverseLookUp = reverseCellDate(curYear, curMonth)
    for (date in shift_dates_arr) {
        let shiftDate = new Date(shift_dates_arr[date])
        if (shiftDate.getMonth() == curMonth && shiftDate.getFullYear() == curYear) {
            answer = reverseLookUp[shiftDate.getDate()]
            row = answer[0]
            col = answer[1]
            $('#calendar-body tr').eq(row).find('td').eq(col).addClass('highlight')
        }
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

    let nextYear = (curMonth == 11) ? curYear +1: curYear
    let nextMonth = (curMonth+1) % 12
    let prevYear = (curMonth == 0) ? curYear -1: curYear
    let prevMonth = (curMonth == 0) ? 11:curMonth-1
    selected_dates = []
    if (click_count == 0) {
        $('td').removeClass('date-selection')

        dateRow = this.parentNode.rowIndex
        dateCol = this.cellIndex
        dateRow = dateRow -1  //minus header row
    
        date = dateLookUp[[dateRow, dateCol]]
    
        // let yearSelector = document.getElementById('yearSelector')
        // let monthSelector = document.getElementById('monthSelector')
        // let dateSelector = document.getElementById('dateSelector')
    
        // yearSelector.value = curYear
        // monthSelector.value = curMonth
        // dateSelector.value = date
        if (dateRow==0 & date>=22) {
            selected_dates.push([prevYear, prevMonth, date])
        } else if (dateRow>=4 & date<=14) {
            selected_dates.push([nextYear, nextMonth, date])
        } else {
            selected_dates.push([curYear, curMonth, date])
        }
        $('#calendar-body tr').eq(dateRow).find('td').eq(dateCol).addClass('date-selection')
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
        
            // let yearSelector = document.getElementById('yearSelector')
            // let monthSelector = document.getElementById('monthSelector')
            // let dateSelector = document.getElementById('dateSelector')
        
            // yearSelector.value = curYear
            // monthSelector.value = curMonth
            // dateSelector.value = date

            if (dateRow==0 & date>=22) {
                selected_dates.push([prevYear, prevMonth, date])
            } else if (dateRow>=4 & date<=14) {
                selected_dates.push([nextYear, nextMonth, date])
            } else {
                selected_dates.push([curYear, curMonth, date])
            }
            $('#calendar-body tr').eq(dateRow).find('td').eq(dateCol).addClass('date-selection')
        } else {
            date = dateLookUp[[next_row, next_col]]
    
            // let yearSelector = document.getElementById('yearSelector')
            // let monthSelector = document.getElementById('monthSelector')
            // let dateSelector = document.getElementById('dateSelector')
        
            // yearSelector.value = curYear
            // monthSelector.value = curMonth
            // dateSelector.value = date
            
            for (let i=dateRow; i<=next_row; i++) {
                for (let j=0; j<7; j++) {
                    date = dateLookUp[[i, j]]
                    if (i==dateRow) {
                        if ((dateRow != next_row) & (j >= dateCol)) {
                            if (i==0 & date>=22) {
                                selected_dates.push([prevYear, prevMonth, date])
                            } else if (i>=4 & date<=14) {
                                selected_dates.push([nextYear, nextMonth, date])
                            } else {
                                selected_dates.push([curYear, curMonth, date])
                            }
                            
                            $('#calendar-body tr').eq(i).find('td').eq(j).addClass('date-selection')
                        } else if ((dateRow == next_row) & ((j >= dateCol) & (j <= next_col))) {
                            if (i==0 & date>=22) {
                                selected_dates.push([prevYear, prevMonth, date])
                            } else if (i>=4 & date<=14) {
                                selected_dates.push([nextYear, nextMonth, date])
                            } else {
                                selected_dates.push([curYear, curMonth, date])
                            }
                            $('#calendar-body tr').eq(i).find('td').eq(j).addClass('date-selection')
                        }
                    } else if (i==next_row) {
                        if (j <= next_col) {
                            if (i==0 & date>=22) {
                                selected_dates.push([prevYear, prevMonth, date])
                            } else if (i>=4 & date<=14) {
                                selected_dates.push([nextYear, nextMonth, date])
                            } else {
                                selected_dates.push([curYear, curMonth, date])
                            }
                            $('#calendar-body tr').eq(i).find('td').eq(j).addClass('date-selection')
                        }
                    } else {
                        if (i==0 & date>=22) {
                            selected_dates.push([prevYear, prevMonth, date])
                        } else if (i>=4 & date<=14) {
                            selected_dates.push([nextYear, nextMonth, date])
                        } else {
                            selected_dates.push([curYear, curMonth, date])
                        }
                        $('#calendar-body tr').eq(i).find('td').eq(j).addClass('date-selection')
                    }
                }

            }
            click_count ++
            click_count = click_count%2
        }

        
    }
// for (date of selected_dates) {
//     console.log(date)
// }
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
    let send_dates = JSON.stringify(selected_dates)
    let csrftoken = getCookie('csrftoken')
    $.ajax({
        type: "POST",
        url: "/main/swap/",
        data: send_dates,
        headers: {
            'X-CSRF-Token': csrftoken
        },
        success: function(){},
        contentType:'application/json'
    })
}
buildCalendar (year, month)

