from django.urls import reverse

try:
    print('reverse("password_reset_confirm") ->', reverse('password_reset_confirm', kwargs={'uidb64':'uid','token':'tok'}))
except Exception as e:
    print('password_reset_confirm reverse failed:', type(e).__name__, e)

try:
    print('reverse("accounts:password_reset_confirm") ->', reverse('accounts:password_reset_confirm', kwargs={'uidb64':'uid','token':'tok'}))
except Exception as e:
    print('accounts:password_reset_confirm reverse failed:', type(e).__name__, e)
