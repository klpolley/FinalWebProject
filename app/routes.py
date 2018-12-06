from flask import flash, redirect, url_for, render_template, request, jsonify
from app import app, db, mail
from app.models import User, Course, Department, MentorToCourse
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, SearchForm, EditAccountForm, ContactForm, AddCourseForm, \
    ResolveRequestForm

@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('edit_account')
        return redirect(next_page)

    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/edit_account', methods=['GET', 'POST'])
@login_required
def edit_account():
    form = EditAccountForm(current_user.username)

    #default to no courses being mentored
    form.department.choices = [(0, 'NONE')] + [(d.id, d.name) for d in Department.query.order_by('name')]
    #dept = Department.query.order_by('name').first()
    #form.course.choices = [(c.id, c.name) for c in Course.query.filter_by(department=dept).order_by('number')]
    form.course.choices = [(0, 'NONE')] + [(c.id, c.name) for c in Course.query.order_by('name')]

    form.remove.choices = [(a.course.id, a.course.name) for a in current_user.courses]

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.name = form.name.data
        current_user.bio = form.bio.data

        course = Course.query.filter_by(id=form.course.data).first()
        if course is not None and MentorToCourse.query.filter_by(mentor=current_user, course=course).count() == 0:
            assoc = MentorToCourse(mentor=current_user, course=course)
            db.session.add(assoc)

        for c in form.remove.data:
            assoc = MentorToCourse.query.filter_by(mentor=current_user, course_id=c).first()
            db.session.delete(assoc)

        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('account', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.name.data = current_user.name
        form.bio.data = current_user.bio

    return render_template('editAccount.html', title='Edit Account', form=form)

@app.route('/add_mentor_course', methods=['GET', 'POST'])
def mentor_courses():

    courses = request.get_json()["courses"]
    for c in courses:
        course = Course.query.filter_by(id=c).first()
        if course is not None and MentorToCourse.query.filter_by(mentor=current_user, course=course).count() == 0:
            assoc = MentorToCourse(mentor=current_user, course=course)
            db.session.add(assoc)

    db.session.commit()

    return jsonify({'please':'work'})

@app.route('/account/<username>', methods=['GET', 'POST'])
@login_required
def account(username):
    user = User.query.filter_by(username=username).first_or_404()
    sent_reqs = user.requests.all()
    received_reqs = user.requested.all()

    contact = ContactForm()
    if contact.validate_on_submit():
        current_user.send_request(user)
        db.session.commit()
        #send email and all that
        msg = Message("Help Request", recipients=[user.email])
        msg.body = contact.message.data
        mail.send(msg)
        flash('Help request sent to: ' + username)

    return render_template('account.html', user=user, sent=sent_reqs, received=received_reqs, contact=contact)


@app.route('/resolve_request', methods=['GET', 'POST'])
@login_required
def resolve():
    form = ResolveRequestForm()
    form.requests.choices = [(r.id, r.name) for r in current_user.requested.all()]

    if form.validate_on_submit():
        for r in form.requests.data:
            user = User.query.filter_by(id=r).first()
            current_user.resolve_request(user)

        db.session.commit()
        return redirect(url_for('account', username=current_user.username))

    return render_template('resolveRequest.html', form=form)


@app.route('/add_course', methods = ['GET','POST'])
def add_course():
    form = AddCourseForm()
    form.existing_dept.choices = [(0, 'NEW DEPARTMENT')]+[(row.id, row.name) for row in Department.query.all()]

    if form.validate_on_submit():
        if form.existing_dept.data != 0:
            course = Course(dept_id=form.existing_dept.data, number=form.number.data, name=form.name.data)
            db.session.add(course)
        else:
            dept = Department(name=form.new_dept_name.data, abbr=form.new_dept_abbr.data)
            db.session.add(dept)
            course = Course(department=dept, number=form.number.data, name=form.name.data)
            db.session.add(course)
        db.session.commit()
        return redirect(url_for('edit_account'))
    else:
        print(form.errors)

    return render_template('newCourse.html', form=form)



@app.route('/course/<dept>')
def course(dept):
    courses = Course.query.filter_by(dept_id=dept).all()

    courseArray = []

    for course in courses:
        courseObj = {}
        courseObj['id'] = course.id
        courseObj['num'] = course.number
        courseObj['name'] = course.name
        courseArray.append(courseObj)

    return jsonify({'courses' : courseArray})


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    form.department.choices = [(row.id, row.name) for row in Department.query.all()]
    dept = Department.query.order_by('name').first()
    form.course.choices = [(c.id, c.name) for c in Course.query.filter_by(department=dept).order_by('number')]
    if request.method == 'POST':
        #user = MentorToCourse.query.filter_by(course_id=form.sCourse.data).all()
        course=Course.query.filter_by(id=form.course.data).first()
        return redirect(url_for('searchResult', course=course.name))
    return render_template('search.html', form=form)


@app.route('/search_result/<course>',methods = ['GET','POST'])
@login_required
def searchResult(course):

    if course is None:
        return "no Mentors for this course"

    else:

        c=Course.query.filter_by(name=course).first()

        mentors=list()
        user = MentorToCourse.query.filter_by(course_id=c.id).all()
        for hh in user:
            mentors.append(User.query.filter_by(id=hh.mentor_id).first())

    return render_template("searchResult.html", mentors=mentors)


@app.route('/reset_db')
def reset_db():
    flash('Resetting Database: deleting old data and repopulating with dummy data')
    # clear all data from all tables
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table {}'.format(table))
        db.session.execute(table.delete())
    db.session.commit()

    # populate tables with dummy data
    users = [
        User(username='profpancake', name='Professor Pancake', email='numberonecake@ghost.edu', bio='Not a professor, definitely a pancake'),
        User(username='mousecop', name='Mouse Cop', email='copper@ghost.edu', bio='Cat no like mouse. Cat like coding WORM'),
        User(username='beets', name='Little Russian Lady', email='numberonecommie@ghost.edu', bio='Please... get me some beets'),
    ]
    users[0].set_password('cat1')
    users[1].set_password('cat2')
    users[2].set_password('cat3')

    db.session.add_all(users)
    db.session.commit()

    users[0].send_request(users[2])
    users[1].send_request(users[0])
    users[2].send_request(users[1])


    departments = [
        Department(name='Computer Science', abbr='COMP'),
        Department(name='Languages', abbr='LNGS'),
        Department(name='Mathematics', abbr='MATH')
    ]
    db.session.add_all(departments)

    courses = [
        Course(name='Principles of Computer Science II', number=172, department=departments[0]),
        Course(name='Introduction to Data Structures', number=220, department=departments[0]),
        Course(name='Language and the Mind', number=242, department=departments[1]),
        Course(name='Statistics', number=124, department=departments[2]),
        Course(name='Intro to WORM Programming', number=999, department=departments[0]),
    ]
    db.session.add_all(courses)

    associations = [
        MentorToCourse(mentor=users[0], course=courses[1]),
        MentorToCourse(mentor=users[0], course=courses[0]),
        MentorToCourse(mentor=users[1], course=courses[3]),
        MentorToCourse(mentor=users[1], course=courses[4]),
        MentorToCourse(mentor=users[2], course=courses[2]),
    ]
    db.session.add_all(associations)

    db.session.commit()

    return redirect(url_for('index'))


