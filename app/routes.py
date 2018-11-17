from flask import flash, redirect, url_for, render_template,request
from app import app, db
from app.models import User, Course, Department, MentorToCourse
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm,SearchForm

@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html')

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
        Department(name='Mathematics', abbr='MATH'),
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
            next_page = url_for('editAccount')
        return redirect(next_page)

    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/editAccount', methods=['GET', 'POST'])
@login_required
def editAccount():
    return render_template('editAccount.html')

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    form.sDepartment.choices = [(row.id, row.name) for row in Department.query.all()]
    form.sCourse.choices = [(rowA.id, rowA.name) for rowA in Course.query.all()]
    if request.method == 'POST':



        return redirect(url_for('index'))
    return render_template('search.html',  title='Sign In', form=form)





