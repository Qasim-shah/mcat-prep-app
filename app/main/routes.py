from flask import render_template, request, flash, redirect, url_for, session, current_app
from flask_login import login_required, current_user
from app.main import bp
from app.models import Question, UserProgress, User, Test, TestResult
from app import db
from datetime import datetime, timedelta
import stripe

@bp.route('/')
def landing():
    return render_template('landing.html', title='Welcome')

@bp.route('/dashboard')
@login_required
def index():
    total_questions = UserProgress.query.filter_by(user_id=current_user.id).count()
    correct_questions = UserProgress.query.filter_by(user_id=current_user.id, is_correct=True).count()
    accuracy = (correct_questions / total_questions) * 100 if total_questions > 0 else 0
    time_spent = db.session.query(db.func.sum(UserProgress.time_spent)).filter_by(user_id=current_user.id).scalar() or 0
    avg_time_per_question = (time_spent / total_questions) if total_questions > 0 else 0

    # Fetch data for charts
    sections = ["Chem/Phys", "Bio/Biochem", "Psych/Soc", "CARS"]
    chart_data = {}
    for section in sections:
        correct = db.session.query(UserProgress).join(Question).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.is_correct == True,
            Question.section == section
        ).count()
        incorrect = db.session.query(UserProgress).join(Question).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.is_correct == False,
            Question.section == section
        ).count()
        chart_data[section.replace('/', '_').lower() + '_data'] = {'correct': correct, 'incorrect': incorrect}

    # Data for difficulty charts
    difficulties = ["Easy", "Medium", "Hard"]
    difficulty_data = {}
    for difficulty in difficulties:
        correct = db.session.query(UserProgress).join(Question).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.is_correct == True,
            Question.difficulty == difficulty
        ).count()
        incorrect = db.session.query(UserProgress).join(Question).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.is_correct == False,
            Question.difficulty == difficulty
        ).count()
        difficulty_data[difficulty.lower() + '_data'] = {'correct': correct, 'incorrect': incorrect}

    # Overall performance data
    overall_correct = UserProgress.query.filter_by(user_id=current_user.id, is_correct=True).count()
    overall_incorrect = UserProgress.query.filter_by(user_id=current_user.id, is_correct=False).count()
    overall_performance_data = {'correct': overall_correct, 'incorrect': overall_incorrect}

    return render_template('index.html', title='Dashboard',
                           total_questions=total_questions,
                           accuracy=accuracy,
                           time_spent=time_spent,
                           avg_time_per_question=avg_time_per_question,
                           **chart_data,
                           **difficulty_data,
                           overall_performance_data=overall_performance_data)

@bp.route('/practice', methods=['GET', 'POST'])
@login_required
def practice():
    if not current_user.is_subscribed:
        flash('Please subscribe to access practice questions.')
        return redirect(url_for('main.subscribe'))
    difficulty_filter = request.args.get('difficulty', session.get('difficulty_filter', 'All'))
    session['difficulty_filter'] = difficulty_filter

    if 'answered_questions' not in session:
        session['answered_questions'] = []

    if request.method == 'POST':
        question_id = request.form.get('question_id')
        question = Question.query.get(question_id)
        user_answer = request.form.get('answer')
        is_correct = (user_answer == question.correct_answer)
        is_flagged = True if request.form.get('flag_question') else False
        time_spent = int(request.form.get('time_spent', 0))
        print(f"Time spent received: {time_spent} seconds")
        print(f"Answered questions in session (before adding current): {session.get('answered_questions')}")

        user_progress = UserProgress(
            user_id=current_user.id,
            question_id=question.id,
            is_correct=is_correct,
            is_flagged=is_flagged,
            time_spent=time_spent
        )
        db.session.add(user_progress)
        db.session.commit()
        if question.id not in session['answered_questions']:
            session['answered_questions'].append(question.id)
            session.modified = True # Mark session as modified
        print(f"Answered questions in session (after adding current): {session.get('answered_questions')}")
        
        return render_template('practice.html', question=question, user_answer=user_answer, is_correct=is_correct, show_explanation=True, time_spent_question=time_spent)

    # GET request for a new question
    answered_ids = session['answered_questions']
    query = Question.query.filter(Question.id.notin_(answered_ids))

    if difficulty_filter != 'All':
        query = query.filter_by(difficulty=difficulty_filter)

    question = query.order_by(db.func.random()).first()

    if not question:
        flash('You have answered all available questions! Starting a new session.')
        session['answered_questions'] = [] # Reset for a new session
        return redirect(url_for('main.practice', difficulty=difficulty_filter)) # Redirect to get a new question

    return render_template('practice.html', question=question, show_explanation=False, current_difficulty=difficulty_filter)

@bp.route('/progress')
@login_required
def progress():
    # Section-wise performance
    sections = ["Chem/Phys", "Bio/Biochem", "Psych/Soc", "CARS"]
    section_performance = {}
    for section in sections:
        total = db.session.query(UserProgress).join(Question).filter(
            UserProgress.user_id == current_user.id,
            Question.section == section
        ).count()
        correct = db.session.query(UserProgress).join(Question).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.is_correct == True,
            Question.section == section
        ).count()
        accuracy = (correct / total) * 100 if total > 0 else 0
        section_performance[section] = {'total': total, 'correct': correct, 'accuracy': accuracy}

    # Daily streaks (simplified for now)
    today = datetime.utcnow().date()
    streak_count = 0
    for i in range(30): # Check last 30 days
        date_to_check = today - timedelta(days=i)
        questions_answered_today = UserProgress.query.filter(
            UserProgress.user_id == current_user.id,
            db.func.date(UserProgress.answered_at) == date_to_check
        ).count()
        if questions_answered_today > 0:
            streak_count += 1
        else:
            break # Streak broken

    # Overall mastery (simplified: total correct / total questions)
    total_answered = UserProgress.query.filter_by(user_id=current_user.id).count()
    total_correct = UserProgress.query.filter_by(user_id=current_user.id, is_correct=True).count()
    overall_mastery = (total_correct / total_answered) * 100 if total_answered > 0 else 0

    return render_template('progress.html', title='Progress Tracker',
                           section_performance=section_performance,
                           streak_count=streak_count,
                           overall_mastery=overall_mastery)

@bp.route('/subscribe')
@login_required
def subscribe():
    if current_user.is_subscribed:
        flash('You are already subscribed!')
        return redirect(url_for('main.index'))

    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': current_app.config['STRIPE_PRICE_ID'],
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=url_for('main.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('main.cancel', _external=True),
            customer_email=current_user.email,
            client_reference_id=current_user.id
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f'Error creating checkout session: {e}')
        return redirect(url_for('main.index'))

@bp.route('/success')
@login_required
def success():
    flash('Subscription successful!')
    return redirect(url_for('main.index'))

@bp.route('/cancel')
@login_required
def cancel():
    flash('Subscription cancelled.')
    return redirect(url_for('main.index'))

@bp.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('stripe-signature')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, current_app.config['STRIPE_WEBHOOK_SECRET']
        )
    except ValueError as e:
        # Invalid payload
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return 'Invalid signature', 400

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('client_reference_id')
        customer_id = session.get('customer')
        subscription_id = session.get('subscription')

        if user_id:
            user = User.query.get(int(user_id))
            if user:
                user.stripe_customer_id = customer_id
                user.stripe_subscription_id = subscription_id
                user.is_subscribed = True
                db.session.commit()
                print(f"User {user.username} subscribed successfully!")

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        customer_id = subscription.get('customer')
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            user.is_subscribed = False
            db.session.commit()
            print(f"User {user.username} subscription cancelled.")

    return 'OK', 200

@bp.route('/tests')
@login_required
def tests():
    tests = Test.query.all()
    return render_template('tests.html', title='Practice Tests', tests=tests)

@bp.route('/test/<int:test_id>')
@login_required
def take_test(test_id):
    test = Test.query.get_or_404(test_id)
    if not test.questions:
        flash('This test has no questions.')
        return redirect(url_for('main.tests'))

    # Initialize test session
    session['current_test_id'] = test.id
    session['test_questions_ids'] = [q.id for q in test.questions]
    session['current_question_index'] = 0
    session['test_start_time'] = int(datetime.now().timestamp())
    session['test_answers'] = []
    session.modified = True

    current_question = test.questions[0]
    return render_template('test_question.html',
                           test=test,
                           current_question=current_question,
                           current_question_index=0,
                           total_questions=len(test.questions),
                           start_time=session['test_start_time'])

@bp.route('/submit_test_answer/<int:test_id>/<int:question_index>', methods=['POST'])
@login_required
def submit_test_answer(test_id, question_index):
    test = Test.query.get_or_404(test_id)
    question_id = request.form.get('question_id')
    user_answer = request.form.get('answer')
    start_time = int(request.form.get('start_time'))
    time_taken = int(datetime.now().timestamp()) - start_time

    question = Question.query.get(question_id)
    is_correct = (user_answer == question.correct_answer)

    # Store answer in session for later processing (when test ends)
    if 'test_answers' not in session:
        session['test_answers'] = {}
    if str(test_id) not in session['test_answers']:
        session['test_answers'][str(test_id)] = []

    session['test_answers'][str(test_id)].append({
        'question_id': question_id,
        'user_answer': user_answer,
        'is_correct': is_correct,
        'time_taken': time_taken
    })
    session.modified = True

    next_question_index = question_index + 1
    if next_question_index < len(test.questions):
        # Go to next question
        return render_template('test_question.html',
                               test=test,
                               current_question=test.questions[next_question_index],
                               current_question_index=next_question_index,
                               total_questions=len(test.questions),
                               start_time=int(datetime.now().timestamp()))
    else:
        # End of test, calculate results
        total_correct = sum(1 for ans in session['test_answers'][str(test_id)] if ans['is_correct'])
        score = (total_correct / len(test.questions)) * 100
        total_time_taken = sum(ans['time_taken'] for ans in session['test_answers'][str(test_id)])

        test_result = TestResult(
            user_id=current_user.id,
            test_id=test.id,
            score=score,
            time_taken_minutes=round(total_time_taken / 60)
        )
        db.session.add(test_result)
        db.session.commit()

        # Clear test answers from session
        session.pop('test_answers', None)

        flash(f'Test completed! Your score: {score:.2f}%')
        return redirect(url_for('main.test_results', test_result_id=test_result.id))

@bp.route('/test_results/<int:test_result_id>')
@login_required
def test_results(test_result_id):
    test_result = TestResult.query.get_or_404(test_result_id)
    if test_result.user_id != current_user.id:
        abort(403) # Forbidden
    return render_template('test_results.html', title='Test Results', test_result=test_result)
