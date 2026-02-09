"""Admin registrations for the accounts app (single, cleaned version)."""
from django.contrib import admin
from django.contrib.auth.models import User
from .models import OTP, Video, PDF, UserProfile
from .models import Item, Mock, PurchasedItem, AttemptedMock, TestResult


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('phone', 'code', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'video_id', 'created_at')
    search_fields = ('title', 'video_id')


@admin.register(PDF)
class PDFAdmin(admin.ModelAdmin):
    list_display = ('company', 'title', 'url', 'created_at')
    search_fields = ('company', 'title')


# ✅ UserProfile को admin में register करो
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'phone', 'has_paid', 'created_at')
    search_fields = ('auth_user__email', 'phone')
    readonly_fields = ('created_at',)
    
    def get_email(self, obj):
        return obj.auth_user.email if obj.auth_user else "N/A"
    get_email.short_description = "Email"


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'item_type', 'price', 'created_at')
    search_fields = ('title',)


@admin.register(Mock)
class MockAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'created_at')
    search_fields = ('title',)


@admin.register(PurchasedItem)
class PurchasedItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'item_type', 'purchased_at')


@admin.register(AttemptedMock)
class AttemptedMockAdmin(admin.ModelAdmin):
    list_display = ('user', 'mock', 'score', 'attempt_date')


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'test_name', 'company', 'difficulty', 'correct_answers', 'total_questions', 'score', 'attempt_date')
    search_fields = ('user__username', 'test_name', 'company')
    list_filter = ('company', 'difficulty', 'attempt_date')
    readonly_fields = ('attempt_date', 'user')
