"""Models for the `accounts` app.

This file provides a single, authoritative model definition for each
model used by the app. The `PDF` model below matches the schema created
in the existing initial migration (`0001_initial.py`) so migrations
and the database stay consistent.
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from django.conf import settings


class PDF(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url = models.URLField()
    company = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} ({self.company})"


class UserProfile(models.Model):
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    auth_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    created_at = models.DateTimeField(default=timezone.now)
    has_paid = models.BooleanField(default=False)
    paid_companies = models.JSONField(default=dict, blank=True)
    test_results = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.phone or f"UserProfile {self.id}"


class OTP(models.Model):
    phone = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def is_expired(self):
        return (timezone.now() - self.created_at).total_seconds() > 10 * 60

    def __str__(self):
        return f"OTP for {self.phone}: {self.code}"


class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_id = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def thumbnail_url(self):
        return f"https://img.youtube.com/vi/{self.video_id}/hqdefault.jpg"

    def __str__(self):
        return self.title


class Transaction(models.Model):
    transaction_id = models.CharField(max_length=255, unique=True)
    company = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"Transaction {self.transaction_id} — {self.company} ({self.amount})"


# New models for marketplace items and user activity
class Item(models.Model):
    ITEM_TYPES = [
        ("pdf", "PDF"),
        ("mock", "Mock"),
        ("interview", "Interview"),
        ("course", "Course"),
    ]

    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    file_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} ({self.item_type})"


class Mock(models.Model):
    title = models.CharField(max_length=255)
    questions = models.JSONField(default=list, blank=True)
    duration = models.IntegerField(help_text="duration in minutes", default=30)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class PurchasedItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchased_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    item_type = models.CharField(max_length=20)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    purchased_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-purchased_at']

    def __str__(self):
        return f"{self.title} - {self.user.username} ({self.purchased_at.date()})"

    def as_dict(self):
        return {
            'id': self.id,
            'itemId': self.item.id if self.item else None,
            'itemType': self.item_type,
            'title': self.title,
            'amountPaid': float(self.amount_paid) if self.amount_paid else 0,
            'transactionId': self.transaction_id,
            'purchasedAt': self.purchased_at.isoformat(),
        }


class AttemptedMock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempted_mocks')
    mock = models.ForeignKey(Mock, on_delete=models.CASCADE)
    score = models.IntegerField()
    attempt_date = models.DateTimeField(default=timezone.now)

    def as_dict(self):
        return {
            'id': self.id,
            'mockId': self.mock.id,
            'score': self.score,
            'attemptDate': self.attempt_date.isoformat(),
        }


class UserActivity(models.Model):
    """Track all user activities - logins, purchases, quiz attempts, etc."""
    
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('pdf_purchase', 'PDF Purchase'),
        ('pdf_view', 'PDF View'),
        ('mock_attempt', 'Mock Test Attempt'),
        ('mock_complete', 'Mock Test Complete'),
        ('quiz_attempt', 'Quiz Attempt'),
        ('quiz_complete', 'Quiz Complete'),
        ('interview_attempt', 'Interview Attempt'),
        ('interview_complete', 'Interview Complete'),
        ('video_watch', 'Video Watch'),
        ('profile_update', 'Profile Update'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    data = models.JSONField(default=dict, blank=True)  # Store extra data like score, amount, etc.
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'User Activities'
    
    def __str__(self):
        return f"{self.user.email} - {self.activity_type} ({self.created_at.date()})"
    
    def as_dict(self):
        return {
            'id': self.id,
            'activityType': self.activity_type,
            'title': self.title,
            'description': self.description,
            'data': self.data,
            'createdAt': self.created_at.isoformat(),
        }


class TestResult(models.Model):
    """Store quiz/test results for users."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results_db')
    test_name = models.CharField(max_length=255)  # e.g., "Google - Easy", "OpenAI - Medium"
    company = models.CharField(max_length=50, blank=True)  # e.g., "google", "openai"
    difficulty = models.CharField(max_length=20, blank=True)  # e.g., "easy", "medium", "hard"
    total_questions = models.IntegerField()
    correct_answers = models.IntegerField()
    score = models.IntegerField()  # Percentage or raw score
    time_taken = models.CharField(max_length=20, blank=True)  # e.g., "15:30"
    attempt_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-attempt_date']

    def __str__(self):
        return f"{self.test_name} - {self.user.username} ({self.attempt_date.date()})"

    def as_dict(self):
        return {
            'id': self.id,
            'testName': self.test_name,
            'company': self.company,
            'difficulty': self.difficulty,
            'totalQuestions': self.total_questions,
            'correctAnswers': self.correct_answers,
            'score': self.score,
            'timeTaken': self.time_taken,
            'attemptDate': self.attempt_date.isoformat(),
        }

class Question(models.Model):
    """Questions organized by company and difficulty level."""
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    COMPANY_CHOICES = [
        ('google', 'Google'),
        ('openai', 'OpenAI'),
        ('uber', 'Uber'),
        ('microsoft', 'Microsoft'),
    ]
    
    company = models.CharField(max_length=50, choices=COMPANY_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('company', 'difficulty', 'question_text')
        ordering = ['company', 'difficulty', 'id']
    
    def __str__(self):
        return f"{self.get_company_display()} - {self.get_difficulty_display()}: {self.question_text[:50]}"
    
    def as_dict(self):
        return {
            'id': self.id,
            'company': self.company,
            'difficulty': self.difficulty,
            'questionText': self.question_text,
            'optionA': self.option_a,
            'optionB': self.option_b,
            'optionC': self.option_c,
            'optionD': self.option_d,
            'correctAnswer': self.correct_answer,
            'explanation': self.explanation,
        }

