from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Count
from .models import Test, Question, Answer, TestAttempt, UserAnswer
from payments.models import Subscription


@login_required
def dashboard(request):
    user = request.user
    if user.is_admin_user():
        tests = Test.objects.annotate(
            attempt_count=Count('attempts'),
            avg_score=Avg('attempts__score')
        ).order_by('-created_at')
        recent_attempts = TestAttempt.objects.select_related('user', 'test').order_by('-started_at')[:10]
        total_users_attempted = TestAttempt.objects.values('user').distinct().count()
        ctx = {
            'tests': tests,
            'recent_attempts': recent_attempts,
            'total_tests': tests.count(),
            'total_attempts': TestAttempt.objects.count(),
            'total_users_attempted': total_users_attempted,
            'avg_score': TestAttempt.objects.filter(status='completed').aggregate(a=Avg('score'))['a'],
        }
        return render(request, 'tests_app/admin_dashboard.html', ctx)
    else:
        active_tests = Test.objects.filter(is_active=True)
        my_attempts = TestAttempt.objects.filter(user=user).select_related('test').order_by('-started_at')
        completed_ids = my_attempts.filter(status='completed').values_list('test_id', flat=True)
        ctx = {
            'active_tests': active_tests,
            'my_attempts': my_attempts[:5],
            'completed_test_ids': list(completed_ids),
            'total_taken': my_attempts.filter(status='completed').count(),
            'passed_count': my_attempts.filter(passed=True).count(),
            'avg_score': my_attempts.filter(status='completed').aggregate(a=Avg('score'))['a'],
            'has_subscription': Subscription.has_active(user),
        }
        return render(request, 'tests_app/student_dashboard.html', ctx)


@login_required
def test_list(request):
    tests = Test.objects.filter(is_active=True)
    my_attempts = {}
    if request.user.is_authenticated and not request.user.is_admin_user():
        for a in TestAttempt.objects.filter(user=request.user, status='completed'):
            my_attempts[a.test_id] = a
    return render(request, 'tests_app/test_list.html', {'tests': tests, 'my_attempts': my_attempts})


@login_required
def take_test(request, test_id):
    test = get_object_or_404(Test, id=test_id, is_active=True)
    if request.user.is_admin_user():
        messages.warning(request, 'Admins cannot take tests.')
        return redirect('dashboard')

    # Check premium access
    if test.is_premium and not Subscription.has_active(request.user):
        messages.warning(request, '🔒 This test requires a premium subscription.')
        return redirect('pricing')

    # Check existing in-progress attempt
    attempt = TestAttempt.objects.filter(user=request.user, test=test, status='in_progress').first()
    if not attempt:
        attempt = TestAttempt.objects.create(user=request.user, test=test, total_questions=test.questions.count())

    questions = test.questions.prefetch_related('answers').all()
    answered_ids = set(attempt.user_answers.values_list('question_id', flat=True))

    if request.method == 'POST':
        for q in questions:
            ans_id = request.POST.get(f'question_{q.id}')
            if ans_id:
                answer = get_object_or_404(Answer, id=ans_id, question=q)
                UserAnswer.objects.update_or_create(
                    attempt=attempt,
                    question=q,
                    defaults={'selected_answer': answer}
                )
        # Submit
        if 'submit' in request.POST:
            return redirect('submit_test', attempt_id=attempt.id)

    ctx = {
        'test': test,
        'questions': questions,
        'attempt': attempt,
        'answered_ids': answered_ids,
    }
    return render(request, 'tests_app/take_test.html', ctx)


@login_required
def submit_test(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)
    if attempt.status == 'completed':
        return redirect('test_result', attempt_id=attempt.id)

    correct = 0
    total = attempt.test.questions.count()
    for ua in attempt.user_answers.select_related('selected_answer'):
        if ua.selected_answer and ua.selected_answer.is_correct:
            correct += 1

    score = (correct / total * 100) if total > 0 else 0
    attempt.correct_count = correct
    attempt.total_questions = total
    attempt.score = round(score, 1)
    attempt.passed = score >= attempt.test.passing_score
    attempt.status = 'completed'
    attempt.finished_at = timezone.now()
    attempt.save()

    return redirect('test_result', attempt_id=attempt.id)


@login_required
def test_result(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)
    user_answers = attempt.user_answers.select_related('question', 'selected_answer').prefetch_related('question__answers')
    ctx = {
        'attempt': attempt,
        'user_answers': user_answers,
    }
    return render(request, 'tests_app/test_result.html', ctx)


@login_required
def my_results(request):
    attempts = TestAttempt.objects.filter(user=request.user, status='completed').select_related('test').order_by('-finished_at')
    return render(request, 'tests_app/my_results.html', {'attempts': attempts})


@login_required
def test_detail_admin(request, test_id):
    if not request.user.is_admin_user():
        return redirect('dashboard')
    test = get_object_or_404(Test, id=test_id)
    attempts = TestAttempt.objects.filter(test=test, status='completed').select_related('user').order_by('-finished_at')
    questions = test.questions.prefetch_related('answers').all()
    ctx = {
        'test': test,
        'attempts': attempts,
        'questions': questions,
        'avg_score': attempts.aggregate(a=Avg('score'))['a'],
        'pass_rate': attempts.filter(passed=True).count() / attempts.count() * 100 if attempts.count() > 0 else 0,
    }
    return render(request, 'tests_app/test_detail_admin.html', ctx)
