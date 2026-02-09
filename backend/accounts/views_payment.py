from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Transaction, User, PurchasedItem
from django.utils import timezone
import json

@csrf_exempt
@require_POST
def verify_transaction(request):
    try:
        data = json.loads(request.body)
        transaction_id = data.get('transactionId')
        company = data.get('company')
        amount = data.get('amount', 99.00)  # Get amount from request or use default
        pdf_name = data.get('pdfName') or company  # PDF name or company name
        
        if not transaction_id or not company:
            return JsonResponse({
                'ok': False,
                'error': 'Missing transaction ID or company'
            }, status=400)
            
        # Check if transaction ID already exists
        if Transaction.objects.filter(transaction_id=transaction_id).exists():
            return JsonResponse({
                'ok': False,
                'error': 'This transaction ID has already been used. Please enter a valid one.'
            }, status=400)
            
        # Create new transaction
        transaction = Transaction.objects.create(
            transaction_id=transaction_id,
            company=company,
            amount=amount
        )
        
        # Update user's paid companies if user is authenticated
        if request.user.is_authenticated:
            user = request.user
            paid_companies = user.paid_companies or {}
            paid_companies[company] = True
            user.paid_companies = paid_companies
            user.save()
            transaction.user = user
            transaction.save()
            
            # Record PurchasedItem in database
            try:
                PurchasedItem.objects.create(
                    user=user,
                    title=pdf_name,
                    item_type='pdf',
                    amount_paid=amount,
                    transaction_id=transaction_id,
                    purchased_at=timezone.now()
                )
            except Exception as e:
                print(f"Error creating PurchasedItem: {e}")
                # Don't fail the transaction if PurchasedItem creation fails
            
        return JsonResponse({
            'ok': True,
            'message': 'Payment verified successfully',
            'transactionId': transaction_id,
            'amount': float(amount)
        })
        
    except Exception as e:
        return JsonResponse({
            'ok': False,
            'error': str(e)
        }, status=500)