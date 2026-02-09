import json
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from .models import Item, Mock, PurchasedItem, AttemptedMock, User, Question
from .jwt_utils import verify_token, create_token
import socketio


def _get_user_from_request(request, data=None):
    """Resolve user from Authorization Bearer token or `userId` field in payload.

    Returns (user_obj, error_response_or_None)
    """
    # 1) Try Authorization header
    auth = request.META.get('HTTP_AUTHORIZATION')
    if auth and auth.lower().startswith('bearer '):
        token = auth.split(None, 1)[1]
        payload = verify_token(token)
        if not payload:
            return None, JsonResponse({'ok': False, 'error': 'invalid_token'}, status=401)
        user_id = payload.get('user_id')
        try:
            u = User.objects.get(pk=user_id)
            return u, None
        except User.DoesNotExist:
            return None, JsonResponse({'ok': False, 'error': 'user_not_found'}, status=404)

    # 2) Try JSON body userId
    if data is None:
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = {}
    user_id = data.get('userId')
    if user_id:
        try:
            u = User.objects.get(pk=user_id)
            return u, None
        except User.DoesNotExist:
            return None, JsonResponse({'ok': False, 'error': 'user_not_found'}, status=404)

    return None, JsonResponse({'ok': False, 'error': 'authentication_required'}, status=401)


def _emit_profile_updated(user_id, profile):
    """Emit profileUpdated via Socket.IO to server on localhost:3000.

    This uses a short-lived Socket.IO client connection.
    """
    try:
        sio = socketio.Client()
        sio.connect('http://localhost:3000', namespaces=['/'])
        # emit to server which will forward to room
        sio.emit('server_emit', {'to': str(user_id), 'event': 'profileUpdated', 'payload': profile})
        sio.disconnect()
    except Exception:
        # In production log the error; for demo we ignore
        pass


@csrf_exempt
@require_POST
def purchase(request):
    """POST /purchase

    Body: { userId, itemId, itemType }
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('invalid json')

    user, err = _get_user_from_request(request, data)
    if err:
        return err

    item_id = data.get('itemId')
    if not item_id:
        return HttpResponseBadRequest('itemId required')
    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'item_not_found'}, status=404)

    # create PurchasedItem record
    pi = PurchasedItem.objects.create(
        user=user,
        item=item,
        title=item.title,
        item_type=item.item_type,
        purchased_at=timezone.now(),
    )

    # Build updated profile payload
    purchased = [p.as_dict() for p in user.purchased_items.all().order_by('-purchased_at')]
    attempted = [a.as_dict() for a in user.attempted_mocks.all().order_by('-attempt_date')]
    profile = {
        'userInfo': {'id': str(user.id), 'phone': getattr(user, 'phone', None)},
        'purchasedItems': purchased,
        'attemptedMocks': attempted,
    }

    # emit realtime
    _emit_profile_updated(user.id, profile)

    return JsonResponse({'ok': True, 'user': profile})


@csrf_exempt
@require_POST
def mock_attempt(request):
    """POST /mock/attempt

    Body: { userId, mockId, score }
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('invalid json')

    user, err = _get_user_from_request(request, data)
    if err:
        return err

    mock_id = data.get('mockId')
    score = data.get('score')
    if mock_id is None or score is None:
        return HttpResponseBadRequest('mockId and score required')

    try:
        mock = Mock.objects.get(pk=mock_id)
    except Mock.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'mock_not_found'}, status=404)

    am = AttemptedMock.objects.create(user=user, mock=mock, score=int(score), attempt_date=timezone.now())

    purchased = [p.as_dict() for p in user.purchased_items.all().order_by('-purchased_at')]
    attempted = [a.as_dict() for a in user.attempted_mocks.all().order_by('-attempt_date')]
    profile = {
        'userInfo': {'id': str(user.id), 'phone': getattr(user, 'phone', None)},
        'purchasedItems': purchased,
        'attemptedMocks': attempted,
    }

    _emit_profile_updated(user.id, profile)

    return JsonResponse({'ok': True, 'user': profile})


@require_GET
def user_profile(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'user_not_found'}, status=404)

    purchased = [p.as_dict() for p in user.purchased_items.all().order_by('-purchased_at')]
    attempted = [a.as_dict() for a in user.attempted_mocks.all().order_by('-attempt_date')]

    profile = {
        'userInfo': {
            'id': str(user.id),
            'phone': getattr(user, 'phone', None),
        },
        'purchasedItems': purchased,
        'attemptedMocks': attempted,
    }

    return JsonResponse({'ok': True, 'profile': profile})


@csrf_exempt
def token_for_user(request):
    """Utility endpoint to mint JWT for a given user id (demo). POST { userId }
    In production, issue tokens at login only.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('invalid json')

    user_id = data.get('userId')
    if not user_id:
        return HttpResponseBadRequest('userId required')
    try:
        u = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'user_not_found'}, status=404)

    token = create_token({'user_id': str(u.id)})
    return JsonResponse({'ok': True, 'token': token})


@csrf_exempt
@require_POST
def test_create_item(request):
    """Temporary test-only endpoint: POST { item_type, title, price, file_url } -> creates Item"""
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('invalid json')
    itype = data.get('item_type') or 'pdf'
    title = data.get('title') or 'Test Item'
    price = data.get('price') or 0
    file_url = data.get('file_url')
    item = Item.objects.create(item_type=itype, title=title, description=data.get('description',''), price=price, file_url=file_url)
    return JsonResponse({'ok': True, 'item': {'id': item.id, 'title': item.title}})


@csrf_exempt
@require_POST
def test_create_mock(request):
    """Temporary test-only endpoint: POST { title, duration } -> creates Mock"""
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('invalid json')
    title = data.get('title') or 'Test Mock'
    duration = int(data.get('duration') or 30)
    m = Mock.objects.create(title=title, questions=data.get('questions',[]), duration=duration)
    return JsonResponse({'ok': True, 'mock': {'id': m.id, 'title': m.title}})


@require_GET
def get_questions(request):
    """GET /api/get-questions/?company=google&difficulty=medium
    
    Returns 20 questions for the specified company and difficulty level.
    If fewer than 20 questions exist, returns all available.
    """
    company = request.GET.get('company', 'google')
    difficulty = request.GET.get('difficulty', 'medium')

    # Validate inputs
    valid_companies = ['google', 'openai', 'uber', 'microsoft']
    valid_difficulties = ['easy', 'medium', 'hard']

    if company not in valid_companies:
        return JsonResponse(
            {'ok': False, 'error': f'Invalid company. Valid options: {", ".join(valid_companies)}'}, 
            status=400
        )

    if difficulty not in valid_difficulties:
        return JsonResponse(
            {'ok': False, 'error': f'Invalid difficulty. Valid options: {", ".join(valid_difficulties)}'}, 
            status=400
        )

    try:
        # Fetch questions matching company and difficulty
        questions = Question.objects.filter(
            company=company,
            difficulty=difficulty
        ).order_by('?')[:20]  # Shuffle and limit to 20

        if not questions.exists():
            return JsonResponse(
                {'ok': True, 'questions': [], 'count': 0},
                status=200
            )

        # Serialize questions
        questions_data = [q.as_dict() for q in questions]

        return JsonResponse(
            {
                'ok': True,
                'questions': questions_data,
                'count': len(questions_data),
                'company': company,
                'difficulty': difficulty
            },
            status=200
        )

    except Exception as e:
        return JsonResponse(
            {'ok': False, 'error': str(e)},
            status=500
        )


@require_GET
def get_user_purchased_items(request, user_id):
    """GET /user/<user_id>/purchased-items/
    
    Returns all purchased items for a user.
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'user_not_found'}, status=404)

    from .models import PurchasedItem
    purchased_items = PurchasedItem.objects.filter(user=user).order_by('-purchased_at')
    items_data = [item.as_dict() for item in purchased_items]
    
    return JsonResponse({
        'ok': True,
        'purchased_items': items_data,
        'count': len(items_data)
    })


@require_GET
def get_user_test_results(request, user_id):
    """GET /user/<user_id>/test-results/
    
    Returns all test results for a user.
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'user_not_found'}, status=404)

    from .models import TestResult
    test_results = TestResult.objects.filter(user=user).order_by('-attempt_date')
    results_data = [result.as_dict() for result in test_results]
    
    return JsonResponse({
        'ok': True,
        'test_results': results_data,
        'count': len(results_data)
    })
