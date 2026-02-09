from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)


def send_result_email(email, name, test_name, score, total, accuracy, time_taken, rank, feedback):
    """Send a professional HTML result email to the user.

    Returns True on success, False on failure.
    """
    subject = f"{test_name} Results · StudyPro"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', 'no-reply@studypro.local')

    context = {
        'name': name or 'Candidate',
        'test_name': test_name,
        'score': score,
        'total': total,
        'accuracy': accuracy,
        'time_taken': time_taken,
        'rank': rank,
        'feedback': feedback,
        'brand_url': 'https://studypro.example.com',
        'brand_name': 'StudyPro',
    }

    # Render HTML body from template
    html_body = render_to_string('emails/result_email.html', context)

    # Compose and send
    try:
        text_body = render_to_string('emails/result_email.txt', context)
    except Exception:
        text_body = f"{test_name} results for {name}: {score}/{total} ({accuracy}%)\n{feedback}"

    try:
        msg = EmailMultiAlternatives(subject=subject, body=text_body, from_email=from_email, to=[email])
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        return True
    except Exception as e:
        logger.exception('Failed to send result email to %s: %s', email, e)
        return False
