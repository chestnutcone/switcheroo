let shifts = JSON.parse(document.getElementById('shifts').textContent)
let schedules = JSON.parse(document.getElementById('schedules').textContent)
let action_logs = JSON.parse(document.getElementById('action_logs').textContent)

function setShiftDisplay(param) {
    $(param).addClass('active')
    $("#schedule-button").removeClass('active')

    $("#shift-form").removeClass('hide')
    $("#schedule-form").addClass('hide')

    $("#schedule-main-page").addClass('hide')

    shiftTable()
}

function setScheduleDisplay(param) {
    $(param).addClass('active')
    $("#shift-button").removeClass('active')

    $("#schedule-form").removeClass('hide')
    $("#shift-form").addClass('hide')

    $("#schedule-main-page").addClass('hide')

    scheduleTable()
}

function shiftTable() {
    document.getElementById('shift-search-bar').value = ''
    let select_all = document.getElementById('shift-select-all')
    select_all.checked = false  
    $(`#shift-table-body`).empty()
    let shift_table = document.getElementById('shift-table-body')
    for (u in shifts) {
        let shift = shifts[u]
        let row = document.createElement('tr')
        let checkbox_cell = document.createElement('td')
        row.setAttribute('data-shift_pk', shift['pk'])
        let checkbox = document.createElement('input')
        checkbox.setAttribute('type', 'checkbox') 
        checkbox_cell.appendChild(checkbox)
        let shift_name = document.createElement('td')
        shift_name.innerText = shift['shift_name']
        let shift_start = document.createElement('td')
        shift_start.innerText = shift['shift_start']
        let shift_dur = document.createElement('td')
        shift_dur.innerText = shift['shift_duration']

        row.appendChild(checkbox_cell)
        row.appendChild(shift_name)
        row.appendChild(shift_start)
        row.appendChild(shift_dur)
        shift_table.appendChild(row)
    }
}

function scheduleTable() {
    document.getElementById('schedule-search-bar').value = ''
    let select_all = document.getElementById('schedule-select-all')
    select_all.checked = false  
    $(`#schedule-table-body`).empty()
    let schedule_table = document.getElementById('schedule-table-body')
    for (u in schedules) {
        let schedule = schedules[u]
        let row = document.createElement('tr')
        let checkbox_cell = document.createElement('td')
        row.setAttribute('data-schedule_pk', schedule['pk'])
        let checkbox = document.createElement('input')
        checkbox.setAttribute('type', 'checkbox') 
        checkbox_cell.appendChild(checkbox)
        let schedule_name = document.createElement('td')
        schedule_name.innerText = schedule['schedule_name']
        let schedule_days = document.createElement('td')
        schedule_days.innerText = schedule['schedule'].join(', ')

        row.appendChild(checkbox_cell)
        row.appendChild(schedule_name)
        row.appendChild(schedule_days)
        schedule_table.appendChild(row)
    }
}

function scheduleDaysDisplay(param) {
    let days = parseInt(param.value)
    let total_options = $("#schedule_pattern_length option").length
    for (let i=1; i<= days; i++) {
        let day_form_id = `schedule_day_${i}`
        $(`#${day_form_id}`).removeClass('hide')
    }
    if (days < total_options) {
        for (let i=days+1; i<= total_options; i++) {
            let day_form_id = `schedule_day_${i}`
            $(`#${day_form_id}`).addClass('hide')
        }
    }
}

function scheduleDaysOptions() {
    $("select[name='schedule_day']").each(function() {

        let cur_opt = document.createElement('option')
        cur_opt.setAttribute('value', null)
        cur_opt.innerText = 'Rest'
        this.appendChild(cur_opt)

        for (s in shifts) {
            let shift = shifts[s]
            let cur_opt = document.createElement('option')
            cur_opt.setAttribute('value', shift['pk'])
            cur_opt.innerText = shift['shift_name']
            this.appendChild(cur_opt)
        }
    })
}

function submitShift() {
    let shift_name = document.getElementById('shift_name_input').value
    let shift_start_time = document.getElementById('shift_start_input').value
    let shift_dur_hr = document.getElementById('shift_duration_hour_input')
    let shift_dur_min = document.getElementById('shift_duration_minute_input')
    let shift_dur_hr_value = null
    let shift_dur_min_value = null
    if (shift_dur_hr.checkValidity()) {
        shift_dur_hr_value = shift_dur_hr.value
    }
    if (shift_dur_min.checkValidity()) {
        shift_dur_min_value = shift_dur_min.value
    }

    let csrftoken = getCookie('csrftoken')
    let condition = shift_name && shift_start_time && 
    shift_dur_hr_value && shift_dur_min_value
    if (condition) {
        let send_data = {'action': 'create_shift',
                        'shift_name': shift_name,
                        'shift_start_time': shift_start_time,
                        'shift_dur_hr': shift_dur_hr_value,
                        'shift_dur_min': shift_dur_min_value}
        send_data = JSON.stringify(send_data)
        $.ajax({
            type: "POST",
            url: "/main/manager/schedule",
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
    } else {
        alert('Field is empty or invalid input. Data not sent')
    }
}

function submitSchedule() {
    let schedule_name = document.getElementById('schedule_name_input').value
    let total_options = $("#schedule_pattern_length option").length
    let chosen_cycle = parseInt(document.getElementById("schedule_pattern_length").value)
    let shift_pk = []
    for (let i=1; i<=chosen_cycle; i++) {
        let cur_opt = document.getElementById(`schedule_day_${i}_select`).value
        shift_pk.push(cur_opt)
    }
    if (chosen_cycle < total_options) {
        for (let i=chosen_cycle+1; i<= total_options; i++) {
            shift_pk.push(null)
        }
    }
    let csrftoken = getCookie('csrftoken')
    let condition = schedule_name && shift_pk
    if (condition) {
        let send_data = {'action': 'create_schedule',
                        'schedule_name': schedule_name,
                        'shift_pk': shift_pk,
                        'cycle': chosen_cycle}
        send_data = JSON.stringify(send_data)
        $.ajax({
            type: "POST",
            url: "/main/manager/schedule",
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
    } else {
        alert('Field is empty or invalid input. Data not sent')
    }
}

function deleteShift() {
    let action = document.getElementById('shiftFormAction').value
    if (action == "Delete") {
        let selected_shift = $("#shift-table-body input[type='checkbox']:checked")
        let all_shift_pk = []
        selected_shift.each(function() {
            let selected_shift_pk = this.parentNode.parentNode.dataset.shift_pk
            all_shift_pk.push(selected_shift_pk)
        })
        let confirmation = confirm(`Are you sure you want to DELETE ${all_shift_pk.length} Shift(s)`)
        if (confirmation) {
            let send_data = {'action': 'delete_shift',
                            'shift_pks': all_shift_pk}
            send_data= JSON.stringify(send_data)
            let csrftoken = getCookie('csrftoken') 
            $.ajax({
                type: "POST",
                url: "/main/manager/schedule",
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
}

function deleteSchedule() {
    let action = document.getElementById('scheduleFormAction').value
    if (action == "Delete") {
        let selected_schedule = $("#schedule-table-body input[type='checkbox']:checked")
        let all_schedule_pk = []
        selected_schedule.each(function() {
            let selected_schedule_pk = this.parentNode.parentNode.dataset.schedule_pk
            all_schedule_pk.push(selected_schedule_pk)
        })
        let confirmation = confirm(`Are you sure you want to DELETE ${all_schedule_pk.length} Schedule(s)`)
        if (confirmation) {
            let send_data = {'action': 'delete_schedule',
                            'schedule_pks': all_schedule_pk}
            send_data= JSON.stringify(send_data)
            let csrftoken = getCookie('csrftoken') 
            $.ajax({
                type: "POST",
                url: "/main/manager/schedule",
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
}

function fetchRecentActions() {
    let action_list = document.getElementById('recentActionsList')
    action_logs = JSON.parse(action_logs)
    // let action_meaning = {1:"Addition", 2:"Change", 3:"Deletion"}
    for (a of action_logs) {
        let action_item = document.createElement('li')
        let action_icon = null
        switch (a[1]) {
            case 1:
                action_icon = '<span class="glyphicon glyphicon-plus text-success"></span>'
                break;
            case 2:
                action_icon = '<span class="glyphicon glyphicon-pencil text-warning"></span>'
                break;
            case 3:
                action_icon = '<span class="glyphicon glyphicon-minus text-danger"></span>'
                break;
        }
        action_item.innerHTML = `${action_icon} ${a[0]} (${a[2]})`
        action_list.appendChild(action_item)
    }
}

fetchRecentActions()
scheduleDaysOptions()