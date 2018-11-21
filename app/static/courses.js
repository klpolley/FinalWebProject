
var dept_select = document.getElementById("department");
var course_select = document.getElementById("course");

dept_select.onchange = function()  {

    dept = dept_select.value;
    if (dept == 0) {
        course_select.innerHTML = '<option value="0">NONE</option>'
    }
    else {
        fetch('/course/' + dept).then(function (response) {
            response.json().then(function (data) {
                var optionHTML = '';
                for (var course of data.courses) {
                    optionHTML += '<option value="' + course.id + '">' + course.name + '</option>';
                }
                course_select.innerHTML = optionHTML;
            })

        });
    }

};

dept_select.onchange();
