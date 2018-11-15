from app import db
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

requests = db.Table(
    'requests',
    db.Column('sender_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('receiver_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(128), index=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    bio = db.Column(db.String(256))
    courses = db.relationship('MentorToCourse', back_populates='mentor')

    requested = db.relationship(
        'User', secondary=requests,
        primaryjoin=(requests.c.sender_id == id),
        secondaryjoin=(requests.c.receiver_id == id),
        backref=db.backref('requests', lazy='dynamic'), lazy='dynamic'
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def send_request(self, user):
        if not self.has_requested(user):
            self.requested.append(user)

    def has_requested(self, user):
        return self.requested.filter(requests.c.receiver_id == user.id).count() > 0


class MentorToCourse(db.Model):
    mentor_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True)
    mentor = db.relationship("User", back_populates='courses')
    course = db.relationship("Course", back_populates='mentors')

    def __repr__(self):
        return '<Mentor {}, Course {}>'.format(self.mentor_id, self.course_id)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    number = db.Column(db.Integer, index=True)
    dept_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    mentors = db.relationship('MentorToCourse', back_populates='course')

    def __repr__(self):
        return '<Course {}>'.format(self.name)


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    abbr = db.Column(db.String(16))
    courses = db.relationship('Course', backref='department', lazy='dynamic')
