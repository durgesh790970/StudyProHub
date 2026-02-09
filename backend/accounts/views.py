"""
Views for the accounts app.

This module implements API endpoints and template views:
- Template views: home, login_page, dashboard
- API endpoints: send_otp, verify_otp, me, list_videos, list_pdfs, mark_paid

Important: This demo returns OTP codes in responses for easy testing. Remove
that behavior when moving to production.
"""
import json
import random
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.template import TemplateDoesNotExist  # 👈 ADD THIS LINE
from .models import OTP, User, Video, PDF
from .email_utils import send_result_email
from django.http import Http404
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User as AuthUser

from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

def signup_page(request):
    if request.method == "POST":
        fullname = request.POST['fullname']
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['confirmPassword']

        if password != cpassword:
            messages.error(request,"Passwords do not match!")
            return redirect('accounts:signup_page')

        # ✅ User को Django auth में create करो
        auth_user = User.objects.create_user(username=email, email=email, password=password, first_name=fullname)
        
        # ✅ UserProfile में data save करो automatically
        from .models import UserProfile
        UserProfile.objects.create(auth_user=auth_user)
        
        messages.success(request,"Account Created Successfully! Please Login.")
        return redirect('accounts:login_page')
    

    return render(request, "signup.html")


def login_page(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {user.first_name}!")
            return redirect('accounts:dashboard')  # Change your URL here
        else:
            messages.error(request, "Invalid Email or Password!")
            return redirect('accounts:login_page')

    return render(request, "login.html")


from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

def dashboard(request):
    return render(request, 'dashboard.html')


def profile(request):
    """Render a profile page showing user details and purchases.

    Supports two login methods used in this project:
    - OTP/phone: session['phone'] -> accounts.models.User
    - Email/password: session['user_id'] -> django.contrib.auth.models.User
    """
    phone = request.session.get('phone')
    uid = request.session.get('user_id')

    if not (phone or uid):
        return redirect('accounts:login_page')

    # Default context
    context = {'purchases': [], 'transactions': [], 'purchased_items': [], 'test_results': []}

    if phone:
        try:
            acct_user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return redirect('accounts:login_page')
        # purchases stored in paid_companies JSONField
        purchases = list((acct_user.paid_companies or {}).keys())
        # transactions related to this accounts.User
        from .models import Transaction, PDF, PurchasedItem, TestResult
        txs = Transaction.objects.filter(user=acct_user).order_by('-created_at')
        # Get purchased items from database
        purchased_items = list(PurchasedItem.objects.filter(user=acct_user).order_by('-purchased_at'))
        # Get test results from database
        test_results = list(TestResult.objects.filter(user=acct_user).order_by('-attempt_date'))
        # also derive purchased PDF objects (by company key)
        purchased_pdfs = []
        if purchases:
            purchased_pdfs = list(PDF.objects.filter(company__in=purchases).order_by('-created_at'))
        context.update({'user_obj': acct_user, 'purchases': purchases, 'transactions': txs, 'purchased_pdfs': purchased_pdfs, 'purchased_items': purchased_items, 'test_results': test_results, 'profile_user_id': getattr(acct_user, 'id', None)})
    else:
        # email/password user
        try:
            auth_user = AuthUser.objects.get(pk=uid)
        except AuthUser.DoesNotExist:
            return redirect('accounts:login_page')
        # try to find or create linked accounts.User to surface purchases
        from .models import User as AccountUser, Transaction, PDF, PurchasedItem, TestResult
        acct_user = None
        try:
            acct_user = AccountUser.objects.filter(auth_user=auth_user).first()
        except Exception:
            acct_user = None

        purchased_pdfs = []
        txs = []
        purchased_items = []
        test_results = []
        if acct_user:
            purchases = list((acct_user.paid_companies or {}).keys())
            if purchases:
                purchased_pdfs = list(PDF.objects.filter(company__in=purchases).order_by('-created_at'))
            txs = list(Transaction.objects.filter(user=acct_user).order_by('-created_at'))
            # Get purchased items from database
            purchased_items = list(PurchasedItem.objects.filter(user=acct_user).order_by('-purchased_at'))
            # Get test results from database
            test_results = list(TestResult.objects.filter(user=acct_user).order_by('-attempt_date'))

        # if we have a linked AccountUser, expose its id for realtime/profile API
        linked_id = getattr(acct_user, 'id', None) if acct_user else None
        context.update({'user_obj': auth_user, 'email_user': True, 'purchased_pdfs': purchased_pdfs, 'transactions': txs, 'purchased_items': purchased_items, 'test_results': test_results, 'profile_user_id': linked_id})

    return render(request, 'accounts/profile.html', context)



@csrf_exempt
def get_user_email(request):
    """API endpoint: Get logged-in user's email.
    
    Returns:
    {
        "ok": true,
        "email": "user@example.com",
        "name": "John Doe"
    }
    or
    {
        "ok": false,
        "error": "not_authenticated"
    }
    """
    # Check Django session auth first
    if request.user.is_authenticated:
        return JsonResponse({
            'ok': True,
            'email': request.user.email,
            'name': request.user.first_name or request.user.username
        })
    
    # Check for phone-based auth in session
    phone = request.session.get('phone')
    if phone:
        try:
            acct_user = User.objects.get(phone=phone)
            return JsonResponse({
                'ok': True,
                'email': acct_user.email or '',
                'name': acct_user.name or 'User'
            })
        except User.DoesNotExist:
            pass
    
    return JsonResponse({
        'ok': False,
        'error': 'not_authenticated'
    }, status=401)


def logout_page(request):
    request.session.flush()
    return redirect("accounts:login_page")



def _generate_code():
    """Generate a 6-digit OTP code."""
    return f"{random.randint(0, 999999):06d}"


def home(request):
    """Render the home page with featured companies from PDFs."""
    # Get unique company names from PDFs to show in the featured section
    featured_companies = (
        PDF.objects.exclude(company='')
        .values_list('company', flat=True)
        .distinct()
        .order_by('company')[:4]  # Limit to 4 featured companies
    )
    # Render the existing index.html template located under accounts/templates/
    # (TEMPLATES['DIRS'] already includes this path in settings)
    return render(request, 'index.html', {
        'featured_companies': featured_companies
    })
    

def index(request):
    return render(request, 'index.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def videos_page(request):
    return render(request, 'videos.html')

def pdfs_page(request):
    return render(request, 'pdfs.html')

def quiz_page(request):
    return render(request, 'quiz.html')

def BTech_page(request):
    return render(request, 'BTech.html')

def interview_page(request):
    return render(request, 'Interview.html')


def contect_page(request):
    return render(request, 'contect.html')

def login_page(request):
    return render(request, 'login.html')

def signup_page(request):
    # Handle email/password signup
    if request.method == 'POST' and request.POST.get('email'):
        fullname = request.POST.get('fullname', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirmPassword', '')

        if not (fullname and email and password and confirm):
            messages.error(request, 'All fields are required')
            return render(request, 'accounts/signup.html')

        if password != confirm:
            messages.error(request, 'Passwords do not match')
            return render(request, 'accounts/signup.html')

        # Check existing user by email
        if AuthUser.objects.filter(email__iexact=email).exists():
            messages.error(request, 'An account with that email already exists')
            return render(request, 'accounts/signup.html')

        # Create Django auth user (username stored as email)
        user = AuthUser.objects.create_user(username=email, email=email)
        user.first_name = fullname
        user.set_password(password)
        user.save()

        # No need to link to accounts.User - PurchasedItem and TestResult use django.contrib.auth.User directly
        # The email-based user is now fully integrated with Django's auth.User model

        # store user id in session per project convention
        try:
            request.session['user_id'] = user.id
        except Exception:
            pass

        messages.success(request, 'Account created — logged in')
        return redirect('accounts:dashboard')

    return render(request, 'accounts/signup.html')


def dashboard(request):
    """Render the dashboard; attempt to lookup user by session phone.

    The template contains JS which calls API endpoints to fetch videos/pdfs.
    """
    phone = request.session.get('phone')
    user = None
    if phone:
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            user = None

    return render(request, 'accounts/dashboard.html', {'user': user})

    
from django.http import Http404
from django.shortcuts import render

def dynamic_html(request, path):
    """
    Dynamically render any .html file from templates folder.
    Example:
        /company-pdfs/pdf-capgemini.html → templates/company-pdfs/pdf-capgemini.html
    """
    try:
        return render(request, path)
    except Exception:
        raise Http404(f"Template not found: {path}")
  
    
@csrf_exempt
def send_otp(request):
    """API: send an OTP to a phone number (demo).

    Request (POST JSON): { "phone": "+911234..." }
    Response (JSON): { "ok": true, "debug_code": "1234" }

    In production this should trigger an SMS provider and NOT return the code.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')

    try:
        payload = json.loads(request.body)
        phone = payload.get('phone')
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    if not phone:
        return HttpResponseBadRequest('phone required')

    code = _generate_code()
    OTP.objects.create(phone=phone, code=code)

    # DEBUG: return the code in response so testers can auto-fill it.
    return JsonResponse({'ok': True, 'debug_code': code})


@csrf_exempt
def verify_otp(request):
    """API: verify OTP. If valid, create User (if not exists) and set session.

    Request (POST JSON): { "phone": "+91...", "code": "1234" }
    Response: { "ok": True, "phone": "+91..." }
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    try:
        payload = json.loads(request.body)
        phone = payload.get('phone')
        code = payload.get('code')
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    if not phone or not code:
        return HttpResponseBadRequest('phone and code required')

    # find the latest OTP for this phone
    otp_qs = OTP.objects.filter(phone=phone).order_by('-created_at')
    if not otp_qs.exists():
        return JsonResponse({'ok': False, 'error': 'No OTP found'}, status=400)

    otp = otp_qs.first()
    if otp.is_expired() or otp.code != code:
        return JsonResponse({'ok': False, 'error': 'Invalid or expired code'}, status=400)

    # create user if necessary
    user, created = User.objects.get_or_create(phone=phone)

    # store phone in session so template views can use it
    request.session['phone'] = phone

    return JsonResponse({'ok': True, 'phone': phone})


def me(request):
    """Return current user info based on session phone (if any)."""
    phone = request.session.get('phone')
    if not phone:
        return JsonResponse({'ok': False, 'error': 'not_logged_in'}, status=401)

    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'user_not_found'}, status=404)

    return JsonResponse({'ok': True, 'user': {
        'phone': user.phone,
        'has_paid': user.has_paid,
        'paid_companies': user.paid_companies,
    }})


def list_videos(request):
    """Return JSON list of videos (title + youtube_id)."""
    videos = Video.objects.all().order_by('-created_at')
    data = [{'id': v.id, 'title': v.title, 'youtube_id': v.youtube_id, 'thumbnail': v.thumbnail_url()} for v in videos]
    return JsonResponse({'ok': True, 'videos': data})


def list_pdfs(request):
    """Return JSON list of PDFs; optional `company` query param to filter."""
    company = request.GET.get('company')
    qs = PDF.objects.all().order_by('-created_at')
    if company:
        qs = qs.filter(company__iexact=company)
    data = [{'id': p.id, 'company': p.company, 'title': p.title, 'file_url': p.file_url} for p in qs]
    return JsonResponse({'ok': True, 'pdfs': data})


@csrf_exempt
def submit_test(request):
    """API endpoint: Receive test submission and send result email.

    Expects JSON payload with fields:
      - email (required)
      - company, difficulty
      - total_questions, answered, correct, wrong, percentage
      - time_remaining
      - answers (optional)
      - name (optional)
      - rank (optional)
      - feedback (optional)
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')

    try:
        payload = json.loads(request.body)
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    email = payload.get('email')
    if not email:
        return JsonResponse({'ok': False, 'error': 'email required'}, status=400)

    name = payload.get('name') or None
    company = payload.get('company') or ''
    difficulty = payload.get('difficulty') or ''
    test_name = f"{company.title()} - {difficulty.title()}" if company else payload.get('test_name') or 'StudyPro Test'
    total = payload.get('total_questions') or payload.get('total') or 0
    score = payload.get('correct') or 0
    percentage = payload.get('percentage') or 0
    time_remaining = payload.get('time_remaining') or None
    rank = payload.get('rank') or 'N/A'
    feedback = payload.get('feedback') or ''

    # Compute time_taken if possible
    time_taken = payload.get('time_taken')
    if not time_taken and isinstance(time_remaining, (int, float)):
        try:
            # If client sends time_limit too, prefer that; otherwise return remaining seconds
            time_limit = payload.get('time_limit')
            if time_limit:
                taken_seconds = int(time_limit) - int(time_remaining)
                # format minutes:seconds
                mins = taken_seconds // 60
                secs = taken_seconds % 60
                time_taken = f"{mins}m {secs}s"
            else:
                time_taken = f"{int(time_remaining)}s remaining"
        except Exception:
            time_taken = str(time_remaining)

    # If no feedback, generate one based on percentage
    if not feedback:
        try:
            p = float(percentage)
            if p >= 85:
                feedback = 'Excellent performance. Keep up the great work!'
            elif p >= 70:
                feedback = 'Good job — a few adjustments and you will be great.'
            elif p >= 50:
                feedback = 'Fair attempt. Focus on weak areas and practice more.'
            else:
                feedback = 'Keep practicing — try shorter, focused practice sessions.'
        except Exception:
            feedback = ''

    # Call the email sender
    email_sent = False
    try:
        email_sent = send_result_email(email=email, name=name, test_name=test_name, score=score, total=total, accuracy=percentage, time_taken=time_taken, rank=rank, feedback=feedback)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

    # Auto-save result to database and user profile if authenticated
    auto_saved = False
    db_saved = False
    try:
        # Try to get user by email first
        user = None
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            if request.user.is_authenticated:
                user = request.user
        
        if user:
            # Save to TestResult database table
            from .models import TestResult
            test_result = TestResult.objects.create(
                user=user,
                test_name=test_name,
                company=company,
                difficulty=difficulty,
                total_questions=total,
                correct_answers=score,
                score=percentage,
                time_taken=time_taken,
                attempt_date=timezone.now()
            )
            db_saved = True
            
            # Also save to JSONField for backward compatibility
            result_obj = {
                'email': email,
                'name': name,
                'company': company,
                'difficulty': difficulty,
                'test_name': test_name,
                'correct': score,
                'total_questions': total,
                'percentage': percentage,
                'time_taken': time_taken,
                'rank': rank,
                'feedback': feedback,
                'timestamp': payload.get('timestamp') or timezone.now().isoformat()
            }
            
            # Initialize test_results if needed
            if not user.test_results:
                user.test_results = []
            
            # Add result to user's test_results
            user.test_results.append(result_obj)
            user.save()
            auto_saved = True
            
    except Exception as e:
        print(f"Error auto-saving result: {e}")
        # Don't fail the submission if auto-save fails

    return JsonResponse({
        'ok': True,
        'message': 'result submitted',
        'email_sent': bool(email_sent),
        'auto_saved': auto_saved,
        'db_saved': db_saved
    })



def save_test_result(request):
    """API endpoint: Save test result to user profile and database.
    
    Expects JSON with test result data:
      - email, company, difficulty, score, total, percentage, timestamp, etc.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')

    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'error': 'not_authenticated'}, status=401)

    try:
        payload = json.loads(request.body)
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    email = payload.get('email')
    if not email:
        return JsonResponse({'ok': False, 'error': 'email required'}, status=400)

    # Get or create user by email
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Try to get from authenticated session
        if request.user.is_authenticated:
            user = request.user
        else:
            return JsonResponse({'ok': False, 'error': 'user_not_found'}, status=404)

    # Add timestamp if not present
    if 'timestamp' not in payload:
        payload['timestamp'] = timezone.now().isoformat()

    # Extract test data for database storage
    test_name = payload.get('test_name', 'Test')
    company = payload.get('company', '')
    difficulty = payload.get('difficulty', '')
    total_questions = payload.get('total_questions') or payload.get('total', 0)
    correct_answers = payload.get('correct') or payload.get('score', 0)
    score_percent = payload.get('percentage') or 0
    time_taken = payload.get('time_taken', '')

    # Save to TestResult database table
    from .models import TestResult
    try:
        TestResult.objects.create(
            user=user,
            test_name=test_name,
            company=company,
            difficulty=difficulty,
            total_questions=total_questions,
            correct_answers=correct_answers,
            score=score_percent,
            time_taken=time_taken,
            attempt_date=timezone.now()
        )
    except Exception as e:
        print(f"Error saving to TestResult table: {e}")

    # Also save to JSONField for backward compatibility
    # Initialize test_results if needed
    if not user.test_results:
        user.test_results = []

    # Add new result to array
    user.test_results.append(payload)
    user.save()

    return JsonResponse({'ok': True, 'message': 'result saved', 'count': len(user.test_results)})



def delete_test_result(request):
    """API endpoint: Delete test result from user profile and database.
    
    Expects JSON with:
      - result_id (database ID) OR timestamp (legacy support)
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')

    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'error': 'not_authenticated'}, status=401)

    try:
        payload = json.loads(request.body)
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    result_id = payload.get('result_id')
    timestamp = payload.get('timestamp')
    
    if not (result_id or timestamp):
        return JsonResponse({'ok': False, 'error': 'result_id or timestamp required'}, status=400)

    user = request.user
    
    # Delete from database if result_id provided
    if result_id:
        try:
            from .models import TestResult
            test_result = TestResult.objects.get(pk=result_id, user=user)
            test_result.delete()
        except TestResult.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'result_not_found'}, status=404)
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)

    # Also delete from JSONField for backward compatibility
    if user.test_results:
        original_count = len(user.test_results)
        user.test_results = [r for r in user.test_results if r.get('timestamp') != timestamp] if timestamp else user.test_results
        
        if len(user.test_results) < original_count:
            user.save()

    return JsonResponse({'ok': True, 'message': 'result deleted'})


@csrf_exempt
def mark_paid(request):
    """Demo endpoint to mark a user as paid.

    Accepts POST JSON:
      { "phone": "+91...", "type": "video" }
      { "phone": "+91...", "type": "pdf", "company": "Acme" }

    In production, this update should be triggered only after verifying
    a payment provider webhook (server-to-server).
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')

    try:
        payload = json.loads(request.body)
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    phone = payload.get('phone') or request.session.get('phone')
    if not phone:
        return JsonResponse({'ok': False, 'error': 'phone required'}, status=400)

    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'user_not_found'}, status=404)

    t = payload.get('type')
    if t == 'video':
        user.has_paid = True
        user.save()
        return JsonResponse({'ok': True, 'message': 'marked has_paid'})
    elif t == 'pdf':
        company = payload.get('company')
        if not company:
            return HttpResponseBadRequest('company required for pdf type')
        paid = user.paid_companies or {}
        paid[company] = True
        user.paid_companies = paid
        user.save()
        return JsonResponse({'ok': True, 'message': f'marked paid for {company}'})
    else:
        return HttpResponseBadRequest('unknown type')
"""Basic API views for demo OTP login and user management.

Endpoints:
- POST /api/send_otp/  { phone }
- POST /api/verify_otp/ { phone, code }
- GET  /api/me/  (optional: ?phone=...)

This is a minimal demo; in production replace SMS/OTP service and add
proper authentication tokens (JWT/session) and rate limiting.
"""
import json
import random
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .models import OTP, User
from django.utils import timezone


def _generate_code():
    return f"{random.randint(0, 999999):06d}"


@csrf_exempt
@require_POST
def send_otp(request):
    """Receive a phone number and create an OTP entry.

    Request JSON: { "phone": "9123456789" }
    Response: { ok: true }
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        phone = data.get('phone')
        if not phone:
            return JsonResponse({'ok': False, 'error': 'phone required'}, status=400)

        code = _generate_code()
        # store OTP in DB (demo). In real app use ephemeral cache or external provider.
        OTP.objects.create(phone=phone, code=code)

        # In demo we return code for convenience; remove this in production
        return JsonResponse({'ok': True, 'debug_code': code})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


def logout_user(request):
    """Logout helper used by templates/urls: clear session and redirect to login."""
    try:
        request.session.flush()
    except Exception:
        pass
    return redirect('accounts:login_page')


@csrf_exempt
@require_POST
def verify_otp(request):
    """Verify OTP and create/get user.

    Request JSON: { "phone": "9123456789", "code": "123456" }
    Response: { ok: true, user: { id, phone, has_paid, paid_companies } }
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        phone = data.get('phone')
        code = data.get('code')
        if not (phone and code):
            return JsonResponse({'ok': False, 'error': 'phone and code required'}, status=400)

        # Find latest OTP for phone
        otps = OTP.objects.filter(phone=phone).order_by('-created_at')
        if not otps.exists():
            return JsonResponse({'ok': False, 'error': 'OTP not found'}, status=400)

        otp = otps.first()
        if otp.is_expired():
            return JsonResponse({'ok': False, 'error': 'OTP expired'}, status=400)

        if otp.code != code:
            return JsonResponse({'ok': False, 'error': 'Invalid code'}, status=400)

        # Create or get user
        user, created = User.objects.get_or_create(phone=phone)

        # Set a simple session value so template views can identify logged-in user
        try:
            request.session['phone'] = user.phone
        except Exception:
            # If sessions aren't configured, we still return the user JSON
            pass

        # Simple success response. In production return a token (JWT) or set secure session.
        return JsonResponse({'ok': True, 'user': {
            'id': str(user.id),
            'phone': user.phone,
            'has_paid': user.has_paid,
            'paid_companies': user.paid_companies,
        }})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


@require_GET
def me(request):
    """Get user info by phone query param (demo). In real app, use auth.

    GET /api/me/?phone=9123456789
    """
    phone = request.GET.get('phone')
    if not phone:
        return JsonResponse({'ok': False, 'error': 'phone query param required'}, status=400)
    try:
        user = User.objects.get(phone=phone)
        return JsonResponse({'ok': True, 'user': {
            'id': str(user.id),
            'phone': user.phone,
            'has_paid': user.has_paid,
            'paid_companies': user.paid_companies,
        }})
    except User.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'user not found'}, status=404)


def list_videos(request):
    """Return a JSON list of videos."""
    vids = []
    try:
        videos = __import__('accounts.models', fromlist=['Video']).Video.objects.all().order_by('-created_at')
        for v in videos:
            vids.append({
                'id': str(v.id),
                'title': v.title,
                'description': v.description,
                'videoId': v.video_id,
                'createdAt': v.created_at.isoformat(),
            })
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

    return JsonResponse({'ok': True, 'videos': vids})


def list_pdfs(request):
    """Return PDFs; optional filter by company via ?company=capgemini"""
    company = request.GET.get('company')
    pdfs = []
    try:
        PDF = __import__('accounts.models', fromlist=['PDF']).PDF
        qs = PDF.objects.all().order_by('-created_at')
        if company:
            qs = qs.filter(company=company)
        for p in qs:
            pdfs.append({
                'id': str(p.id),
                'title': p.title,
                'description': p.description,
                'url': p.url,
                'company': p.company,
                'createdAt': p.created_at.isoformat(),
            })
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

    return JsonResponse({'ok': True, 'pdfs': pdfs})


def pdf_download(request, pk):
    """Protected download: allow only users who purchased the PDF's company or have general paid access."""
    try:
        pdf = PDF.objects.get(pk=pk)
    except PDF.DoesNotExist:
        return Http404('PDF not found')

    # Find current accounts.User either via phone session or linked auth_user
    acct_user = None
    phone = request.session.get('phone')
    uid = request.session.get('user_id')
    if phone:
        try:
            acct_user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            acct_user = None
    elif uid:
        try:
            auth_user = AuthUser.objects.get(pk=uid)
            acct_user = User.objects.filter(auth_user=auth_user).first()
        except Exception:
            acct_user = None

    # Check access: either has_paid OR company in paid_companies
    allowed = False
    if acct_user:
        if acct_user.has_paid:
            allowed = True
        else:
            paid = acct_user.paid_companies or {}
            if pdf.company and paid.get(pdf.company):
                allowed = True

    if allowed:
        # safe redirect to actual URL (could be local file or external link)
        return redirect(pdf.url)
    else:
        return HttpResponseForbidden('You do not have access to this PDF')


def login_page(request):
    """Render login template and handle email/password POST.

    - If POST contains 'email' handle email/password auth and store
      `request.session['user_id'] = user.id` on success.
    - Otherwise preserve existing OTP flow: if phone in session redirect.
    """
    # If already logged in via phone or user_id, redirect to dashboard
    if request.session.get('phone') or request.session.get('user_id'):
        return redirect('accounts:dashboard')

    # Handle email/password login submission
    if request.method == 'POST' and request.POST.get('email'):
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        if not (email and password):
            messages.error(request, 'Please enter email and password')
            return render(request, 'accounts/login.html', {})

        try:
            auth_user = AuthUser.objects.get(email__iexact=email)
        except AuthUser.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'accounts/login.html', {})

        user = authenticate(request, username=auth_user.username, password=password)
        if user is not None:
            # Successful login: store user id in session and redirect
            request.session['user_id'] = user.id
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid email or password')
            return render(request, 'accounts/login.html', {})

    # Default: render login form (OTP flow still available in JS)
    return render(request, 'accounts/login.html', {})


def logout_page(request):
    """Logout by clearing the session and redirecting to login."""
    try:
        request.session.flush()
    except Exception:
        pass
    return redirect('accounts:login_page')


def dashboard(request):
    """Render dashboard showing videos and companies.

    Require login either via `phone` (legacy OTP) or `user_id` (email/password).
    """
    phone = request.session.get('phone')
    auth_user = None
    if not (phone or request.session.get('user_id')):
        return redirect('accounts:login_page')

    user = None
    if phone:
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return redirect('accounts:login_page')
    else:
        # email/password logged in user
        uid = request.session.get('user_id')
        try:
            auth_user = AuthUser.objects.get(pk=uid)
            # expose fullname property expected by templates
            setattr(auth_user, 'fullname', auth_user.first_name or auth_user.get_full_name())
            user = auth_user
        except AuthUser.DoesNotExist:
            return redirect('accounts:login_page')

    # Load videos and companies
    Video = __import__('accounts.models', fromlist=['Video']).Video
    PDF = __import__('accounts.models', fromlist=['PDF']).PDF

    videos = Video.objects.all().order_by('-created_at')
    pdfs = PDF.objects.all().order_by('-created_at')

    # derive unique company list
    companies = sorted(list({p.company for p in pdfs if p.company}))

    context = {
        'user': user,
        'videos': videos,
        'companies': companies,
    }
    return render(request, 'accounts/dashboard.html', context)


@csrf_exempt
@require_POST
def mark_paid(request):
    """Mark payment for the current session user.

    POST body JSON: { "type": "video" }  OR { "type": "pdf", "company": "capgemini" }

    For demo we accept the client confirmation and update the User document.
    In production, update after verifying webhook from PhonePe.
    """
    try:
        phone = request.session.get('phone')
        if not phone:
            return JsonResponse({'ok': False, 'error': 'not logged in'}, status=401)

        data = json.loads(request.body.decode('utf-8'))
        typ = data.get('type')
        user = User.objects.get(phone=phone)

        if typ == 'video':
            user.has_paid = True
            user.save()
            return JsonResponse({'ok': True, 'message': 'video access granted'})
        elif typ == 'pdf':
            company = data.get('company')
            if not company:
                return JsonResponse({'ok': False, 'error': 'company required'}, status=400)
            pc = user.paid_companies or {}
            pc[company] = True
            user.paid_companies = pc
            user.save()
            return JsonResponse({'ok': True, 'message': f'pdf access granted for {company}'})
        else:
            return JsonResponse({'ok': False, 'error': 'invalid type'}, status=400)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


# ==========================================
# TEST FLOW VIEWS
# ==========================================

def select_difficulty(request):
    """
    Display difficulty selection page for test.
    User can choose Easy, Medium, or Hard.
    """
    context = {
        'page_title': 'Select Difficulty Level',
    }
    return render(request, 'select-difficulty.html', context)


def test_instructions(request):
    """
    Display test instructions page.
    Shows test details, rules, and warning before starting.
    """
    difficulty = request.GET.get('difficulty', 'medium')
    
    # Validate difficulty
    valid_difficulties = ['easy', 'medium', 'hard']
    if difficulty not in valid_difficulties:
        difficulty = 'medium'
    
    context = {
        'page_title': 'Test Instructions',
        'difficulty': difficulty,
        'test_config': {
            'total_questions': 20,
            'max_marks': 100,
            'marks_per_question': 5,
            'negative_marking': False,
            'time_limit': 30,  # minutes
            'passing_marks': 60,
        }
    }
    return render(request, 'instructions.html', context)


def test_page(request):
    """
    Display the main test-taking page.
    Loads questions via JavaScript from the API.
    Validates company and difficulty parameters.
    """
    company = request.GET.get('company', 'google')
    difficulty = request.GET.get('difficulty', 'medium')
    
    # Validate company
    valid_companies = ['google', 'openai', 'uber', 'microsoft']
    if company not in valid_companies:
        company = 'google'
    
    # Validate difficulty
    valid_difficulties = ['easy', 'medium', 'hard']
    if difficulty not in valid_difficulties:
        difficulty = 'medium'
    
    context = {
        'page_title': 'Interview Test',
        'company': company,
        'difficulty': difficulty,
        'test_config': {
            'total_questions': 20,
            'max_marks': 100,
            'marks_per_question': 5,
            'time_limit': 1800,  # 30 minutes in seconds
        }
    }
    return render(request, 'test-page.html', context)


def test_result(request):
    """
    Display the test result page.
    Shows beautiful result preview with email sending status.
    Auto-redirects to dashboard after email is sent.
    """
    return render(request, 'test-result.html')
    return render(request, 'test-page.html', context)


def company_test(request, company=None, difficulty=None):
    """
    Render a company/difficulty specific test page.
    These routes will be used to provide friendly filenames like:
      /tests/google/google-easy.html
    The view validates inputs and passes a `company_logo_url` to the template.
    """
    valid_companies = ['google', 'openai', 'uber', 'microsoft']
    valid_difficulties = ['easy', 'medium', 'hard']

    # Normalize and validate
    company = (company or request.GET.get('company', 'google')).lower()
    difficulty = (difficulty or request.GET.get('difficulty', 'medium')).lower()

    if company not in valid_companies:
        company = 'google'
    if difficulty not in valid_difficulties:
        difficulty = 'medium'

    # Construct a static path for a small logo we added under static/img/logos
    company_logo_url = f"/static/accounts/img/logos/{company}.svg"

    context = {
        'page_title': f'{company.title()} Interview Test',
        'company': company,
        'difficulty': difficulty,
        'company_logo_url': company_logo_url,
        'test_config': {
            'total_questions': 20,
            'max_marks': 100,
            'marks_per_question': 5,
            'time_limit': 1800,
        }
    }

    return render(request, 'test-page.html', context)


# Company Information Database
COMPANY_DATABASE = {
    'capgemini': {
        'name': 'Capgemini',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/c/cb/Capgemini_201x_logo.svg',
        'tagline': 'Digital Leader. Business Accelerator.',
        'description': 'Capgemini is a global leader in partnering with companies to transform and manage their business and technology. With over 300,000 employees and presence in over 50 countries, Capgemini serves clients across all major industries.',
        'industries': ['IT Services', 'Digital Transformation', 'Consulting', 'Cloud Solutions'],
        'hiring_roles': ['Systems Engineer', 'Senior Associate', 'Software Developer', 'Data Engineer', 'Cloud Architect'],
        'salary_range': '₹3.5 - 6 LPA',
        'bonus': '8-12%',
        'benefits': ['Health Insurance', '5 days work week', 'Performance bonus', 'Professional development', 'Stock options'],
        'interview_process': [
            {'round': 'Online Assessment', 'description': 'Aptitude, logical reasoning, verbal ability, and coding test (120 minutes)'},
            {'round': 'Technical Interview', 'description': 'Discussion on core DSA concepts, system design basics, and project-related questions'},
            {'round': 'Pseudo Code Round', 'description': 'Problem-solving using pseudo code or flowcharts'},
            {'round': 'HR Round', 'description': 'Discussion on background, career goals, and company culture fit'}
        ],
        'required_skills': [
            {
                'category': 'Technical Skills',
                'items': ['C/C++/Java/Python', 'Data Structures & Algorithms', 'DBMS', 'SQL', 'Basic OOP concepts']
            },
            {
                'category': 'Soft Skills',
                'items': ['Communication ability', 'Problem-solving mindset', 'Teamwork', 'Adaptability']
            }
        ],
        'interview_tips': [
            {'icon': '📚', 'title': 'Prepare DSA', 'description': 'Focus on arrays, linked lists, trees, and basic graph problems'},
            {'icon': '💻', 'title': 'Practice Pseudo Code', 'description': 'Capgemini emphasizes pseudo code; practice writing clean algorithmic solutions'},
            {'icon': '🎯', 'title': 'Know Your Projects', 'description': 'Be ready to explain all projects on your resume with technical depth'},
            {'icon': '⏱️', 'title': 'Time Management', 'description': 'Online assessment is tricky; practice solving within time limits'}
        ]
    },
    'cognizant': {
        'name': 'Cognizant',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/0/0e/Cognizant_logo.svg',
        'tagline': 'Digital Engineering. Powered by AI.',
        'description': 'Cognizant is a leading provider of information technology, consulting, and business process outsourcing services. With offices worldwide, they help enterprises modernize and transform their business operations.',
        'industries': ['IT Services', 'BPO', 'Digital Services', 'AI & Analytics'],
        'hiring_roles': ['Programmer Analyst', 'Associate Programmer', 'Senior Programmer', 'DevOps Engineer', 'Data Scientist'],
        'salary_range': '₹3.5 - 5.5 LPA',
        'bonus': '8-10%',
        'benefits': ['Comprehensive health coverage', 'Flexible work arrangements', 'Training programs', 'Career growth path', 'Wellness benefits'],
        'interview_process': [
            {'round': 'Online Test', 'description': 'Aptitude (quantitative, logical, verbal) + coding assessment'},
            {'round': 'Technical Round 1', 'description': 'Core technical knowledge, programming concepts, and basic system design'},
            {'round': 'Technical Round 2', 'description': 'Problem-solving, code optimization, and project discussion'},
            {'round': 'HR Round', 'description': 'Background verification, motivation, and cultural fit'}
        ],
        'required_skills': [
            {
                'category': 'Programming',
                'items': ['Java/Python/C++', 'SQL and Database concepts', 'Full-stack development basics']
            },
            {
                'category': 'Core Concepts',
                'items': ['Data Structures', 'Algorithms', 'OOPS', 'Web technologies']
            }
        ],
        'interview_tips': [
            {'icon': '🔧', 'title': 'Tools & Technologies', 'description': 'Highlight experience with relevant tools used in your projects'},
            {'icon': '📝', 'title': 'Problem Analysis', 'description': 'Ask clarifying questions and analyze problems systematically'},
            {'icon': '💬', 'title': 'Communication', 'description': 'Explain your thought process clearly to the interviewer'},
            {'icon': '🚀', 'title': 'Quick Learning', 'description': 'Show eagerness to learn new technologies and frameworks'}
        ]
    },
    'tcs': {
        'name': 'TCS (Tata Consultancy Services)',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/f/f6/Tata_Consultancy_Services_Logo.svg',
        'tagline': 'Experience Certainty.',
        'description': 'TCS is one of the largest IT services, consulting, and business solutions organizations globally. Known for consistent hiring and employee development programs, TCS is a preferred choice for campus recruiting.',
        'industries': ['IT Services', 'Consulting', 'Infrastructure Services', 'Applications Development'],
        'hiring_roles': ['Systems Engineer', 'Network Administration', 'Software Developer', 'IT Support', 'Cloud Solutions'],
        'salary_range': '₹3 - 5 LPA',
        'bonus': '8-15%',
        'benefits': ['Health & wellness programs', 'Retirement benefits', 'Professional certification support', 'Flexible scheduling', 'Learning opportunities'],
        'interview_process': [
            {'round': 'Aptitude Test', 'description': 'Quantitative, logical reasoning, verbal ability (90 minutes)'},
            {'round': 'Technical Interview', 'description': 'Programming languages, data structures, databases, and general CS concepts'},
            {'round': 'Coding Challenge', 'description': 'Write code to solve given problems using your preferred language'},
            {'round': 'HR Round', 'description': 'Final discussion on background, interests, and company culture'}
        ],
        'required_skills': [
            {
                'category': 'Core Programming',
                'items': ['C/Java/Python', 'OOPS Concepts', 'Basic problem-solving']
            },
            {
                'category': 'Fundamentals',
                'items': ['Data Structures', 'Database basics', 'Operating Systems basics']
            }
        ],
        'interview_tips': [
            {'icon': '✅', 'title': 'Clear Basics', 'description': 'TCS focuses on fundamentals; ensure your basics are crystal clear'},
            {'icon': '🎓', 'title': 'Academic Knowledge', 'description': 'Knowledge from college subjects will be directly tested'},
            {'icon': '🤝', 'title': 'Soft Skills', 'description': 'Emphasize teamwork, communication, and willingness to learn'},
            {'icon': '⚡', 'title': 'Consistency', 'description': 'Maintain consistent knowledge; they appreciate long-term learners'}
        ]
    },
    'hcl': {
        'name': 'HCL Technologies',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/8/8e/HCL_Technologies_Logo.svg',
        'tagline': 'Supercharge your aspirations',
        'description': 'HCL Technologies is a global technology company providing software and services. They are known for innovation and providing excellent career growth opportunities to young professionals.',
        'industries': ['IT Services', 'Product Engineering', 'Infrastructure Services'],
        'hiring_roles': ['Software Developer', 'Systems Engineer', 'Associate Software Engineer', 'Quality Analyst', 'DevOps Specialist'],
        'salary_range': '₹3 - 5.5 LPA',
        'bonus': '8-12%',
        'benefits': ['Medical insurance', 'Learning & development', 'Flexible work options', 'Performance bonus', 'Employee wellness'],
        'interview_process': [
            {'round': 'Online Assessment', 'description': 'Aptitude + coding test (reasoning, quantitative, coding practical)'},
            {'round': 'Technical Interview', 'description': 'Problem-solving, code writing, and technical depth assessment'},
            {'round': 'Managerial Round', 'description': 'Discussion on project experience and approach to challenges'},
            {'round': 'HR Round', 'description': 'Final round with HR team'}
        ],
        'required_skills': [
            {
                'category': 'Languages',
                'items': ['C/Java/Python/JavaScript', 'SQL']
            },
            {
                'category': 'CS Fundamentals',
                'items': ['DSA', 'DBMS', 'Operating Systems', 'Networking basics']
            }
        ],
        'interview_tips': [
            {'icon': '🎯', 'title': 'Direct Approach', 'description': 'HCL values direct communication; be clear and concise'},
            {'icon': '💡', 'title': 'Innovation Mindset', 'description': 'Show enthusiasm for learning new technologies'},
            {'icon': '🔍', 'title': 'Deep Dive', 'description': 'Be ready to go deep into any technology you mention'},
            {'icon': '📊', 'title': 'Real-world Problems', 'description': 'Relate your knowledge to real-world applications'}
        ]
    },
    'infosys': {
        'name': 'Infosys',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/1/1a/Infosys_logo_horizontal.svg',
        'tagline': 'Next is what we make it',
        'description': 'Infosys is a global leader in digital services and consulting. Committed to delivering innovation on every client engagement, Infosys provides digital, consulting, technology, and outsourcing services.',
        'industries': ['IT Services', 'Digital Transformation', 'Consulting', 'Business Automation'],
        'hiring_roles': ['Software Developer', 'Systems Engineer', 'Senior Software Developer', 'Data Engineer', 'Cloud Specialist'],
        'salary_range': '₹3.5 - 6 LPA',
        'bonus': '8-12%',
        'benefits': ['Comprehensive health coverage', 'Work-life balance programs', 'Career progression path', 'Continuous learning', 'Performance incentives'],
        'interview_process': [
            {'round': 'Online Test', 'description': 'Aptitude (logical, quantitative, verbal) + coding round'},
            {'round': 'Technical Interview 1', 'description': 'Core concepts, problem-solving, and code review'},
            {'round': 'Technical Interview 2', 'description': 'Deep technical knowledge and project discussion'},
            {'round': 'HR Round', 'description': 'HR panel discussion'}
        ],
        'required_skills': [
            {
                'category': 'Programming',
                'items': ['Java/Python/C++', 'SQL', 'HTML/CSS/JavaScript basics']
            },
            {
                'category': 'Concepts',
                'items': ['DSA', 'DBMS', 'Web services', 'Microservices basics']
            }
        ],
        'interview_tips': [
            {'icon': '🌐', 'title': 'Specialization', 'description': 'Highlight specific technology areas you\'re strong in'},
            {'icon': '📱', 'title': 'Modern Tech', 'description': 'Show knowledge of latest frameworks and tools'},
            {'icon': '🚀', 'title': 'Scalability', 'description': 'Discuss how to build scalable and efficient solutions'},
            {'icon': '🤖', 'title': 'AI/Automation', 'description': 'Knowledge of AI/ML basics is a plus'}
        ]
    },
    'accenture': {
        'name': 'Accenture',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/c/cd/Accenture.svg',
        'tagline': 'Let There Be Change',
        'description': 'Accenture is a global professional services company with leading capabilities in digital, cloud, and security. Committed to delivering on the promise of technology and human ingenuity.',
        'industries': ['Consulting', 'Technology Services', 'Digital Transformation', 'Business Services'],
        'hiring_roles': ['Associate Software Engineer', 'Senior Technology Analyst', 'Solutions Engineer', 'Network Engineer', 'AI/ML Specialist'],
        'salary_range': '₹4 - 7 LPA',
        'bonus': '10-15%',
        'benefits': ['Medical benefits', 'Flexible workplace', 'Professional development', 'Mentoring programs', 'Stock programs'],
        'interview_process': [
            {'round': 'Online Cognitive Assessment', 'description': 'Accenture Digital Assessment: logical, numerical, verbal, and technical questions'},
            {'round': 'Technical Interview', 'description': 'Programming concepts, system design, and problem-solving'},
            {'round': 'Second Technical Round', 'description': 'Advanced concepts and project experience discussion'},
            {'round': 'HR & Management Round', 'description': 'Final round with HR and senior management'}
        ],
        'required_skills': [
            {
                'category': 'Technical Stacks',
                'items': ['Java/Python/C++/JavaScript', 'Full-stack development', 'Cloud platforms']
            },
            {
                'category': 'Advanced Topics',
                'items': ['System Design', 'Microservices', 'DevOps', 'Cloud computing']
            }
        ],
        'interview_tips': [
            {'icon': '🎓', 'title': 'Accenture Assessment', 'description': 'Practice their specific online assessment; it\'s unique and different'},
            {'icon': '🌍', 'title': 'Global Mindset', 'description': 'Show openness to working with global teams'},
            {'icon': '💼', 'title': 'Client Skills', 'description': 'Accenture works with clients; emphasize communication skills'},
            {'icon': '🔄', 'title': 'Agile & DevOps', 'description': 'Familiarity with agile and DevOps methodologies is valuable'}
        ]
    },
    'amazon': {
        'name': 'Amazon',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg',
        'tagline': 'Work Hard. Have Fun. Make History.',
        'description': 'Amazon is a global technology company focused on e-commerce, cloud computing, digital streaming, and artificial intelligence. Known for its leadership principles and fast-paced environment.',
        'industries': ['E-commerce', 'Cloud Computing', 'AI/ML', 'Streaming Services'],
        'hiring_roles': ['Software Development Engineer', 'Data Engineer', 'Solutions Architect', 'DevOps Engineer', 'ML Scientist'],
        'salary_range': '₹6 - 15 LPA',
        'bonus': '10-15%',
        'benefits': ['ESOP/Stock options', 'Health and wellness', 'Relocation assistance', 'Professional development', 'Maternity benefits'],
        'interview_process': [
            {'round': 'Online Coding Assessment', 'description': 'LeetCode-style problems (2 problems in 90 minutes)'},
            {'round': 'Phone Technical Interview', 'description': 'System design or coding round with experienced engineer'},
            {'round': '2-4 Onsite Interviews', 'description': 'Mix of coding, system design, and behavioral interviews'},
            {'round': 'Bar Raiser Interview', 'description': 'Final interview with senior engineer from different team'}
        ],
        'required_skills': [
            {
                'category': 'Core Competencies',
                'items': ['Strong DSA', 'System Design', 'Java/Python', 'Distributed systems']
            },
            {
                'category': 'Amazon Specific',
                'items': ['Leadership principles knowledge', 'AWS basics', 'Scalability thinking']
            }
        ],
        'interview_tips': [
            {'icon': '⚡', 'title': 'Leadership Principles', 'description': 'Familiarize yourself with Amazon\'s 16 leadership principles'},
            {'icon': '🎯', 'title': 'Customer Obsession', 'description': 'Show focus on customer problems in your answers'},
            {'icon': '🔬', 'title': 'Data-Driven', 'description': 'Use metrics and data to support your solutions'},
            {'icon': '📈', 'title': 'Bias for Action', 'description': 'Show decisiveness and ability to make quick calls'}
        ]
    },
    'microsoft': {
        'name': 'Microsoft',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg',
        'tagline': 'Empowering Every Person and Organization',
        'description': 'Microsoft is a global leader in software, services, and solutions. Innovation is at the heart of everything they do, from cloud computing to AI to enterprise solutions.',
        'industries': ['Software', 'Cloud Computing', 'AI/ML', 'Gaming', 'Cybersecurity'],
        'hiring_roles': ['Software Engineer', 'Cloud Solution Architect', 'Security Engineer', 'Data Scientist', 'AI Specialist'],
        'salary_range': '₹8 - 20 LPA',
        'bonus': '15-25%',
        'benefits': ['Competitive stock options', 'World-class benefits', 'Health insurance', 'Gym memberships', 'Professional growth'],
        'interview_process': [
            {'round': 'Online Assessment', 'description': 'Coding + problem-solving (Microsoft specific assessment)'},
            {'round': 'Phone Screening', 'description': 'Technical depth and communication assessment'},
            {'round': '2-3 Onsite Rounds', 'description': 'Mix of coding, system design, and technical interviews'},
            {'round': 'Team Match Round', 'description': 'Discussion with potential team lead'}
        ],
        'required_skills': [
            {
                'category': 'Technical Skills',
                'items': ['C#/Java/Python', 'Advanced DSA', 'System Design', '.NET basics']
            },
            {
                'category': 'Cloud & Scale',
                'items': ['Azure knowledge', 'Cloud architecture', 'Distributed systems']
            }
        ],
        'interview_tips': [
            {'icon': '🧠', 'title': 'Think Cloud', 'description': 'Show understanding of cloud-first thinking and scalability'},
            {'icon': '🔧', 'title': 'Tools & Platforms', 'description': 'Familiarity with Microsoft tools (Azure, Office 365, etc.)'},
            {'icon': '🤝', 'title': 'Collaboration', 'description': 'Microsoft values teamwork and cross-functional collaboration'},
            {'icon': '📚', 'title': 'Continuous Learning', 'description': 'Show passion for learning new technologies'}
        ]
    },
    'wipro': {
        'name': 'Wipro',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/1/19/Wipro_Logo_2017.svg',
        'tagline': 'Applying Thought',
        'description': 'Wipro is a leading provider of information technology, consulting and business process services. Known for its strong engineering teams and global presence.',
        'industries': ['IT Services', 'Consulting', 'Engineering Services'],
        'hiring_roles': ['Software Engineer', 'Systems Engineer', 'Senior Associate', 'Data Analyst', 'Cloud Engineer'],
        'salary_range': '₹3 - 5 LPA',
        'bonus': '8-12%',
        'benefits': ['Health insurance', 'Flexible work', 'Training programs', 'Career growth', 'Employee wellness'],
        'interview_process': [
            {'round': 'Online Aptitude Test', 'description': 'Quantitative, logical, and verbal reasoning'},
            {'round': 'Technical Round', 'description': 'Core programming concepts and problem-solving'},
            {'round': 'Coding Challenge', 'description': 'Write code solutions for given problems'},
            {'round': 'HR Round', 'description': 'Background and cultural fit discussion'}
        ],
        'required_skills': [
            {'category': 'Programming', 'items': ['Java/Python/C++', 'SQL', 'Data Structures']},
            {'category': 'Concepts', 'items': ['Algorithms', 'DBMS', 'Networks']}
        ],
        'interview_tips': [
            {'icon': '💻', 'title': 'Code Quality', 'description': 'Write clean, readable code with proper variable names'},
            {'icon': '⚡', 'title': 'Optimization', 'description': 'Focus on optimizing solutions for time and space'},
            {'icon': '🎯', 'title': 'Problem Solving', 'description': 'Break problems into smaller components'},
            {'icon': '📝', 'title': 'Documentation', 'description': 'Explain your approach clearly'}
        ]
    },
    'deloitte': {
        'name': 'Deloitte',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Deloitte_2019_logo.svg/440px-Deloitte_2019_logo.svg.png',
        'tagline': 'Make an Impact',
        'description': 'Deloitte is a global consulting firm providing audit, consulting, financial advisory, risk advisory, and tax services.',
        'industries': ['Consulting', 'Audit', 'Advisory', 'Compliance'],
        'hiring_roles': ['Business Analyst', 'Consultant', 'Technology Consultant', 'Risk Analyst', 'Data Analyst'],
        'salary_range': '₹4 - 8 LPA',
        'bonus': '10-15%',
        'benefits': ['Medical coverage', 'Mentoring program', 'Professional development', 'Flexible working'],
        'interview_process': [
            {'round': 'Aptitude Test', 'description': 'Logical reasoning and analytical skills'},
            {'round': 'Technical/Business Round', 'description': 'Domain knowledge and problem-solving'},
            {'round': 'Case Study', 'description': 'Real-world business case analysis'},
            {'round': 'HR & Final Round', 'description': 'Culture fit and offer discussion'}
        ],
        'required_skills': [
            {'category': 'Analytical', 'items': ['Problem-solving', 'Logical thinking', 'Data analysis']},
            {'category': 'Business', 'items': ['Industry knowledge', 'Communication', 'Client management']}
        ],
        'interview_tips': [
            {'icon': '🎓', 'title': 'Case Studies', 'description': 'Practice solving business case problems'},
            {'icon': '💼', 'title': 'Industry Knowledge', 'description': 'Stay updated with current industry trends'},
            {'icon': '🗣️', 'title': 'Communication', 'description': 'Present your ideas clearly and confidently'},
            {'icon': '📊', 'title': 'Analytics', 'description': 'Show strong analytical and quantitative skills'}
        ]
    },
    'goldman-sachs': {
        'name': 'Goldman Sachs',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/5/5d/GoldmanSachs.svg',
        'tagline': 'Investment Banking Excellence',
        'description': 'Goldman Sachs is a leading global investment banking, securities and investment management firm.',
        'industries': ['Investment Banking', 'Finance', 'Trading', 'Risk Management'],
        'hiring_roles': ['Analyst', 'Associate', 'Engineer', 'Risk Analyst', 'Quantitative Analyst'],
        'salary_range': '₹8 - 20 LPA',
        'bonus': '20-50%',
        'benefits': ['Stock options', 'Bonuses', 'Premium healthcare', 'Learning funds'],
        'interview_process': [
            {'round': 'Online Assessment', 'description': 'Quantitative reasoning and coding'},
            {'round': 'Technical Interview', 'description': 'System design and problem-solving'},
            {'round': 'Business Round', 'description': 'Financial domain knowledge'},
            {'round': 'Executive Round', 'description': 'Leadership and culture fit'}
        ],
        'required_skills': [
            {'category': 'Technical', 'items': ['C++/Java/Python', 'Data Structures', 'Algorithms']},
            {'category': 'Finance', 'items': ['Financial markets', 'Quantitative analysis', 'Risk management']}
        ],
        'interview_tips': [
            {'icon': '💰', 'title': 'Financial Knowledge', 'description': 'Understand financial markets and instruments'},
            {'icon': '🔢', 'title': 'Quantitative Skills', 'description': 'Excel at mathematical and statistical problems'},
            {'icon': '⚙️', 'title': 'System Design', 'description': 'Be ready for large-scale system design questions'},
            {'icon': '🎯', 'title': 'Precision', 'description': 'Attention to detail is critical'}
        ]
    },
    'paloalto': {
        'name': 'Palo Alto Networks',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/3/34/Palo_Alto_Networks_logo.svg',
        'tagline': 'Secure Every Moment',
        'description': 'Palo Alto Networks is a cybersecurity company delivering security software and services.',
        'industries': ['Cybersecurity', 'Enterprise Security', 'Cloud Security', 'Network Security'],
        'hiring_roles': ['Security Engineer', 'Software Engineer', 'Security Analyst', 'Threat Researcher', 'DevOps Engineer'],
        'salary_range': '₹6 - 14 LPA',
        'bonus': '15-20%',
        'benefits': ['Security training', 'Home office', 'Learning budget', 'Flexible schedule'],
        'interview_process': [
            {'round': 'Coding Assessment', 'description': 'Programming and problem-solving skills'},
            {'round': 'Security Interview', 'description': 'Security concepts and threat analysis'},
            {'round': 'System Design', 'description': 'Designing secure systems at scale'},
            {'round': 'Final Round', 'description': 'Team and culture fit'}
        ],
        'required_skills': [
            {'category': 'Security', 'items': ['Networking basics', 'Cryptography', 'Threat modeling', 'Incident response']},
            {'category': 'Technical', 'items': ['C/C++/Python', 'Linux', 'Security protocols']}
        ],
        'interview_tips': [
            {'icon': '🔐', 'title': 'Security First', 'description': 'Always think about security implications'},
            {'icon': '🌐', 'title': 'Network Knowledge', 'description': 'Strong understanding of networking essentials'},
            {'icon': '🛡️', 'title': 'Threat Analysis', 'description': 'Be able to identify and mitigate security threats'},
            {'icon': '🧠', 'title': 'Stay Updated', 'description': 'Keep up with latest cybersecurity trends'}
        ]
    },
    'zscaler': {
        'name': 'Zscaler',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Zscaler_logo_2023.svg/220px-Zscaler_logo_2023.svg.png',
        'tagline': 'Zero Trust Security',
        'description': 'Zscaler is a cybersecurity company providing zero trust security solutions and services.',
        'industries': ['Cybersecurity', 'Zero Trust', 'Cloud Security', 'Enterprise Security'],
        'hiring_roles': ['Security Engineer', 'Cloud Engineer', 'Software Engineer', 'Solutions Architect', 'Security Analyst'],
        'salary_range': '₹5 - 12 LPA',
        'bonus': '12-18%',
        'benefits': ['Security certifications', 'Relocation support', 'Remote work', 'Professional development'],
        'interview_process': [
            {'round': 'Technical Screening', 'description': 'Coding and basic DSA assessment'},
            {'round': 'Security Deep Dive', 'description': 'Security protocols and threat models'},
            {'round': 'Architecture Round', 'description': 'Cloud and security architecture design'},
            {'round': 'Team Discussion', 'description': 'Team fit and career goals'}
        ],
        'required_skills': [
            {'category': 'Cloud Security', 'items': ['Cloud platforms', 'Container security', 'API security']},
            {'category': 'Programming', 'items': ['Python/Go', 'Networking', 'Linux']}
        ],
        'interview_tips': [
            {'icon': '☁️', 'title': 'Cloud Knowledge', 'description': 'Deep understanding of cloud architectures'},
            {'icon': '🔑', 'title': 'Zero Trust', 'description': 'Understand zero trust security principles'},
            {'icon': '🚀', 'title': 'Scalability', 'description': 'Design solutions for scale and performance'},
            {'icon': '🔍', 'title': 'Monitoring', 'description': 'Knowledge of security monitoring and logging'}
        ]
    },
    'airbus': {
        'name': 'Airbus',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/d/d8/Airbus_Logo_2017.svg',
        'tagline': 'We make it fly',
        'description': 'Airbus is a European aircraft manufacturer and aerospace company.',
        'industries': ['Aerospace', 'Defense', 'Aviation', 'Engineering'],
        'hiring_roles': ['Software Engineer', 'Embedded Systems Engineer', 'Mechanical Engineer', 'Systems Engineer', 'DevOps Engineer'],
        'salary_range': '₹5 - 10 LPA',
        'bonus': '10-15%',
        'benefits': ['Relocation', 'Housing allowance', 'Medical coverage', 'Professional development'],
        'interview_process': [
            {'round': 'Technical Assessment', 'description': 'Programming and problem-solving'},
            {'round': 'Embedded Systems Round', 'description': 'Real-time systems and embedded C/C++'},
            {'round': 'System Design', 'description': 'Designing complex aerospace systems'},
            {'round': 'HR Round', 'description': 'Background and culture fit'}
        ],
        'required_skills': [
            {'category': 'Embedded', 'items': ['C/C++', 'Embedded systems', 'Real-time programming']},
            {'category': 'Aerospace', 'items': ['Systems thinking', 'Safety-critical systems', 'RTOS']}
        ],
        'interview_tips': [
            {'icon': '✈️', 'title': 'Domain Knowledge', 'description': 'Learn about aerospace industry basics'},
            {'icon': '🔧', 'title': 'Embedded Focus', 'description': 'Strong embedded systems expertise expected'},
            {'icon': '⚙️', 'title': 'Complex Systems', 'description': 'Ability to handle complex system design'},
            {'icon': '📋', 'title': 'Documentation', 'description': 'Detailed documentation and standards compliance'}
        ]
    },
    'morgan-stanley': {
        'name': 'Morgan Stanley',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/3/36/Morgan_Stanley_logo.svg',
        'tagline': 'Your Global Investment Partner',
        'description': 'Morgan Stanley is a leading global financial services firm providing investment banking, securities and wealth management services.',
        'industries': ['Investment Banking', 'Finance', 'Wealth Management', 'Trading'],
        'hiring_roles': ['Analyst', 'Associate', 'Software Engineer', 'Quantitative Analyst', 'Risk Manager'],
        'salary_range': '₹7 - 18 LPA',
        'bonus': '15-40%',
        'benefits': ['Stock options', 'Performance bonus', 'Healthcare', 'Education fund'],
        'interview_process': [
            {'round': 'Online Test', 'description': 'Logical reasoning and quantitative skills'},
            {'round': 'Technical Interview', 'description': 'Programming and system design'},
            {'round': 'Business Round', 'description': 'Financial knowledge and case studies'},
            {'round': 'Executive Round', 'description': 'Leadership assessment'}
        ],
        'required_skills': [
            {'category': 'Finance', 'items': ['Financial markets', 'Derivatives', 'Risk analysis']},
            {'category': 'Technical', 'items': ['C++/Java', 'Algorithms', 'Database systems']}
        ],
        'interview_tips': [
            {'icon': '📈', 'title': 'Market Knowledge', 'description': 'Understand financial markets and instruments'},
            {'icon': '💻', 'title': 'Trading Systems', 'description': 'Knowledge of high-frequency trading systems'},
            {'icon': '🎯', 'title': 'Performance', 'description': 'Focus on optimization and efficiency'},
            {'icon': '💼', 'title': 'Professionalism', 'description': 'Demonstrate professional and analytical approach'}
        ]
    },
    'kpit': {
        'name': 'KPIT Technologies',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/8/8a/KPIT_Technologies_logo.jpg',
        'tagline': 'Automotive Software Excellence',
        'description': 'KPIT Technologies is a leading automotive software and engineering services company.',
        'industries': ['Automotive', 'Embedded Systems', 'IoT', 'Engineering Services'],
        'hiring_roles': ['Embedded Software Engineer', 'Automotive Software Engineer', 'Systems Engineer', 'Quality Engineer', 'DevOps Engineer'],
        'salary_range': '₹3.5 - 7 LPA',
        'bonus': '8-12%',
        'benefits': ['Medical insurance', 'Flexible working', 'Technical training', 'Career progression'],
        'interview_process': [
            {'round': 'Technical Assessment', 'description': 'C/C++ and embedded systems programming'},
            {'round': 'Automotive Knowledge', 'description': 'Automotive domain and protocols (CAN, LIN)'},
            {'round': 'System Design', 'description': 'Designing automotive software systems'},
            {'round': 'HR Round', 'description': 'Background and motivation'}
        ],
        'required_skills': [
            {'category': 'Embedded', 'items': ['C/C++', 'RTOS', 'Microcontrollers', 'Automotive protocols']},
            {'category': 'Domain', 'items': ['CAN/LIN/FlexRay', 'AUTOSAR', 'Vehicle diagnostics']}
        ],
        'interview_tips': [
            {'icon': '🚗', 'title': 'Automotive Focus', 'description': 'Learn about automotive software development'},
            {'icon': '⚙️', 'title': 'Embedded Expertise', 'description': 'Strong C/C++ and embedded systems knowledge'},
            {'icon': '🔌', 'title': 'Protocols', 'description': 'Understand automotive communication protocols'},
            {'icon': '🛠️', 'title': 'Debugging', 'description': 'Strong debugging and troubleshooting skills'}
        ]
    },
    'thermax': {
        'name': 'Thermax',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/0/0c/Thermax_Limited_Logo.png',
        'tagline': 'Engineering Solutions for Sustainability',
        'description': 'Thermax is an engineering company providing energy and environment solutions.',
        'industries': ['Engineering', 'Energy', 'Environmental', 'Industrial Solutions'],
        'hiring_roles': ['Design Engineer', 'Software Engineer', 'Mechanical Engineer', 'Electrical Engineer', 'Project Manager'],
        'salary_range': '₹3 - 6 LPA',
        'bonus': '8-10%',
        'benefits': ['Medical coverage', 'Performance bonus', 'Technical training', 'Career growth'],
        'interview_process': [
            {'round': 'Technical Test', 'description': 'Engineering fundamentals and problem-solving'},
            {'round': 'Domain Round', 'description': 'Industry-specific knowledge and applications'},
            {'round': 'Project Discussion', 'description': 'Academic or professional projects'},
            {'round': 'HR Round', 'description': 'Background and fit assessment'}
        ],
        'required_skills': [
            {'category': 'Engineering', 'items': ['CAD/CAM', 'Thermodynamics', 'Heat transfer', 'Mechanical design']},
            {'category': 'Technical', 'items': ['MATLAB/Python', 'Simulation tools', 'AutoCAD']}
        ],
        'interview_tips': [
            {'icon': '🌱', 'title': 'Sustainability', 'description': 'Show interest in green and sustainable solutions'},
            {'icon': '🏭', 'title': 'Industrial Knowledge', 'description': 'Understand industrial processes and challenges'},
            {'icon': '📐', 'title': 'Design Skills', 'description': 'Demonstrate CAD and design capabilities'},
            {'icon': '💡', 'title': 'Problem Solving', 'description': 'Focus on practical engineering solutions'}
        ]
    },
    'amandeus': {
        'name': 'Amadeus',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/2/2c/Amadeus_IT_Group_logo.svg',
        'tagline': 'Powering Travel',
        'description': 'Amadeus is a leading travel technology company providing software and services to the travel industry.',
        'industries': ['Travel Technology', 'SaaS', 'Cloud Solutions', 'B2B'],
        'hiring_roles': ['Software Engineer', 'Backend Developer', 'Systems Engineer', 'DevOps Engineer', 'Quality Analyst'],
        'salary_range': '₹4 - 9 LPA',
        'bonus': '12-15%',
        'benefits': ['Travel benefits', 'Professional development', 'Flexible hours', 'Health insurance'],
        'interview_process': [
            {'round': 'Online Coding', 'description': 'Algorithm and data structure problems'},
            {'round': 'System Design', 'description': 'Designing scalable travel systems'},
            {'round': 'Backend Technology', 'description': 'Microservices and distributed systems'},
            {'round': 'HR & Team Match', 'description': 'Culture and team fit'}
        ],
        'required_skills': [
            {'category': 'Backend', 'items': ['Java/Python', 'SQL', 'REST APIs', 'Microservices']},
            {'category': 'Cloud', 'items': ['Cloud platforms', 'Container orchestration', 'CI/CD']}
        ],
        'interview_tips': [
            {'icon': '✈️', 'title': 'Travel Industry', 'description': 'Understand travel systems and GDS basics'},
            {'icon': '🏗️', 'title': 'System Design', 'description': 'Focus on scalable distributed architecture'},
            {'icon': '🔄', 'title': 'Microservices', 'description': 'Experience with microservices pattern'},
            {'icon': '📊', 'title': 'Data Handling', 'description': 'Handle large-scale data and transactions'}
        ]
    },
    'hexaware': {
        'name': 'Hexaware',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/2/22/Hexaware_Logo.png',
        'tagline': 'Digital Reimagined',
        'description': 'Hexaware is an IT services and consulting company providing digital transformation solutions.',
        'industries': ['IT Services', 'Digital Transformation', 'Consulting', 'Cloud Services'],
        'hiring_roles': ['Software Engineer', 'Systems Engineer', 'Senior Developer', 'Cloud Architect', 'QA Analyst'],
        'salary_range': '₹3 - 6 LPA',
        'bonus': '8-12%',
        'benefits': ['Health insurance', 'Learning programs', 'Flexible work', 'Career path'],
        'interview_process': [
            {'round': 'Aptitude Test', 'description': 'Quantitative, logical and reasoning skills'},
            {'round': 'Technical Interview', 'description': 'Programming and problem-solving'},
            {'round': 'Second Technical', 'description': 'Project experience and system design'},
            {'round': 'HR Round', 'description': 'Final selection'}
        ],
        'required_skills': [
            {'category': 'Programming', 'items': ['Java/Python', 'SQL', 'Full-stack basics']},
            {'category': 'Digital', 'items': ['Cloud platforms', 'DevOps', 'Agile methodology']}
        ],
        'interview_tips': [
            {'icon': '🌐', 'title': 'Digital Focus', 'description': 'Show knowledge of digital transformation'},
            {'icon': '☁️', 'title': 'Cloud Ready', 'description': 'Familiar with cloud platforms and services'},
            {'icon': '⚡', 'title': 'Agile Mindset', 'description': 'Comfortable with agile and DevOps practices'},
            {'icon': '🤝', 'title': 'Collaboration', 'description': 'Emphasize teamwork and communication'}
        ]
    },
    'ibm': {
        'name': 'IBM',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg',
        'tagline': 'Think. Build. Transform.',
        'description': 'IBM is a global technology and consulting company providing enterprise hardware, software, and services. Known for innovation in cloud, AI, and quantum computing.',
        'industries': ['Enterprise IT', 'Cloud Solutions', 'AI & Cognitive', 'Quantum Computing', 'Consulting'],
        'hiring_roles': ['Software Engineer', 'Cloud Developer', 'Data Scientist', 'Systems Engineer', 'Solutions Architect'],
        'salary_range': '₹4 - 8 LPA',
        'bonus': '10-15%',
        'benefits': ['Health insurance', 'Stock options', 'Training programs', 'Flexible work arrangements', 'Wellness programs'],
        'interview_process': [
            {'round': 'Online Assessment', 'description': 'Coding test on HackerEarth or similar platform (2-3 problems, 90 minutes)'},
            {'round': 'Technical Interview 1', 'description': 'Core concepts, DSA, system design, and code optimization'},
            {'round': 'Technical Interview 2', 'description': 'Advanced problem-solving, architecture design, and project discussion'},
            {'round': 'HR Round', 'description': 'Background, motivation, and cultural fit assessment'}
        ],
        'required_skills': [
            {
                'category': 'Programming',
                'items': ['Java/Python/C++', 'SQL and Databases', 'Web services and APIs', 'Full-stack development']
            },
            {
                'category': 'Cloud & DevOps',
                'items': ['AWS/Azure/GCP', 'Docker/Kubernetes', 'CI/CD pipelines', 'Linux administration']
            }
        ],
        'interview_tips': [
            {'icon': '☁️', 'title': 'Cloud Knowledge', 'description': 'Showcase understanding of cloud services and architectures'},
            {'icon': '🤖', 'title': 'AI & Innovation', 'description': 'Mention interest in AI, blockchain, or quantum technologies'},
            {'icon': '🏗️', 'title': 'System Design', 'description': 'Practice designing scalable systems and microservices'},
            {'icon': '📊', 'title': 'Analytics Mindset', 'description': 'Demonstrate data-driven thinking in solutions'}
        ]
    },
    'accolite': {
        'name': 'Accolite Digital',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Accolite_Digital_Logo.png/220px-Accolite_Digital_Logo.png',
        'tagline': 'Digital Transformation Enabler',
        'description': 'Accolite Digital is a digital transformation consulting company specializing in cloud solutions, AI, and enterprise modernization. Focused on startup and SME growth.',
        'industries': ['Digital Transformation', 'Cloud Consulting', 'AI Solutions', 'Enterprise Software', 'Startup Tech'],
        'hiring_roles': ['Software Engineer', 'Cloud Architect', 'Data Engineer', 'Full Stack Developer', 'Technical Lead'],
        'salary_range': '₹3.5 - 7 LPA',
        'bonus': '8-12%',
        'benefits': ['Performance bonus', 'Health insurance', 'Professional development', 'Flexible working', 'Stock options'],
        'interview_process': [
            {'round': 'Online Test', 'description': 'Coding challenge on platform like HackerRank (2-3 problems)'},
            {'round': 'Technical Interview 1', 'description': 'Data structures, algorithms, and database concepts'},
            {'round': 'Technical Interview 2', 'description': 'System design, API design, and cloud architecture'},
            {'round': 'HR & Culture Round', 'description': 'Values alignment and career aspirations'}
        ],
        'required_skills': [
            {
                'category': 'Core Development',
                'items': ['Java/Python/JavaScript', 'Databases (SQL & NoSQL)', 'REST APIs', 'Microservices']
            },
            {
                'category': 'Cloud & Modern Stack',
                'items': ['AWS or GCP', 'Docker & Kubernetes', 'Agile methodologies', 'Git & Version control']
            }
        ],
        'interview_tips': [
            {'icon': '🚀', 'title': 'Startup Mindset', 'description': 'Show entrepreneurial thinking and problem-solving attitude'},
            {'icon': '💡', 'title': 'Modern Tech Stack', 'description': 'Highlight experience with latest frameworks and technologies'},
            {'icon': '🔧', 'title': 'Hands-on Skills', 'description': 'Demonstrate practical knowledge of modern development tools'},
            {'icon': '📱', 'title': 'Full Stack Ready', 'description': 'Comfortable working across frontend, backend, and infrastructure'}
        ]
    },
    'sap': {
        'name': 'SAP',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/5/5c/SAP_2011_logo.svg',
        'tagline': 'Run Better. Together.',
        'description': 'SAP is a leading enterprise resource planning software company. Provides integrated business management solutions and cloud-based applications for businesses worldwide.',
        'industries': ['Enterprise Software', 'ERP Solutions', 'Cloud Computing', 'Business Intelligence', 'Analytics'],
        'hiring_roles': ['Software Developer', 'ABAP Developer', 'Consultant', 'Sales Engineer', 'Product Manager'],
        'salary_range': '₹4 - 10 LPA',
        'bonus': '12-18%',
        'benefits': ['Premium health insurance', 'Stock options', 'Generous PTO', 'Learning budget', 'Global mobility'],
        'interview_process': [
            {'round': 'Coding Assessment', 'description': 'Algorithm and data structure problems (60-90 minutes)'},
            {'round': 'Technical Phone Interview', 'description': 'Technical depth, problem-solving approach, and domain knowledge'},
            {'round': 'On-site Technical', 'description': 'System design, architecture discussions, and real-world scenarios'},
            {'round': 'Final Round', 'description': 'HR round and team cultural fit assessment'}
        ],
        'required_skills': [
            {
                'category': 'Core Skills',
                'items': ['Java/Python/C#', 'SQL and Database design', 'Software architecture', 'API development']
            },
            {
                'category': 'SAP Specific',
                'items': ['ABAP (preferred)', 'SAP Cloud Platform', 'SAP Fiori', 'HANA database basics']
            }
        ],
        'interview_tips': [
            {'icon': '🏢', 'title': 'Enterprise Focus', 'description': 'Understand enterprise software challenges and solutions'},
            {'icon': '📊', 'title': 'ERP Knowledge', 'description': 'Basic understanding of ERP concepts and business processes'},
            {'icon': '🌍', 'title': 'Global Mindset', 'description': 'Show interest in global business and innovation'},
            {'icon': '💼', 'title': 'Professional Approach', 'description': 'Demonstrate maturity and business acumen in discussions'}
        ]
    }
}


def company_details(request, company):
    """Display detailed information about a specific company."""
    try:
        company_key = company.lower().strip()
        
        if company_key not in COMPANY_DATABASE:
            # If exact match not found, try to find partial match
            for key in COMPANY_DATABASE.keys():
                if key in company_key or company_key in key:
                    company_key = key
                    break
            else:
                raise Http404(f"Company '{company}' not found")
        
        company_data = COMPANY_DATABASE[company_key]
        
        context = {
            'company': company_data,
            'page_title': f'{company_data["name"]} - Interview Preparation Guide'
        }
        
        return render(request, 'company-details.html', context)
    
    except Http404:
        raise
    except Exception as e:
        raise Http404(f"Error loading company details: {str(e)}")


# ✅ नए Users को देखने के लिए view
def view_all_users(request):
    """सभी registered users को show करता है"""
    from .models import UserProfile
    
    # सभी users को get करो
    all_users = AuthUser.objects.all()
    user_data = []
    
    for user in all_users:
        profile = UserProfile.objects.filter(auth_user=user).first()
        user_data.append({
            'id': user.id,
            'email': user.email,
            'fullname': user.first_name,
            'date_joined': user.date_joined,
            'phone': profile.phone if profile else '-',
            'is_paid': profile.has_paid if profile else False,
        })
    
    context = {
        'users': user_data,
        'total_users': len(user_data),
    }
    return render(request, 'users_list.html', context)
