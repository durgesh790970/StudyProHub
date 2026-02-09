from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Video, PDF


class Command(BaseCommand):
    help = 'Create sample superuser and seed videos/pdfs for local development.'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin@example.com')
        parser.add_argument('--password', default='adminpass')
        parser.add_argument('--first-name', default='Admin')

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        password = options['password']
        first_name = options['first_name']

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=username, password=password, first_name=first_name)
            self.stdout.write(self.style.SUCCESS(f'Created superuser: {username}'))
        else:
            self.stdout.write(self.style.NOTICE(f'superuser {username} already exists'))

        # Create sample videos
        sample_videos = [
            {'title': 'Intro to Algorithms', 'video_id': 'dQw4w9WgXcQ'},
            {'title': 'System Design Basics', 'video_id': 'M7FIvfx5J10'},
        ]
        for sv in sample_videos:
            Video.objects.get_or_create(title=sv['title'], video_id=sv['video_id'])

        # Create sample PDFs
        sample_pdfs = [
            {'title': 'Acme Interview Questions', 'url': 'https://example.com/acme.pdf', 'company': 'Acme'},
            {'title': 'Capgemini Papers', 'url': 'https://example.com/capg.pdf', 'company': 'Capgemini'},
        ]
        for sp in sample_pdfs:
            PDF.objects.get_or_create(title=sp['title'], url=sp['url'], company=sp['company'])

        self.stdout.write(self.style.SUCCESS('Seeded sample videos and PDFs.'))
