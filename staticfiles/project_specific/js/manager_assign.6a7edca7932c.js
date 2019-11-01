let employee_dict = JSON.parse(document.getElementById('employees').textContent)
let shift_dict = JSON.parse(document.getElementById('shifts').textContent)
let schedule_dict = JSON.parse(document.getElementById('schedules').textContent)
let single_day_shift_based = true

function setSingleDay(param) {
    $('#singlePerson').removeClass('active')
    $('#automaticAssign').removeClass('active')
    $(param).addClass('active')
    $('#singleDayForm').removeClass('hide')
    $('#shiftPatternForm').addClass('hide')
    $('#automaticAssignForm').addClass('hide')
    employeeTable(access_id='day', typeofbox='radio')
}

function setSingleDayTimeBased() {
    $('label[for=shiftStart], #shift-start').removeClass('hide')
    $('label[for=shiftEnd], #shift-end').removeClass('hide')
    $('label[for=shiftSelection], #day-shift-selection').addClass('hide')
    single_day_shift_based = false
}

function setSingleDayShiftBased() {
    $('label[for=shiftStart], #shift-start').addClass('hide')
    $('label[for=shiftEnd], #shift-end').addClass('hide')
    $('label[for=shiftSelection], #day-shift-selection').removeClass('hide')
    single_day_shift_based = true
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

function submitSingleDay() {
    let start_date = document.getElementById('day-date-picker').value
    let shift_start_time = document.getElementById('shift-start').value
    let shift_end_time = document.getElementById('shift-end').value
    let shift_selection = document.getElementById('day-shift-selection').value
    let override = document.getElementById('day-override').checked
    let employee = $('#day-employees-body input[type="radio"]:checked')[0]
    let employee_id = null
    if (employee) {
        employee_id = employee.parentNode.parentNode.dataset.employee_id
    }
    let send_data = null
    if (single_day_shift_based) {
        send_data = {'action': 'assign_day_shift_based',
                    'start_date': start_date,
                    'shift_pk': shift_selection,
                    'override': override,
                    'employee_id': employee_id} 
    } else {
        send_data = {'action': 'assign_day_time_based',
                    'start_date': start_date,
                    'shift_start': shift_start_time,
                    'shift_end': shift_end_time,
                    'override': override,
                    'employee_id': employee_id}
    }
    let csrftoken = getCookie('csrftoken') 
    let base_condition = start_date && employee
    let condition = base_condition && (shift_start_time && shift_end_time || shift_selection)
    if (condition) {
        send_data = JSON.stringify(send_data)
        $.ajax({
            type: "POST",
            url: "/main/manager/assign",
            data: send_data,
            headers: {
                'X-CSRFToken': csrftoken
            },
            dataType: 'json',
            success: function(result) {
                displaySingleDayStatus(result)
            },
            contentType:'application/json'
        })
    } else {
        alert('Field cannot be empty. Data not sent')
    }
}

function submitSchedulePatternForm() {
    let start_date = document.getElementById('person-date-picker').value
    let schedule_selection = document.getElementById('person-schedule-selection').value
    let repeat = document.getElementById('person-schedule-repeat').value
    let override = document.getElementById('person-override').checked
    let employee = $('#person-employees-body input[type="radio"]:checked')[0]
    let employee_id = null
    if (employee) {
        employee_id = employee.parentNode.parentNode.dataset.employee_id
    }
    let send_data = null

    send_data = {'action': 'assign_schedule',
                'start_date': start_date,
                'schedule_pk': schedule_selection,
                'repeat': repeat,
                'override': override,
                'employee_id': employee_id} 

    let csrftoken = getCookie('csrftoken') 
    let condition = start_date && schedule_selection && repeat

    if (condition) {
        send_data = JSON.stringify(send_data)
        $.ajax({
            type: "POST",
            url: "/main/manager/assign",
            data: send_data,
            headers: {
                'X-CSRFToken': csrftoken
            },
            dataType: 'json',
            success: function(result) {
                displaySchedulePatternStatus(result)
            },
            contentType:'application/json'
        })
    } else {
        alert('Field cannot be empty. Data not sent')
    }
}

function submitSchedulePatternOverride(param) {
    let dataset = JSON.parse(param.dataset.employee_data)
    let csrftoken = getCookie('csrftoken') 
    let send_data = {'action': 'override_assign_schedule',
                    'employee_id':dataset['args'][0],
                    'employee_data': dataset}
    send_data = JSON.stringify(send_data)
    $.ajax({
        type: "POST",
        url: "/main/manager/assign",
        data: send_data,
        headers: {
            'X-CSRFToken': csrftoken
        },
        dataType: 'json',
        success: function(result) {
            displaySchedulePatternStatus(result)
        },
        contentType:'application/json'
    })
}

function submitAutoAssign() {
    let auto_employees = $("#auto-employees-body input[type='checkbox']:checked")
    let auto_employees_id = []
    auto_employees.each(function() {
        auto_employees_id.push(this.parentNode.parentNode.dataset.employee_id)
    })
    let start_date = document.getElementById('auto-date-picker').value
    let schedule_selection = document.getElementById('auto-schedule-selection').value
    let workers_per_day = document.getElementById('auto-workers-per-day').value
    let day_length = document.getElementById('auto-days-length').value

    let send_data = {'action': 'group_set_schedule',
                    'employees_id_list': auto_employees_id,
                    'start_date': start_date,
                    'schedule_pk': schedule_selection,
                    'workers_per_day': workers_per_day,
                    'day_length': day_length}
    let csrftoken = getCookie('csrftoken') 
    let condition = auto_employees_id.length != 0 && schedule_selection && 
    workers_per_day && day_length

    if (condition) {
        send_data = JSON.stringify(send_data)
        $.ajax({
            type: "POST",
            url: "/main/manager/assign",
            data: send_data,
            headers: {
                'X-CSRFToken': csrftoken
            },
            dataType: 'json',
            success: function(result) {
                displayAutoAssignStatus(result)
            },
            contentType:'application/json'
        })
    } else {
        alert('Field cannot be empty. Data not sent')
    }
}

function submitAssignOverride(param) {
    let dataset = JSON.parse(param.dataset.employee_data)
    let employee_pk = param.dataset.employee_pk
    let csrftoken = getCookie('csrftoken') 
    let send_data = {'action': 'override_auto_assign',
                    'employee_data': dataset,
                    'employee_pk': employee_pk}
    send_data = JSON.stringify(send_data)
    $.ajax({
        type: "POST",
        url: "/main/manager/assign",
        data: send_data,
        headers: {
            'X-CSRFToken': csrftoken
        },
        dataType: 'json',
        success: function(result) {
            displayAssignOverride(param, result)
        },
        contentType:'application/json'
    })
}

function displayAssignOverride(param, response) {
    let employee_list = param.parentNode.parentNode
    $(employee_list).empty()
    let status_detail = response['status_detail']
    let overridable = status_detail['overridable']
    let non_overridable = status_detail['non_overridable']
    let holiday = status_detail['holiday']
    if (response['status']) {
        $(employee_list).remove()
    } else {
        if (overridable.length != 0) {
            let override_list = document.createElement('ul')
            override_list.innerText = 'Overridable'
            for (o in overridable) {
                let cur_o = document.createElement('li')
                let cur_d = overridable[o]
                cur_o.innerText = `${cur_d[0].split(' ')[0]} ${cur_d[1]}`
                override_list.appendChild(cur_o)
            }
            employee_list.appendChild(override_list)
        } 
        if (non_overridable.length != 0) {
            let non_override_list = document.createElement('ul')
            non_override_list.innerText = 'Non-overridable'
            for (n in non_overridable) {
                let cur_n = document.createElement('li')
                let cur_d = non_overridable[n]
                cur_n.innerText = `${cur_d[0].split(' ')[0]} ${cur_d[1]}`
                non_override_list.appendChild(cur_n)
            }
            employee_list.appendChild(non_override_list)
        }
        if (holiday.length != 0) {
            let holiday_list = document.createElement('ul')
            holiday_list.innerText = 'Holiday'
            for (h in holiday) {
                let cur_h = document.createElement('li')
                cur_h.innerText = holiday[h]
                holiday_list.appendChild(cur_h)
            }
            employee_list.appendChild(holiday_list)
        }
    }
    let condition = overridable.length != 0 || non_overridable.length != 0 ||
    holiday.length != 0
    if (condition) {
        let employee_name = document.createTextNode(response['employee_name'])
        employee_list.insertBefore(employee_name, employee_list.childNodes[0])
    }
}

function displaySingleDayStatus(response) {
    $("#singleDay-status").removeClass('hide')
    let title = $('#singleDay-status-title')
    title.removeClass()
    let error_detail = $("#singleDay-error-msg")
    error_detail.empty()
    let holiday_detail = $("#singleDay-holiday")

    let status_detail = response['status_detail']
    if (response['status']) {
        title.addClass('alert alert-success')
        title.text('Status: Success')
    } else if (status_detail['overridable'].length != 0) {
        title.addClass('alert alert-warning')
        title.text('Status: Fail (Can Override)')
        error_detail.text("Not in Employee's preferred workday")

    } else if (status_detail['non_overridable'].length != 0) {
        title.addClass('alert alert-danger')
        title.text('Status: Fail')
        error_detail.text('Existing Schedule or Vacation overlap')
    }
    holiday_detail.empty()
    if (status_detail['holiday'].length != 0) {
        holiday_detail.text('Holiday')
        let holiday = document.createElement('li')
        holiday.innerText = status_detail['holiday'][0]
        holiday_detail.append(holiday)
    }
}

function displaySchedulePatternStatus(response) {
    $("#personPattern-status").removeClass('hide')
    let title = $('#personPattern-status-title')
    title.removeClass()
    let error_detail = $("#personPattern-error-msg")
    error_detail.empty()
    let holiday_detail = $("#personPattern-holiday")
    holiday_detail.empty()
    let overridable = $("#personPattern-overridable")
    overridable.empty()
    let non_overridable = $("#personPattern-non_overridable")
    non_overridable.empty()

    let status_detail = response['status_detail']
    let status_overridable = status_detail['overridable']
    let status_non_overridable = status_detail['non_overridable']

    if (response['status']) {
        title.addClass('alert alert-success')
        title.text('Status: Success')
    } else if (status_overridable.length != 0) {
        title.addClass('alert alert-warning')
        title.text('Status: Fail (Possible Override)')
    } else if (status_detail['non_overridable'].length != 0) {
        title.addClass('alert alert-danger')
        title.text('Status: Fail')
    }
    if (status_overridable.length != 0) {
        
        error_detail.text("Some days are not in Employee's preferred workday")
        overridable.text('Possible Overridable dates')
        for (o in status_overridable) {
            let cur_overridable = status_overridable[o]
            let cur_li = document.createElement('li')
            cur_li.innerText = `${cur_overridable[0]} ${cur_overridable[1]}`
            overridable.append(cur_li)
        }
        let override_button = document.createElement('button')
        override_button.setAttribute('class', 'btn')
        override_button.innerText = 'Override'
        override_button.setAttribute('data-employee_data', JSON.stringify(status_detail))
        override_button.setAttribute('onclick', 'submitSchedulePatternOverride(this)')

        overridable.append(override_button)
    } 
    if (status_non_overridable.length != 0) {

        error_detail.text('Existing Schedule or Vacation overlap')
        non_overridable.text('Non-overridable dates')
        for (n in status_non_overridable) {
            let cur_non = status_non_overridable[n]
            let cur_li = document.createElement('li')
            cur_li.innerText = `${cur_non[0]} ${cur_non[1]}`
            non_overridable.append(cur_li)
        }
    }
    
    if (status_detail['holiday'].length != 0) {
        holiday_detail.text('Holiday')
        let holiday = document.createElement('li')
        holiday.innerText = status_detail['holiday'][0]
        holiday_detail.append(holiday)
    }
}

function displayAutoAssignStatus(response) {
    let status_area = $("#autoAssign-status")
    status_area.empty()
    status_area.removeClass('hide')
    let title = document.createElement('h1')
    title.innerText = 'Status'
    status_area.append(title)
    for (e in response) {
        let cur_e = response[e]
        let employee_list = document.createElement('ul')
        employee_list.innerText = cur_e['employee_name']

        let cur_overridable = cur_e['overridable']
        let cur_non_overridable = cur_e['non_overridable']
        let cur_holiday = cur_e['holiday']
        if (cur_overridable.length != 0) {
            let cur_o_list = document.createElement('ul')
            cur_o_list.innerText = 'Overridable'
            for (o_dates in cur_overridable) {
                let overridable_d = document.createElement('li')
                let cur_date = cur_overridable[o_dates]
                overridable_d.innerText = `${cur_date[0].split(' ')[0]} ${cur_date[1]}`
                cur_o_list.appendChild(overridable_d)
            }
            let override_button = document.createElement('button')
            override_button.setAttribute('class', 'btn')
            override_button.setAttribute('onclick', 'submitAssignOverride(this)')
            override_button.setAttribute('data-employee_data', JSON.stringify(cur_e))
            override_button.setAttribute('data-employee_pk', e)
            override_button.innerText = "Override"
            cur_o_list.appendChild(override_button)
            employee_list.appendChild(cur_o_list)
        }
        if (cur_non_overridable.length != 0) {
            let cur_n_list = document.createElement('ul')
            cur_n_list.innerText = 'Non-overridable'
            for (n_dates in cur_non_overridable) {
                let non_overridable_d = document.createElement('li')
                cur_non_overridable[n_dates]
                non_overridable_d.innerText = `${cur_non_overridable[n_dates][0].split(' ')[0]} ${cur_non_overridable[n_dates][1]}`
                cur_n_list.appendChild(non_overridable_d)
            }
            employee_list.appendChild(cur_n_list)
        }
        if (cur_holiday.length != 0) {
            let cur_holiday_list = document.createElement('ul')
            cur_holiday_list.innerText = "Holiday"
            for (h in cur_holiday) {
                let holiday_count = document.createElement('li')
                holiday_count.innerText = cur_holiday[h]
                cur_holiday_list.appendChild(holiday_count)
            }
            employee_list.appendChild(cur_holiday_list)
        }
        let condition = cur_overridable.length != 0 || 
        cur_non_overridable.length != 0 || cur_holiday.length != 0
        if (condition) {
            status_area.append(employee_list)
        }
    }
}

setSchedule('auto')
setSchedule('person')
setShift()
setMinDate()

