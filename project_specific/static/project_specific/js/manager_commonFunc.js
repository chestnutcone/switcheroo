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

function selectAll(param) {
    $('input[type="checkbox"]:visible').each(function() {
        this.checked = param.checked
    })
}

function selectRadio(param) {
    $('input[type="radio"]:checked').each(function() {
        this.checked = false
    })
    param.checked = true
}

function searchTable(param, access_id) {
    let text = $(param).val().toLowerCase()
    $(`#${access_id} tr`).filter(
        function () {
        $(this).toggle($(this).text().toLowerCase().indexOf(text) > -1)
    })
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

function daysInMonth(year, month) {
    return 32 - new Date(year, month, 32).getDate()
}

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