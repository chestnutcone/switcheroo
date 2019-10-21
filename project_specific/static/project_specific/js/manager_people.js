let units = JSON.parse(document.getElementById('units').textContent)
let positions = JSON.parse(document.getElementById('positions').textContent)
let employees = JSON.parse(document.getElementById('employees').textContent)
let users = JSON.parse(document.getElementById('users').textContent)
let workdays = JSON.parse(document.getElementById('workdays').textContent)

function setUnitDisplay(param) {
    $(param).addClass('active')
    $("#position-button").removeClass('active')
    $("#employee-button").removeClass('active')

    $("#unit-form").removeClass('hide')
    $("#position-form").addClass('hide')
    $("#employee-form").addClass('hide')

    $("#people-main-page").addClass('hide')

    unitTable()
}

function setPositionDisplay(param) {
    $(param).addClass('active')
    $("#unit-button").removeClass('active')
    $("#employee-button").removeClass('active')

    $("#position-form").removeClass('hide')
    $("#unit-form").addClass('hide')
    $("#employee-form").addClass('hide')

    $("#people-main-page").addClass('hide')

    positionTable()
}

function setEmployeeDisplay(param) {
    $(param).addClass('active')
    $("#position-button").removeClass('active')
    $("#unit-button").removeClass('active')

    $("#employee-form").removeClass('hide')
    $("#position-form").addClass('hide')
    $("#unit-form").addClass('hide')

    $("#people-main-page").addClass('hide')

    employeeTable()
    userTable()
    positionSelection()
    unitSelection()
    workdaySelection()
}

function employeeTable() {
    document.getElementById('employee-search-bar').value = ''
    let select_all = document.getElementById('employee-select-all')
    select_all.checked = false  
    $(`#employee-table-body`).empty()
    let employee_table = document.getElementById('employee-table-body')
    for (e in employees) {
        let employee = employees[e]
        let row = document.createElement('tr')
        let checkbox_cell = document.createElement('td')
        row.setAttribute('data-employee_id', employee['employee_id'])
        let checkbox = document.createElement('input')
        checkbox.setAttribute('type', 'checkbox') 
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

function userTable() {
    document.getElementById('user-search-bar').value = ''
    $('#user-table-body').empty()
    let user_table = document.getElementById('user-table-body')
    for (u in users) {
        let cur_user = users[u]
        let row = document.createElement('tr')
        let checkbox_cell = document.createElement('td')
        row.setAttribute('data-employee_id', cur_user['employee_id'])
        let checkbox = document.createElement('input')
        checkbox.setAttribute('type', 'radio')
        checkbox.setAttribute('onclick', 'selectRadio(this)')
        checkbox_cell.appendChild(checkbox)

        let user_name = document.createElement('td')
        user_name.innerText = cur_user['username']
        let first_name = document.createElement('td')
        first_name.innerText = cur_user['first_name']
        let last_name = document.createElement('td')
        last_name.innerText = cur_user['last_name']
        let staff_status = document.createElement('td')
        if (cur_user['staff_status']) {
            staff_status.innerHTML = "<span class='glyphicon glyphicon-ok text-success'></span>"
        } else {
            staff_status.innerHTML = "<span class='glyphicon glyphicon-remove text-danger'></span>"
        }
        let employee_id = document.createElement('td')
        employee_id.innerText = cur_user['employee_id']

        row.appendChild(checkbox_cell)
        row.appendChild(user_name)
        row.appendChild(first_name)
        row.appendChild(last_name)
        row.appendChild(staff_status)
        row.appendChild(employee_id)

        user_table.appendChild(row)
    }
}

function positionSelection() {
    let position_selection = document.getElementById('position-selection')
    for (p in positions) {
        let cur_pos = positions[p]
        let cur_opt = document.createElement('option')
        cur_opt.setAttribute('value', cur_pos['pk'])
        cur_opt.innerText = cur_pos['position_name']

        position_selection.appendChild(cur_opt)
    }
}

function unitSelection() {
    let unit_selection = document.getElementById('unit-selection')
    for (p in units) {
        let cur_unit = units[p]
        let cur_opt = document.createElement('option')
        cur_opt.setAttribute('value', cur_unit['pk'])
        cur_opt.innerText = cur_unit['unit_name']

        unit_selection.appendChild(cur_opt)
    }
}

function workdaySelection() {
    let work_selection = document.getElementById('workday-selection')
    for (p in workdays) {
        let cur_workday = workdays[p]
        let cur_opt = document.createElement('option')
        cur_opt.setAttribute('value', cur_workday['pk'])
        cur_opt.innerText = cur_workday['workday_name']

        work_selection.appendChild(cur_opt)
    }
}

function unitTable() {
    document.getElementById('unit-search-bar').value = ''
    let select_all = document.getElementById('unit-select-all')
    select_all.checked = false  
    $(`#unit-table-body`).empty()
    let unit_table = document.getElementById('unit-table-body')
    for (u in units) {
        let unit = units[u]
        let row = document.createElement('tr')
        let checkbox_cell = document.createElement('td')
        row.setAttribute('data-unit_pk', unit['pk'])
        let checkbox = document.createElement('input')
        checkbox.setAttribute('type', 'checkbox') 
        checkbox_cell.appendChild(checkbox)
        let unit_name = document.createElement('td')
        unit_name.innerText = unit['unit_name']

        row.appendChild(checkbox_cell)
        row.appendChild(unit_name)
        unit_table.appendChild(row)
    }
}

function positionTable() {
    document.getElementById('position-search-bar').value = ''
    let select_all = document.getElementById('position-select-all')
    select_all.checked = false  
    $(`#position-table-body`).empty()
    let position_table = document.getElementById('position-table-body')
    for (u in positions) {
        let position = positions[u]
        let row = document.createElement('tr')
        let checkbox_cell = document.createElement('td')
        row.setAttribute('data-position_pk', position['pk'])
        let checkbox = document.createElement('input')
        checkbox.setAttribute('type', 'checkbox') 
        checkbox_cell.appendChild(checkbox)
        let position_name = document.createElement('td')
        position_name.innerText = position['position_name']

        row.appendChild(checkbox_cell)
        row.appendChild(position_name)
        position_table.appendChild(row)
    }
}

function submitUnit() {
    let unit_name = document.getElementById('unit_name_input').value
    let csrftoken = getCookie('csrftoken')
    if (unit_name) {
        let send_data = {'action': 'create_unit',
                    'unit_name': unit_name}
        send_data = JSON.stringify(send_data)
        $.ajax({
            type: "POST",
            url: "/main/manager/people",
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
        alert('Field cannot be empty. Data not sent')
    }
}

function submitPosition() {
    let pos_name = document.getElementById('position_name_input').value
    let csrftoken = getCookie('csrftoken')
    if (pos_name) {
        let send_data = {'action': 'create_position',
                    'position_name': pos_name}
        send_data = JSON.stringify(send_data)
        $.ajax({
            type: "POST",
            url: "/main/manager/people",
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
        alert('Field cannot be empty. Data not sent')
    }
}

function submitEmployee() {
    let employee = $('input[type="radio"]:checked')[0]
    let employee_id = null
    if (employee) {
        employee_id = employee.parentNode.parentNode.dataset.employee_id
    }
    
    let pos_employee = document.getElementById('position-selection').value
    let unit_employee = document.getElementById('unit-selection').value
    let workday_employee = document.getElementById('workday-selection').selectedOptions
    let workday_chosen = []
    for (let i=0; i<workday_employee.length; i++) {
        workday_chosen.push(workday_employee[i].value)
    }
    let date_joined = document.getElementById('date-selection').value

    let condition = employee_id && pos_employee && 
    unit_employee && workday_chosen && date_joined

    let csrftoken = getCookie('csrftoken') 
    if (condition) {
        let send_data = {'action': 'create_employee',
                        'position_pk': pos_employee,
                        'unit_pk': unit_employee,
                        'workday_pk': workday_chosen,
                        'date_joined': date_joined,
                        'employee_id': employee_id}
        send_data = JSON.stringify(send_data)
        $.ajax({
            type: "POST",
            url: "/main/manager/people",
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
        alert('Field cannot be empty. Data not sent')
    }
}