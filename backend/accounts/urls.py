"""
URL routes for the accounts app. This file maps both template views and API endpoints.
"""
from django.urls import path
from . import views
from . import api
from . import forms
from django.contrib.auth import views as auth_views
from . import views_payment
from django.urls import path, re_path
from api_database import (
    api_register_user,
    api_login_user,
    api_user_profile,
    api_transactions,
    api_test_results,
    api_user_info,
    api_database_stats,
    api_track_activity,
    api_record_pdf_purchase,
    api_record_mock_attempt,
    api_record_quiz_attempt,
    api_get_user_profile_data
)

app_name = 'accounts'

urlpatterns = [
    # Template pages

    path('', views.index, name='index'),
    path('videos.html', views.videos_page, name='videos_page'),
    path('pdfs.html', views.pdfs_page, name='pdfs_page'), 
    path('quiz.html', views.quiz_page, name='quiz_page'),
    path('BTech.html', views.BTech_page, name='BTech_page'),
    path('Interview.html', views.interview_page, name='interview_page'),
    path('contect.html', views.contect_page, name='contect_page'),
    path('login.html', views.login_page, name='login_page'),
    path('login/', views.login_page, name='login_page'),
    path('signup.html', views.signup_page, name='signup_page'),
    path('signup/', views.signup_page, name='signup_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_user, name='logout_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),

    # Test flow pages
    path('select-difficulty/', views.select_difficulty, name='select_difficulty'),
    path('test-instructions/', views.test_instructions, name='test_instructions'),
    path('test-page/', views.test_page, name='test_page'),
    path('test-result/', views.test_result, name='test_result'),

    # Password reset flow (email-based) using custom styled forms
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html', form_class=forms.StyledPasswordResetForm, success_url='/password_reset/done/'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html', form_class=forms.StyledSetPasswordForm, success_url='/reset/done/'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),



    # API endpoints
    path('send_otp/', views.send_otp, name='send_otp'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('me/', views.me, name='me'),
    path('list_videos/', views.list_videos, name='list_videos'),
    path('list_pdfs/', views.list_pdfs, name='list_pdfs'),
    path('mark_paid/', views.mark_paid, name='mark_paid'),
    path('verify_transaction/', views_payment.verify_transaction, name='verify_transaction'),
    path('pdf/<int:pk>/download/', views.pdf_download, name='pdf_download'),
    # New API endpoints for purchase, mock attempts and profile
    path('purchase/', api.purchase, name='purchase'),
    path('mock/attempt/', api.mock_attempt, name='mock_attempt'),
    path('user/<int:user_id>/profile/', api.user_profile, name='user_profile'),
    path('user/<int:user_id>/purchased-items/', api.get_user_purchased_items, name='get_user_purchased_items'),
    path('user/<int:user_id>/test-results/', api.get_user_test_results, name='get_user_test_results'),
    path('token/', api.token_for_user, name='token_for_user'),
    # Temporary test endpoints (remove in production)
    path('test/create_item/', api.test_create_item, name='test_create_item'),
    path('test/create_mock/', api.test_create_mock, name='test_create_mock'),
    path('api/get-questions/', api.get_questions, name='get_questions'),
    path('api/get-user-email/', views.get_user_email, name='get_user_email'),
    path('api/submit-test/', views.submit_test, name='submit_test'),
    path('api/save-test-result/', views.save_test_result, name='save_test_result'),
    path('api/delete-test-result/', views.delete_test_result, name='delete_test_result'),
    
    # Company Details Page
    path('company/<str:company>/', views.company_details, name='company_details'),
    
    path('users-list/', views.view_all_users, name='view_all_users'),
    
    # ============================================================================
    # DATABASE API ENDPOINTS
    # ============================================================================
    
    # Authentication APIs
    path('api/register/', api_register_user, name='api_register'),
    path('api/login/', api_login_user, name='api_login'),
    
    # User Profile APIs
    path('api/profile/<int:user_id>/', api_user_profile, name='api_user_profile'),
    
    # Transaction APIs
    path('api/transactions/<int:user_id>/', api_transactions, name='api_transactions'),
    
    # Test Result APIs
    path('api/test-results/<int:user_id>/', api_test_results, name='api_test_results'),
    
    # User Info APIs
    path('api/user-info/<int:user_id>/', api_user_info, name='api_user_info'),
    
    # Database Stats APIs
    path('api/stats/', api_database_stats, name='api_stats'),
    
    # ============================================================================
    # USER ACTIVITY TRACKING ENDPOINTS
    # ============================================================================
    
    # Track user activities
    path('api/track-activity/', api_track_activity, name='api_track_activity'),
    
    # Record PDF purchases
    path('api/purchases/pdf/', api_record_pdf_purchase, name='api_record_pdf_purchase'),
    
    # Record mock test attempts
    path('api/attempts/mock/', api_record_mock_attempt, name='api_record_mock_attempt'),
    
    # Record quiz/interview attempts
    path('api/attempts/quiz/', api_record_quiz_attempt, name='api_record_quiz_attempt'),
    
    # Get complete user profile with activities
    path('api/user-complete-profile/<int:user_id>/', api_get_user_profile_data, name='api_get_user_profile_data'),
    
    # ============================================================================
    # END OF USER ACTIVITY TRACKING ENDPOINTS
    # ============================================================================
    
    # Company-specific friendly filenames (render test-page with proper context)
    path('tests/google/google-easy.html', views.company_test, {'company': 'google', 'difficulty': 'easy'}, name='google_easy_test'),
    path('tests/google/google-medium.html', views.company_test, {'company': 'google', 'difficulty': 'medium'}, name='google_medium_test'),
    path('tests/google/google-hard.html', views.company_test, {'company': 'google', 'difficulty': 'hard'}, name='google_hard_test'),

    path('tests/openai/openai-easy.html', views.company_test, {'company': 'openai', 'difficulty': 'easy'}, name='openai_easy_test'),
    path('tests/openai/openai-medium.html', views.company_test, {'company': 'openai', 'difficulty': 'medium'}, name='openai_medium_test'),
    path('tests/openai/openai-hard.html', views.company_test, {'company': 'openai', 'difficulty': 'hard'}, name='openai_hard_test'),

    path('tests/uber/uber-easy.html', views.company_test, {'company': 'uber', 'difficulty': 'easy'}, name='uber_easy_test'),
    path('tests/uber/uber-medium.html', views.company_test, {'company': 'uber', 'difficulty': 'medium'}, name='uber_medium_test'),
    path('tests/uber/uber-hard.html', views.company_test, {'company': 'uber', 'difficulty': 'hard'}, name='uber_hard_test'),

    path('tests/microsoft/microsoft-easy.html', views.company_test, {'company': 'microsoft', 'difficulty': 'easy'}, name='microsoft_easy_test'),
    path('tests/microsoft/microsoft-medium.html', views.company_test, {'company': 'microsoft', 'difficulty': 'medium'}, name='microsoft_medium_test'),
    path('tests/microsoft/microsoft-hard.html', views.company_test, {'company': 'microsoft', 'difficulty': 'hard'}, name='microsoft_hard_test'),

# 🔥 Dynamic catch-all route for ANY .html file 
    # Example: /company-pdfs/pdf-capgemini.html → templates/company-pdfs/pdf-capgemini.html
    re_path(r'^(?P<path>.*\.html)$', views.dynamic_html, name='dynamic_html'),
]