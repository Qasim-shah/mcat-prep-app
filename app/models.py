from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    stripe_customer_id = db.Column(db.String(120), nullable=True)
    stripe_subscription_id = db.Column(db.String(120), nullable=True)
    is_subscribed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(64), index=True)
    topic = db.Column(db.String(120), index=True)
    difficulty = db.Column(db.String(64))
    question_text = db.Column(db.Text)
    passage_text = db.Column(db.Text, nullable=True)
    option_a = db.Column(db.String(256))
    option_b = db.Column(db.String(256))
    option_c = db.Column(db.String(256))
    option_d = db.Column(db.String(256))
    correct_answer = db.Column(db.String(1))
    explanation = db.Column(db.Text)

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    is_correct = db.Column(db.Boolean)
    is_flagged = db.Column(db.Boolean, default=False)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    time_spent = db.Column(db.Integer) # in seconds

# Association table for Test and Question (Many-to-Many)
test_questions = db.Table('test_questions',
    db.Column('test_id', db.Integer, db.ForeignKey('test.id'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id'), primary_key=True)
)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, nullable=False) # Total time for the test
    questions = db.relationship('Question', secondary=test_questions, lazy='subquery',
                                backref=db.backref('tests', lazy=True))

class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    time_taken_minutes = db.Column(db.Integer)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('test_results', lazy=True))
    test = db.relationship('Test', backref=db.backref('test_results', lazy=True))