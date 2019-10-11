
function cancelVacation(param) {
    let parent_element = param.parentNode
    let vacation_date = parent_element.firstChild.textContent
   
    let data = {'vacation_date':vacation_date}
    let send_data = JSON.stringify({"action": "cancel", "data":data})
    let csrftoken = getCookie('csrftoken')
    $.ajax({
        type: "POST",
        url: "/main/vacation/",
        data: send_data,
        headers: {
            'X-CSRFToken': csrftoken
        },
        dataType: 'json',
        success: function(result) {
            if (result['status']) {
                alert('Vacation cancelled')
                fetchVacationResult()
            }
        },
        contentType:'application/json'
    })
}