let monthSchedules = {}

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
let today = new Date()
month = today.getMonth()
year = today.getFullYear()

function resetDateSelectionVariable () {
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
    fetchSchedules()
}

function prev() {
    let pageDate = document.getElementById('pageDate')
    let curYear = parseInt(pageDate.dataset.year)
    let curMonth = parseInt(pageDate.dataset.month)
    prevYear = (curMonth == 0) ? curYear -1: curYear
    prevMonth = (curMonth == 0) ? 11:curMonth-1
    buildCalendar(prevYear, prevMonth)
    fetchSchedules()
}


function buildCalendar (year, month) {
    let calendarTable = document.getElementById('calendar-body')
    $('#calendar-body').empty()

    let pageDate = document.getElementById('pageDate')
    pageDate.setAttribute('data-month', month)
    pageDate.setAttribute('data-year', year)

    let monthAndYear = document.getElementById('monthAndYear')
    let monthAndYearText = document.createTextNode(`${year} ${months[month]}`)
    monthAndYear.insertBefore(monthAndYearText, monthAndYear.childNodes[0])
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
        let separated_dates = date.split('-')
        let new_month = parseInt(separated_dates[1])
        let new_date = parseInt(separated_dates[2])
        let formatted_date = [separated_dates[0], new_month, new_date].join('-')
        let cellNum = cellLookup[formatted_date]

        if (cellNum) {
            switch (monthSchedules[date]['daily_bin']) {
                case 0:
                    $('#calendar-body tr').eq(cellNum[0]).find('td').eq(cellNum[1]).addClass('highlight-level1')
                    break
                case 1:
                    $('#calendar-body tr').eq(cellNum[0]).find('td').eq(cellNum[1]).addClass('highlight-level2')
                    break
                case 2:
                    $('#calendar-body tr').eq(cellNum[0]).find('td').eq(cellNum[1]).addClass('highlight-level3')
                    break
                case 3:
                    $('#calendar-body tr').eq(cellNum[0]).find('td').eq(cellNum[1]).addClass('highlight-level4')
                    break
            }
        }
        

    }

}

let dateRow = 0
let dateCol = 0
let selected_dates = ''

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
    let title = document.createElement('h1')
    title.innerText = 'Daily Summary'
    daily_summary.appendChild(title)
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

