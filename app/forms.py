from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    SelectField, TextAreaField, IntegerField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User, Department, Course


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class SearchForm(FlaskForm):
    department = SelectField('Department',validators=[DataRequired()])
    course = SelectField('Course',validators=[DataRequired()])
    submit = SubmitField('Search')


class EditAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    name = StringField('Full Name', validators=[DataRequired()])
    bio = TextAreaField('Bio', validators=[DataRequired()])
    #department = SelectField('Department', coerce=int)
    #course = SelectField('Course', coerce=int)
    remove = SelectMultipleField('Remove Course', coerce=int)
    submit = SubmitField('Save Changes')

    def __init__(self, original_username, *args, **kwargs):
        super(EditAccountForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class AddCourseForm(FlaskForm):
    existing_dept = SelectField('Department', coerce=int)
    new_dept_name = StringField('New Department Name', validators=[DataRequired()])
    new_dept_abbr = StringField('New Department Abbreviation', validators=[DataRequired()])
    number = IntegerField('Course Number', validators=[DataRequired()])
    name = StringField('Course Name', validators=[DataRequired()])
    submit = SubmitField('Add Course')



class ContactForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired()])
    send = SubmitField('Send')

class ResolveRequestForm(FlaskForm):
    requests = SelectMultipleField('Requests To Resolve', coerce=int)
    submit = SubmitField('Save Changes')