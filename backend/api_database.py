"""
Backend APIs for complete database operations
Provides REST API endpoints for frontend integration
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

import json
import re
from datetime import datetime
from functools import wraps

# Import database module
import sys
import os
from pathlib import Path

# Global database instance
db = None

def get_db():
    """Get or initialize database manager"""
    global db
    
    if db is not None:
        return db
    
    try:
        # Direct import using absolute path
        import importlib.util
        backend_dir = Path(__file__).resolve().parent
        db_module_path = backend_dir / 'database' / 'db.py'
        
        spec = importlib.util.spec_from_file_location("database_manager", db_module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        DatabaseManager = module.DatabaseManager
        db_path = backend_dir / 'database' / 'app.db'
        db = DatabaseManager(str(db_path))
        return db
    except Exception as import_error:
        # Fallback: Create a dummy db object to prevent import errors
        import_error_msg = str(import_error)
        class DummyDB:
            def __getattr__(self, name):
                raise RuntimeError(f"Database not initialized: {import_error_msg}")
        db = DummyDB()
        return db

# ============================================================================
# DECORATORS
# ============================================================================

def handle_exceptions(func):
    """Decorator to handle exceptions in API endpoints"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': 'Internal server error'
            }, status=500)
    return wrapper

def require_json(func):
    """Decorator to require JSON request body"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.method in ['POST', 'PUT']:
            try:
                request.json_data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON',
                    'message': 'Request body must be valid JSON'
                }, status=400)
        return func(request, *args, **kwargs)
    return wrapper

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_email_format(email):
    """Validate email format"""
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain number"
    return True, "Password is valid"

def sanitize_input(text, max_length=255):
    """Sanitize and validate input"""
    if not isinstance(text, str):
        return None
    text = text.strip()
    if len(text) > max_length:
        return text[:max_length]
    return text

# ============================================================================
# USER REGISTRATION API
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
@handle_exceptions
@require_json
def api_register_user(request):
    """
    Register a new user
    
    POST /api/register/
    
    Request body:
    {
        "email": "user@example.com",
        "username": "username",
        "password": "SecurePass123",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "9876543210"
    }
    """
    data = request.json_data
    
    # Validate required fields
    required_fields = ['email', 'username', 'password', 'first_name']
    for field in required_fields:
        if field not in data or not data[field]:
            return JsonResponse({
                'success': False,
                'error': f'Missing required field: {field}'
            }, status=400)
    
    email = sanitize_input(str(data['email'])).lower() if sanitize_input(str(data['email'])) else ''
    username = sanitize_input(str(data['username'])) or ''
    password = str(data['password'])
    first_name = sanitize_input(str(data['first_name'])) or ''
    last_name = sanitize_input(str(data.get('last_name', ''))) or ''
    phone = sanitize_input(str(data.get('phone', '')), 20) if data.get('phone') else ''
    
    # Validate inputs
    if not email or not username or not password or not first_name:
        return JsonResponse({
            'success': False,
            'error': 'Invalid input values'
        }, status=400)
    
    # Validate email
    if not validate_email_format(email):
        return JsonResponse({
            'success': False,
            'error': 'Invalid email format'
        }, status=400)
    
    # Validate password
    is_valid, msg = validate_password(password)
    if not is_valid:
        return JsonResponse({
            'success': False,
            'error': msg
        }, status=400)
    
    # Check if user already exists
    existing_user = get_db().get_user_by_email(email)
    if existing_user:
        return JsonResponse({
            'success': False,
            'error': 'Email already registered'
        }, status=409)
    
    try:
        # Hash password
        password_hash = make_password(password)
        
        # Get database instance
        database = get_db()
        
        # Create user in database
        user_id = database.create_user(
            email=email,
            username=username,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        
        if user_id:
            # Create user profile
            get_db().create_user_profile(user_id, bio='', is_premium=False)
            
            # Log activity
            get_db().log_activity(
                user_id,
                'REGISTRATION',
                'User registered successfully',
                resource_type='Auth',
                status_code=201
            )
            
            return JsonResponse({
                'success': True,
                'message': 'User registered successfully',
                'user_id': user_id,
                'email': email
            }, status=201)
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to create user'
            }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# ============================================================================
# USER LOGIN API
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
@handle_exceptions
@require_json
def api_login_user(request):
    """
    User login
    
    POST /api/login/
    
    Request body:
    {
        "email": "user@example.com",
        "password": "SecurePass123"
    }
    """
    from django.contrib.auth.models import User as AuthUser
    from django.contrib.auth import login
    
    data = request.json_data
    
    # Validate required fields
    if 'email' not in data or 'password' not in data:
        return JsonResponse({
            'success': False,
            'error': 'Missing email or password'
        }, status=400)
    
    email = sanitize_input(data['email']).lower()
    password = data['password']
    
    try:
        # Get user from custom database
        custom_user = get_db().get_user_by_email(email)
        
        if not custom_user:
            return JsonResponse({
                'success': False,
                'error': 'Invalid email or password'
            }, status=401)
        
        # Verify password
        if not check_password(password, custom_user['password_hash']):
            # Log failed attempt
            get_db().log_activity(
                custom_user['id'],
                'LOGIN_FAILED',
                'Failed login attempt',
                resource_type='Auth',
                status_code=401
            )
            
            return JsonResponse({
                'success': False,
                'error': 'Invalid email or password'
            }, status=401)
        
        # Check if user is active
        if not custom_user['is_active']:
            return JsonResponse({
                'success': False,
                'error': 'Account is inactive'
            }, status=403)
        
        # Get or create Django User for session management
        auth_user, created = AuthUser.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': custom_user.get('first_name', ''),
                'last_name': custom_user.get('last_name', '')
            }
        )
        
        # If user exists but details differ, update them
        if not created:
            auth_user.first_name = custom_user.get('first_name', '')
            auth_user.last_name = custom_user.get('last_name', '')
            auth_user.save()
        
        # Log successful login
        get_db().log_activity(
            custom_user['id'],
            'LOGIN',
            'User logged in successfully',
            resource_type='Auth',
            status_code=200
        )
        
        # Set Django session with Django User ID
        request.session['user_id'] = auth_user.id
        request.session['user_email'] = auth_user.email
        request.session.modified = True
        
        # Also login the Django user to set auth session
        login(request, auth_user)
        
        # Return user info (without password)
        user_info = {
            'id': auth_user.id,  # Django User ID for session
            'email': auth_user.email,
            'first_name': auth_user.first_name,
            'last_name': auth_user.last_name,
        }
        
        return JsonResponse({
            'success': True,
            'message': 'Login successful',
            'user': user_info
        }, status=200)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# ============================================================================
# USER PROFILE API
# ============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST", "PUT"])
@handle_exceptions
@require_json
def api_user_profile(request, user_id):
    """
    Get, create, or update user profile
    
    GET /api/profile/<user_id>/
    POST /api/profile/<user_id>/ (Create profile)
    PUT /api/profile/<user_id>/ (Update profile)
    """
    
    try:
        user = db.get_user_by_id(user_id)
        
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'User not found'
            }, status=404)
        
        if request.method == 'GET':
            # Get user profile
            profile = get_db().get_user_profile(user_id)
            
            if not profile:
                profile = {}
            
            complete_info = {
                'user': {k: v for k, v in user.items() if k != 'password_hash'},
                'profile': profile
            }
            
            return JsonResponse({
                'success': True,
                'data': complete_info
            }, status=200)
        
        elif request.method == 'POST':
            # Create profile
            data = request.json_data or {}
            
            success = get_db().create_user_profile(user_id, **data)
            
            if success:
                profile = get_db().get_user_profile(user_id)
                return JsonResponse({
                    'success': True,
                    'message': 'Profile created successfully',
                    'profile': profile
                }, status=201)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to create profile'
                }, status=400)
        
        elif request.method == 'PUT':
            # Update profile
            data = request.json_data or {}
            
            success = get_db().update_user_profile(user_id, **data)
            
            if success:
                profile = get_db().get_user_profile(user_id)
                
                # Log activity
                get_db().log_activity(
                    user_id,
                    'PROFILE_UPDATE',
                    'Updated profile information',
                    resource_type='Profile',
                    status_code=200
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Profile updated successfully',
                    'profile': profile
                }, status=200)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to update profile'
                }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# ============================================================================
# TRANSACTION API
# ============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
@handle_exceptions
@require_json
def api_transactions(request, user_id):
    """
    Get user transactions or create new transaction
    
    GET /api/transactions/<user_id>/ (Get all transactions)
    POST /api/transactions/<user_id>/ (Create transaction)
    """
    
    try:
        user = get_db().get_user_by_id(user_id)
        
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'User not found'
            }, status=404)
        
        if request.method == 'GET':
            # Get user transactions
            transactions = get_db().get_user_transactions(user_id)
            
            return JsonResponse({
                'success': True,
                'transactions': transactions,
                'count': len(transactions)
            }, status=200)
        
        elif request.method == 'POST':
            # Create transaction
            data = request.json_data or {}
            
            required_fields = ['transaction_id', 'amount']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }, status=400)
            
            success = get_db().create_transaction(
                user_id,
                data['transaction_id'],
                data['amount'],
                **{k: v for k, v in data.items() if k not in ['transaction_id', 'amount']}
            )
            
            if success:
                # Log activity
                get_db().log_activity(
                    user_id,
                    'PURCHASE',
                    f"Purchased {data.get('item_type', 'item')} for ₹{data['amount']}",
                    resource_type='Payment',
                    status_code=201
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Transaction created successfully'
                }, status=201)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to create transaction'
                }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# ============================================================================
# TEST RESULT API
# ============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
@handle_exceptions
@require_json
def api_test_results(request, user_id):
    """
    Get user test results or save new test result
    
    GET /api/test-results/<user_id>/ (Get all test results)
    POST /api/test-results/<user_id>/ (Save test result)
    """
    
    try:
        user = get_db().get_user_by_id(user_id)
        
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'User not found'
            }, status=404)
        
        if request.method == 'GET':
            # Get test results
            results = get_db().get_user_test_results(user_id)
            
            return JsonResponse({
                'success': True,
                'test_results': results,
                'count': len(results)
            }, status=200)
        
        elif request.method == 'POST':
            # Save test result
            data = request.json_data or {}
            
            if 'test_name' not in data:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing test_name'
                }, status=400)
            
            success = get_db().save_test_result(
                user_id,
                data['test_name'],
                **{k: v for k, v in data.items() if k != 'test_name'}
            )
            
            if success:
                # Log activity
                get_db().log_activity(
                    user_id,
                    'TEST_COMPLETE',
                    f"Completed {data['test_name']} - Score: {data.get('score_percent', 0)}%",
                    resource_type='Test',
                    status_code=201
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Test result saved successfully'
                }, status=201)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to save test result'
                }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# ============================================================================
# USER INFO API
# ============================================================================

@csrf_exempt
@require_http_methods(["GET"])
@handle_exceptions
def api_user_info(request, user_id):
    """
    Get complete user information
    
    GET /api/user-info/<user_id>/
    """
    
    try:
        complete_info = get_db().get_user_complete_info(user_id)
        
        if not complete_info:
            return JsonResponse({
                'success': False,
                'error': 'User not found'
            }, status=404)
        
        # Remove password hash
        complete_info['user'] = {
            k: v for k, v in complete_info['user'].items() 
            if k != 'password_hash'
        }
        
        return JsonResponse({
            'success': True,
            'data': complete_info
        }, status=200)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# ============================================================================
# DATABASE STATS API
# ============================================================================

@csrf_exempt
@require_http_methods(["GET"])
@handle_exceptions
def api_database_stats(request):
    """
    Get database statistics
    
    GET /api/stats/
    """
    
    try:
        stats = get_db().get_database_stats()
        
        return JsonResponse({
            'success': True,
            'stats': stats
        }, status=200)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
# ============================================================================
# USER ACTIVITY TRACKING ENDPOINTS
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
@handle_exceptions
@require_json
def api_track_activity(request):
    """
    Track user activity (login, PDF purchase, test attempt, etc.)
    
    POST /api/track-activity/
    
    Request body:
    {
        "userId": 1,
        "activityType": "pdf_purchase|mock_attempt|quiz_complete|login|logout",
        "title": "Activity Title",
        "description": "Activity Description",
        "data": { extra data like score, amount, etc. }
    }
    """
    from accounts.models import UserActivity
    
    data = request.json_data
    
    # Validate required fields
    if 'userId' not in data or 'activityType' not in data:
        return JsonResponse({
            'success': False,
            'error': 'Missing userId or activityType'
        }, status=400)
    
    try:
        user = DjangoUser.objects.get(id=data['userId'])
        
        # Create activity record
        activity = UserActivity.objects.create(
            user=user,
            activity_type=data['activityType'],
            title=data.get('title', ''),
            description=data.get('description', ''),
            data=data.get('data', {})
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Activity tracked: {data["activityType"]}',
            'activity': activity.as_dict()
        }, status=201)
    
    except DjangoUser.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@handle_exceptions
@require_json
def api_record_pdf_purchase(request):
    """
    Record PDF purchase
    
    POST /api/purchases/pdf/
    
    Request body:
    {
        "userId": 1,
        "pdfId": 5,
        "pdfTitle": "PDF Title",
        "company": "Company Name",
        "amount": 199
    }
    """
    from accounts.models import UserActivity, PurchasedItem
    
    data = request.json_data
    
    # Validate required fields
    if 'userId' not in data or 'pdfTitle' not in data:
        return JsonResponse({
            'success': False,
            'error': 'Missing userId or pdfTitle'
        }, status=400)
    
    try:
        user = DjangoUser.objects.get(id=data['userId'])
        
        # Create purchased item record
        purchased = PurchasedItem.objects.create(
            user=user,
            title=data.get('pdfTitle'),
            item_type='pdf',
            amount_paid=data.get('amount', 0),
            transaction_id=data.get('transactionId', '')
        )
        
        # Track activity
        UserActivity.objects.create(
            user=user,
            activity_type='pdf_purchase',
            title=f"Purchased: {data.get('pdfTitle')}",
            description=f"Company: {data.get('company', 'N/A')}",
            data={
                'pdfId': data.get('pdfId'),
                'company': data.get('company'),
                'amount': data.get('amount', 0),
                'transactionId': data.get('transactionId')
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'PDF purchase recorded',
            'purchase': purchased.as_dict()
        }, status=201)
    
    except DjangoUser.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@handle_exceptions
@require_json
def api_record_mock_attempt(request):
    """
    Record mock test attempt
    
    POST /api/attempts/mock/
    
    Request body:
    {
        "userId": 1,
        "mockId": 3,
        "mockTitle": "Mock Test Title",
        "score": 75,
        "totalQuestions": 100,
        "correctAnswers": 75,
        "duration": 30
    }
    """
    from accounts.models import UserActivity, AttemptedMock, Mock
    
    data = request.json_data
    
    # Validate required fields
    required = ['userId', 'mockTitle', 'score']
    for field in required:
        if field not in data:
            return JsonResponse({
                'success': False,
                'error': f'Missing {field}'
            }, status=400)
    
    try:
        user = DjangoUser.objects.get(id=data['userId'])
        
        # Try to get mock object if mockId is provided
        mock = None
        if 'mockId' in data and data['mockId']:
            try:
                mock = Mock.objects.get(id=data['mockId'])
            except Mock.DoesNotExist:
                pass
        
        # Create attempted mock record (if mock exists)
        attempt_record = None
        if mock:
            attempt_record = AttemptedMock.objects.create(
                user=user,
                mock=mock,
                score=data['score']
            )
        
        # Track activity
        UserActivity.objects.create(
            user=user,
            activity_type='mock_complete',
            title=f"Completed: {data.get('mockTitle')}",
            description=f"Score: {data['score']}/{data.get('totalQuestions', '?')}",
            data={
                'mockId': data.get('mockId'),
                'mockTitle': data.get('mockTitle'),
                'score': data['score'],
                'totalQuestions': data.get('totalQuestions'),
                'correctAnswers': data.get('correctAnswers'),
                'percentage': (data['score'] / data.get('totalQuestions', 1) * 100) if data.get('totalQuestions') else 0
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Mock test attempt recorded',
            'score': data['score'],
            'timestamp': data.get('timestamp', '')
        }, status=201)
    
    except DjangoUser.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@handle_exceptions
@require_json
def api_record_quiz_attempt(request):
    """
    Record quiz/interview attempt
    
    POST /api/attempts/quiz/
    
    Request body:
    {
        "userId": 1,
        "quizId": "hr-questions",
        "quizTitle": "HR Questions Quiz",
        "quizType": "hr|technical|aptitude",
        "score": 8,
        "totalQuestions": 10,
        "correctAnswers": 8
    }
    """
    from accounts.models import UserActivity
    
    data = request.json_data
    
    # Validate required fields
    required = ['userId', 'quizTitle', 'score']
    for field in required:
        if field not in data:
            return JsonResponse({
                'success': False,
                'error': f'Missing {field}'
            }, status=400)
    
    try:
        user = DjangoUser.objects.get(id=data['userId'])
        
        # Determine activity type based on quiz type
        quiz_type = data.get('quizType', 'technical').lower()
        activity_type = f'quiz_complete'
        
        # Track activity
        activity = UserActivity.objects.create(
            user=user,
            activity_type=activity_type,
            title=f"Completed: {data.get('quizTitle')}",
            description=f"Score: {data['score']}/{data.get('totalQuestions', '?')} ({data.get('quizType', 'Quiz')})",
            data={
                'quizId': data.get('quizId'),
                'quizTitle': data.get('quizTitle'),
                'quizType': data.get('quizType'),
                'score': data['score'],
                'totalQuestions': data.get('totalQuestions'),
                'correctAnswers': data.get('correctAnswers'),
                'percentage': (data['score'] / data.get('totalQuestions', 1) * 100) if data.get('totalQuestions') else 0
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{data.get("quizType", "Quiz")} attempt recorded',
            'activity': activity.as_dict()
        }, status=201)
    
    except DjangoUser.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
@handle_exceptions
def api_get_user_profile_data(request, user_id):
    """
    Get complete user profile with all activities
    
    GET /api/user-complete-profile/<user_id>/
    """
    from accounts.models import UserActivity, PurchasedItem, AttemptedMock
    
    try:
        user = DjangoUser.objects.get(id=user_id)
        
        # Get all activities
        activities = UserActivity.objects.filter(user=user).order_by('-created_at')[:50]
        
        # Get purchases
        purchases = PurchasedItem.objects.filter(user=user).order_by('-purchased_at')
        
        # Get mock attempts
        attempts = AttemptedMock.objects.filter(user=user).order_by('-attempt_date')
        
        # Calculate statistics
        total_purchases = purchases.count()
        total_mock_attempts = attempts.count()
        total_activities = activities.count()
        
        avg_mock_score = 0
        if total_mock_attempts > 0:
            avg_mock_score = sum([a.score for a in attempts]) / total_mock_attempts
        
        return JsonResponse({
            'success': True,
            'profile': {
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'firstName': user.first_name,
                    'lastName': user.last_name,
                    'username': user.username,
                    'joinedDate': user.date_joined.isoformat()
                },
                'statistics': {
                    'totalPurchases': total_purchases,
                    'totalMockAttempts': total_mock_attempts,
                    'totalActivities': total_activities,
                    'averageMockScore': round(avg_mock_score, 2)
                },
                'activities': [activity.as_dict() for activity in activities],
                'purchases': [purchase.as_dict() for purchase in purchases],
                'mockAttempts': [attempt.as_dict() for attempt in attempts]
            }
        }, status=200)
    
    except DjangoUser.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)