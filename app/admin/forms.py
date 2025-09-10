from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.widgets import ListWidget, CheckboxInput
from app.models import Question

class QuestionForm(FlaskForm):
    section = SelectField('Section', choices=[
        ('Chem/Phys', 'Chemical and Physical Foundations of Biological Systems'),
        ('Bio/Biochem', 'Biological and Biochemical Foundations of Living Systems'),
        ('Psych/Soc', 'Psychological, Social, and Biological Foundations of Behavior'),
        ('CARS', 'Critical Analysis and Reasoning Skills')
    ], validators=[DataRequired()])
    topic = StringField('Topic', validators=[DataRequired(), Length(min=1, max=120)])
    difficulty = SelectField('Difficulty', choices=[
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard')
    ], validators=[DataRequired()])
    question_text = TextAreaField('Question Text', validators=[DataRequired()])
    passage_text = TextAreaField('Passage Text (Optional)')
    option_a = StringField('Option A', validators=[DataRequired()])
    option_b = StringField('Option B', validators=[DataRequired()])
    option_c = StringField('Option C', validators=[DataRequired()])
    option_d = StringField('Option D', validators=[DataRequired()])
    correct_answer = SelectField('Correct Answer', choices=[
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D')
    ], validators=[DataRequired()])
    explanation = TextAreaField('Explanation', validators=[DataRequired()])
    submit = SubmitField('Add Question')

class TestForm(FlaskForm):
    name = StringField('Test Name', validators=[DataRequired(), Length(min=1, max=128)])
    description = TextAreaField('Description')
    duration_minutes = IntegerField('Duration (minutes)', validators=[DataRequired(), NumberRange(min=1)])
    questions = SelectMultipleField('Questions', coerce=int, widget=ListWidget(html_tag='ul'), option_widget=CheckboxInput())
    submit = SubmitField('Create Test')

    def __init__(self, *args, **kwargs):
        super(TestForm, self).__init__(*args, **kwargs)
        self.questions.choices = [(q.id, f'{q.id}: {q.question_text[:50]}...') for q in Question.query.all()]