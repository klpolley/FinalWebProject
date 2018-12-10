$(document).ready(function() {
    var max_fields      = 5; //maximum input boxes allowed
    var wrapper   		= $(".input_fields_wrap"); //Fields wrapper
    var add_button      = $(".add_field_button"); //Add button ID
    var course_button   = $(".submit_add_courses"); //button to add courses

    var x = 0; //initial text box count
    $(add_button).click(function(e){ //on add input button click
        e.preventDefault();
        if(x < max_fields){ //max input box allowed
            x++; //text box increment
            $(wrapper).append('<div>' +
                    '<p>Department</p><select name="department" id="department_temp"></select>' +
                    '<p>Course</p><select name="course" id="course_temp"></select>' +
                    '<a href="#" class="remove_field">Remove</a></div>'); //add input box

            department = document.getElementById("department_temp");
            department.id = x;
            course = document.getElementById("course_temp");
            course.id = "course" + x;

            select = document.getElementById(x);
            dept = select.setAttribute('onchange', 'updater(this)');
            get_depts(select);
            updater(select);
        }
    });

    get_depts = (select) => {
        fetch('/depts').then(function (response) {
                response.json().then(function (data) {
                    var optionHTML = '';
                    for (var dept of data.departments) {
                        optionHTML += '<option value="' + dept.id + '">' + dept.name + '</option>';
                    }
                    select.innerHTML = optionHTML;
                })
            });
    };

    updater = (field) => {
        dept = field.value;
        course_select = document.getElementById("course"+field.id);

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

    remove = (field) => {
         $(field).parent('div').remove(); x--;
    };

    $(wrapper).on("click",".remove_field",
        function(e){ //user click on remove text
            e.preventDefault();
            remove(this);
        });

    $(course_button).click(function(){ //on add input button click
        var course_ids = [];
        var course_fields = [];

        for (var i = 1; i <= x; i++) {
            var element = document.getElementById("course"+i);
            course_ids.push(element.value);
            course_fields.push(element);
        }

        json = {"courses":course_ids};

        $.ajax({
            type : "POST",
            url : "/add_mentor_course",
            data: JSON.stringify(json),
            contentType: 'application/json;charset=UTF-8',
            success: function() {
                document.getElementById('submitted').innerHTML = "Courses Added!";
                for (var field of course_fields) {
                    remove(field);
                }
                var remove_field = document.getElementById("remove");

                fetch('/remove_courses').then(function (response) {
                    response.json().then(function (data) {
                        var optionHTML = '';
                        for (var course of data.courses) {
                            optionHTML += '<option value="' + course.id + '">' + course.name + '</option>';
                        }
                        remove_field.innerHTML = optionHTML;
                    })
                });
            }
        });
    });

});