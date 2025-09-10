from flask import render_template, flash, redirect, url_for
from flask_login import login_required
from app import db
from app.admin import bp
from app.admin.forms import QuestionForm, TestForm
from app.models import Question, Test
from app.decorators import admin_required

@bp.route('/add_question', methods=['GET', 'POST'])
@login_required
@admin_required
def add_question():
    form = QuestionForm()
    if form.validate_on_submit():
        question = Question(
            section=form.section.data,
            topic=form.topic.data,
            difficulty=form.difficulty.data,
            question_text=form.question_text.data,
            passage_text=form.passage_text.data if form.passage_text.data else None,
            option_a=form.option_a.data,
            option_b=form.option_b.data,
            option_c=form.option_c.data,
            option_d=form.option_d.data,
            correct_answer=form.correct_answer.data,
            explanation=form.explanation.data
        )
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully!')
        return redirect(url_for('admin.add_question'))
    return render_template('admin/add_question.html', title='Add Question', form=form)

@bp.route('/add_test', methods=['GET', 'POST'])
@login_required
@admin_required
def add_test():
    form = TestForm()
    if form.validate_on_submit():
        test = Test(
            name=form.name.data,
            description=form.description.data,
            duration_minutes=form.duration_minutes.data
        )
        # Add selected questions to the test
        selected_questions = Question.query.filter(Question.id.in_(form.questions.data)).all()
        for q in selected_questions:
            test.questions.append(q)

        db.session.add(test)
        db.session.commit()
        flash('Test created successfully!')
        return redirect(url_for('admin.add_test'))
    return render_template('admin/add_test.html', title='Create Test', form=form)