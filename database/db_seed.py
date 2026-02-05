"""
Simple seeder to populate sample Video and PDF entries into the MongoDB database
using Django's ORM. Run this with the Django context:

    python manage.py shell < db_seed.py

Or import and run the `run()` function from a Django shell.

This file is intentionally stand-alone and uses django setup when executed as script.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djproject.settings')
django.setup()

from accounts.models import Video, PDF


def run():
    print('Seeding sample videos and pdfs...')
    Video.objects.all().delete()
    PDF.objects.all().delete()

    videos = [
        {'title': 'Sample Video 1', 'youtube_id': 'dQw4w9WgXcQ'},
        {'title': 'Sample Video 2', 'youtube_id': '9bZkp7q19f0'},
        {'title': 'Sample Video 3', 'youtube_id': '3JZ_D3ELwOQ'},
    ]
    for v in videos:
        Video.objects.create(**v)

    pdfs = [
        {'company': 'Acme', 'title': 'Acme - Sample Paper', 'file_url': 'https://example.com/acme-sample.pdf'},
        {'company': 'Globex', 'title': 'Globex - Test Paper', 'file_url': 'https://example.com/globex-test.pdf'},
    ]
    for p in pdfs:
        PDF.objects.create(**p)

    print('Done seeding.')


if __name__ == '__main__':
    run()
