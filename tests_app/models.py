from django.db import models
from django.conf import settings


class Test(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_tests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False, help_text='Premium tests require an active subscription')
    duration_minutes = models.PositiveIntegerField(default=60, help_text='Duration in minutes')
    passing_score = models.PositiveIntegerField(default=60, help_text='Passing score percentage')

    def __str__(self):
        return self.title

    def question_count(self):
        return self.questions.count()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Test'
        verbose_name_plural = 'Tests'


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Q{self.order}: {self.text[:60]}"

    class Meta:
        ordering = ['order']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    label = models.CharField(max_length=1, blank=True)  # A, B, C, D

    def __str__(self):
        return f"{'✓' if self.is_correct else '✗'} {self.text[:50]}"

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'


class TestAttempt(models.Model):
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attempts')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='attempts')
    score = models.FloatField(null=True, blank=True)
    correct_count = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_IN_PROGRESS)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    passed = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.test} ({self.score}%)"

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Test Attempt'
        verbose_name_plural = 'Test Attempts'


class UserAnswer(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('attempt', 'question')
        verbose_name = 'User Answer'
        verbose_name_plural = 'User Answers'
