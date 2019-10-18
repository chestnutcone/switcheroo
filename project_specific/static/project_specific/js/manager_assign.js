let employee_dict = JSON.parse(document.getElementById('employees').textContent)
let shift_dict = JSON.parse(document.getElementById('shifts').textContent)
let schedule_dict = JSON.parse(document.getElementById('schedules').textContent)

function setSingleDay(param) {
    $('#singlePerson').removeClass('active')
    $('#automaticAssign').removeClass('active')
    $(param).addClass('active')
    $('#singleDayForm').removeClass('hide')
    $('#shiftPatternForm').addClass('hide')
    $('#automaticAssignForm').addClass('hide')
    employeeTable(acecss_id='day', typeofbox='radio')
}

function setSingleDayTimeBased() {
    $('label[for=shiftStart], #shift-start').removeClass('hide')
    $('label[for=shiftEnd], #shift-end').removeClass('hide')
    $('label[for=shiftSelection], #day-shift-selection').addClass('hide')
}

function setSingleDayShiftBased() {
    $('label[for=shiftStart], #shift-start').addClass('hide')
    $('label[for=shiftEnd], #shift-end').addClass('hide')
    $('label[for=shiftSelection], #day-shift-selection').removeClass('hide')
}

function setSinglePerson(param) {
    $('#singleDay').removeClass('active')
    $('#automaticAssign').removeClass('active')
    $(param).addClass('active')
    $('#singleDayForm').addClass('hide')
    $('#shiftPatternForm').removeClass('hide')
    $('#automaticAssignForm').addClass('hide')
    employeeTable(access_id='person', typeofbox='radio')
}

function automaticAssign(param) {
    $('#singleDay').removeClass('active')
    $('#singlePerson').removeClass('active')
    $(param).addClass('active')
    $('#singleDayForm').addClass('hide')
    $('#shiftPatternForm').addClass('hide')
    $('#automaticAssignForm').removeClass('hide')
    employeeTable(access_id='auto')
}

function employeeTable(access_id, typeofbox='checkbox') {
    let table_access = `${access_id}-employees-body`
    let search_bar = `${access_id}-search-bar`
    document.getElementById(search_bar).value = ''
    if (typeofbox == 'checkbox') {
        let select_all = document.getElementById('auto-select-all')
        select_all.checked = false
    }
    
    $(`#${table_access}`).empty()
    let employee_table = document.getElementById(table_access)
    for (e in employee_dict) {
        let employee = employee_dict[e]
        let row = document.createElement('tr')
        let checkbox_cell = document.createElement('td')
        row.setAttribute('data-employee_id', employee['employee_id'])
        let checkbox = document.createElement('input')
        if (typeofbox == 'checkbox') {
            checkbox.setAttribute('type', typeofbox)
        } else if (typeofbox == 'radio') {
            checkbox.setAttribute('type', typeofbox)
            checkbox.setAttribute('onclick', 'selectRadio(this)')
        }
        
        checkbox_cell.appendChild(checkbox)
        let first_name = document.createElement('td')
        first_name.innerText = employee['first_name']
        let last_name = document.createElement('td')
        last_name.innerText = employee['last_name']
        let unit = document.createElement('td')
        unit.innerText = employee['unit']
        let position = document.createElement('td')
        position.innerText = employee['position']

        row.appendChild(checkbox_cell)
        row.appendChild(first_name)
        row.appendChild(last_name)
        row.appendChild(unit)
        row.appendChild(position)

        employee_table.appendChild(row)
    }
}

function searchTable(param, access_id) {
    let text = $(param).val().toLowerCase()

    $(`#${access_id} tr`).filter(
        function () {
        $(this).toggle($(this).text().toLowerCase().indexOf(text) > -1)
    })
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

function setSchedule(access_id) {
    let access_name = `${access_id}-schedule-selection`
    let schedule_list = document.getElementById(access_name)

    for (opt in schedule_dict) {
        let cur_schedule = schedule_dict[opt]
        let cur_option = document.createElement('option')
        cur_option.setAttribute('value', cur_schedule['pk'])
        let name = `${cur_schedule['schedule_name']}: ${cur_schedule['schedule'].join(' ')}`
        cur_option.innerText = name
        schedule_list.appendChild(cur_option)
    }
}

function setShift() {
    let shift_list = document.getElementById('day-shift-selection')
    for (opt in shift_dict) {
        let cur_shift = shift_dict[opt]
        let cur_option = document.createElement('option')
        cur_option.setAttribute('value', cur_shift['pk'])
        cur_option.innerText = cur_shift['shift_name']
        shift_list.appendChild(cur_option)
    }
}

function setMinDate() {
    let day_date = document.getElementById('day-date-picker')
    let person_date = document.getElementById('person-date-picker')
    let auto_date = document.getElementById('auto-date-picker')

    let today =  new Date(new Date().getTime() - new Date().getTimezoneOffset() * 60000).toISOString().split("T")[0]
    day_date.setAttribute('min', today)
    person_date.setAttribute('min', today)
    auto_date.setAttribute('min', today)

    day_date.value = today
    person_date.value = today
    auto_date.value = today
}


setSchedule('auto')
setSchedule('person')
setShift()
setMinDate()

