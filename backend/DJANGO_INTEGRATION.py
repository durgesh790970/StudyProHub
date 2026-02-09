"""
Django Integration Examples
How to use the SQLite database with Django

Since you have Django running, here are examples of integration:
1. In Django views
2. In management commands  
3. In Django shell
4. In signals
5. In API endpoints
"""

# ============================================================================
# OPTION 1: USE IN DJANGO VIEWS
# ============================================================================

# File: accounts/views.py
from django.shortcuts import render
from django.http import JsonResponse
from db import (
    initialize_db,
    add_student,
    get_student,
    get_all_students,
    update_student,
    delete_student,
)
import sqlite3


def student_list_view(request):
    """
    GET: Return all students as JSON
    This demonstrates reading from SQLite in a view
    """
    try:
        students = get_all_students()
        
        return JsonResponse({
            'success': True,
            'count': len(students),
            'students': students
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def student_detail_view(request, student_id):
    """
    GET: Return single student
    This demonstrates reading a single record
    """
    try:
        student = get_student(student_id)
        
        if not student:
            return JsonResponse({
                'success': False,
                'error': 'Student not found'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'student': student
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def create_student_view(request):
    """
    POST: Create a new student
    This demonstrates creating a record from form data
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        name = request.POST.get('name')
        email = request.POST.get('email')
        cgpa = float(request.POST.get('cgpa', 0.0))
        phone = request.POST.get('phone', None)
        
        # Validate
        if not name or not email:
            return JsonResponse({
                'success': False,
                'error': 'Name and email are required'
            }, status=400)
        
        # Create
        student_id = add_student(name, email, cgpa, phone)
        
        return JsonResponse({
            'success': True,
            'student_id': student_id,
            'message': 'Student created successfully'
        }, status=201)
        
    except sqlite3.IntegrityError:
        return JsonResponse({
            'success': False,
            'error': 'Email already exists'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def update_student_view(request, student_id):
    """
    PUT/POST: Update student information
    This demonstrates updating a record
    """
    if request.method not in ['PUT', 'POST']:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Check if student exists
        student = get_student(student_id)
        if not student:
            return JsonResponse({
                'success': False,
                'error': 'Student not found'
            }, status=404)
        
        # Get update fields
        updates = {}
        
        if 'name' in request.POST:
            updates['name'] = request.POST.get('name')
        if 'cgpa' in request.POST:
            updates['cgpa'] = float(request.POST.get('cgpa'))
        if 'phone' in request.POST:
            updates['phone'] = request.POST.get('phone')
        if 'status' in request.POST:
            updates['status'] = request.POST.get('status')
        
        # Update
        if updates:
            update_student(student_id, **updates)
        
        return JsonResponse({
            'success': True,
            'message': 'Student updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def delete_student_view(request, student_id):
    """
    DELETE: Remove a student
    This demonstrates deleting a record
    """
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        success = delete_student(student_id)
        
        if not success:
            return JsonResponse({
                'success': False,
                'error': 'Student not found'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'message': 'Student deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# URLs for the views above
# File: accounts/urls.py (add these)
"""
from django.urls import path
from . import views

urlpatterns = [
    # Student API endpoints
    path('api/students/', views.student_list_view, name='student_list'),
    path('api/students/create/', views.create_student_view, name='create_student'),
    path('api/students/<int:student_id>/', views.student_detail_view, name='student_detail'),
    path('api/students/<int:student_id>/update/', views.update_student_view, name='update_student'),
    path('api/students/<int:student_id>/delete/', views.delete_student_view, name='delete_student'),
]
"""


# ============================================================================
# OPTION 2: USE IN MANAGEMENT COMMANDS
# ============================================================================

# File: accounts/management/commands/sync_db.py
from django.core.management.base import BaseCommand
from db import initialize_db, add_student, get_all_students


class Command(BaseCommand):
    help = 'Initialize SQLite database and sync data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset database (delete all data)',
        )
        parser.add_argument(
            '--sample',
            action='store_true',
            help='Add sample data',
        )
    
    def handle(self, *args, **options):
        # Initialize database
        self.stdout.write('Initializing database...')
        initialize_db()
        
        # Add sample data if requested
        if options['sample']:
            self.stdout.write('Adding sample data...')
            add_student('Rahul Kumar', 'rahul@example.com', 9.2)
            add_student('Priya Singh', 'priya@example.com', 9.5)
            add_student('Amit Patel', 'amit@example.com', 8.8)
        
        # Show statistics
        students = get_all_students()
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Database ready! Total students: {len(students)}'
            )
        )


# Run with:
# python manage.py sync_db
# python manage.py sync_db --sample
# python manage.py sync_db --reset


# ============================================================================
# OPTION 3: USE IN DJANGO SHELL
# ============================================================================

# Run interactive Django shell:
# python manage.py shell

# Then in shell:
"""
>>> from db import *
>>> initialize_db()
>>> 
>>> # Add student
>>> sid = add_student('John Doe', 'john@example.com', 9.5)
>>> 
>>> # Get student
>>> student = get_student(sid)
>>> print(student['name'])
John Doe
>>> 
>>> # List all
>>> students = get_all_students()
>>> len(students)
3
>>> 
>>> # Update
>>> update_student(sid, cgpa=9.8)
>>> 
>>> # Delete
>>> delete_student(sid)
>>>
"""


# ============================================================================
# OPTION 4: USE IN DJANGO SIGNALS
# ============================================================================

# File: accounts/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from accounts.models import User  # Your Django User model
from db import add_student, delete_student, get_all_students


@receiver(post_save, sender=User)
def sync_user_to_sqlite(sender, instance, created, **kwargs):
    """
    Automatically add Django User to SQLite when created
    This keeps both databases in sync
    """
    if created:
        try:
            # Add to SQLite
            add_student(
                name=instance.first_name or instance.username,
                email=instance.email,
                phone=instance.profile.phone if hasattr(instance, 'profile') else None
            )
            print(f"✓ User {instance.email} synced to SQLite")
        except Exception as e:
            print(f"✗ Sync error: {e}")


@receiver(post_delete, sender=User)
def delete_user_from_sqlite(sender, instance, **kwargs):
    """
    Remove user from SQLite when deleted from Django
    """
    try:
        # Note: You'd need to store SQLite ID in Django User model
        # to implement proper deletion
        print(f"User {instance.email} deleted from Django")
    except Exception as e:
        print(f"Error: {e}")


# Register signals
# File: accounts/apps.py
"""
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        import accounts.signals  # Import signals when app loads
"""


# ============================================================================
# OPTION 5: USE IN REST API (Django REST Framework)
# ============================================================================

# File: accounts/serializers.py
from rest_framework import serializers


class StudentSerializer(serializers.Serializer):
    """Serializer for SQLite Student data"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField(required=False, allow_blank=True)
    cgpa = serializers.FloatField()
    status = serializers.CharField()
    enrollment_date = serializers.CharField()


# File: accounts/views.py (with DRF)
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from db import add_student, get_student, update_student, delete_student
from .serializers import StudentSerializer


@api_view(['GET', 'POST'])
def student_api(request):
    """
    GET: List all students
    POST: Create new student
    """
    if request.method == 'GET':
        from db import get_all_students
        students = get_all_students()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                student_id = add_student(
                    name=serializer.validated_data['name'],
                    email=serializer.validated_data['email'],
                    cgpa=serializer.validated_data.get('cgpa', 0.0),
                    phone=serializer.validated_data.get('phone')
                )
                return Response(
                    {'id': student_id},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def student_detail_api(request, pk):
    """
    GET: Retrieve student
    PUT: Update student
    DELETE: Delete student
    """
    if request.method == 'GET':
        student = get_student(pk)
        if student:
            serializer = StudentSerializer(student)
            return Response(serializer.data)
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'PUT':
        student = get_student(pk)
        if not student:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StudentSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            try:
                update_student(pk, **serializer.validated_data)
                updated = get_student(pk)
                return Response(StudentSerializer(updated).data)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if delete_student(pk):
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


# URL patterns
"""
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path('api/students/', views.student_api, name='student_list'),
    path('api/students/<int:pk>/', views.student_detail_api, name='student_detail'),
]
"""


# ============================================================================
# OPTION 6: USE IN CELERY TASKS (Async)
# ============================================================================

# File: accounts/tasks.py
from celery import shared_task
from db import add_student, get_student, update_student
import logging

logger = logging.getLogger(__name__)


@shared_task
def register_student_async(name, email, cgpa=0.0, phone=None):
    """
    Async task to register a student
    Useful for heavy operations
    """
    try:
        student_id = add_student(name, email, cgpa, phone)
        logger.info(f"✓ Student registered: {student_id}")
        return {'success': True, 'student_id': student_id}
    except Exception as e:
        logger.error(f"✗ Registration error: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def bulk_import_students(student_list):
    """
    Async task to import multiple students
    student_list: [{'name': '...', 'email': '...', 'cgpa': 9.5}, ...]
    """
    results = {
        'success': 0,
        'failed': 0,
        'errors': []
    }
    
    for student_data in student_list:
        try:
            add_student(**student_data)
            results['success'] += 1
        except Exception as e:
            results['failed'] += 1
            results['errors'].append({
                'student': student_data.get('email'),
                'error': str(e)
            })
    
    logger.info(f"Bulk import complete: {results['success']} success, {results['failed']} failed")
    return results


# Usage in views
@api_view(['POST'])
def bulk_import_view(request):
    """
    POST: Bulk import students
    Data: {'students': [{'name': '...', 'email': '...', ...}]}
    """
    students = request.data.get('students', [])
    
    # Queue async task
    task = bulk_import_students.delay(students)
    
    return Response({
        'task_id': task.id,
        'status': 'Processing...'
    })


# ============================================================================
# OPTION 7: USE IN FORMS & VIEWS
# ============================================================================

# File: accounts/forms.py
from django import forms


class StudentForm(forms.Form):
    """Django form for student data"""
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    cgpa = forms.FloatField(min_value=0.0, max_value=10.0, required=False)
    
    def clean_email(self):
        """Check if email already exists in SQLite"""
        from db import get_all_students
        
        email = self.cleaned_data['email']
        students = get_all_students()
        existing_emails = [s['email'] for s in students]
        
        if email in existing_emails:
            raise forms.ValidationError("This email is already registered")
        
        return email


# File: accounts/views.py
def student_form_view(request):
    """
    Handle student registration form
    """
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            # Save to SQLite
            student_id = add_student(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data.get('phone'),
                cgpa=form.cleaned_data.get('cgpa', 0.0)
            )
            
            return JsonResponse({
                'success': True,
                'student_id': student_id
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    
    else:
        form = StudentForm()
        return render(request, 'student_form.html', {'form': form})


# ============================================================================
# BEST PRACTICES FOR DJANGO + SQLITE
# ============================================================================

"""
✓ Initialize database in your Django ready() method or in settings

✓ Use try-except for all database operations

✓ Keep Django models separate from SQLite tables
  (Use SQLite for supplementary data)

✓ Don't mix SQLite with Django ORM transactions
  (Use them independently)

✓ Index frequently queried fields:
  - students.email
  - students.status
  - enrollments.student_id

✓ Use connection pooling for production

✓ Regular backups:
  cp project.db project.db.backup

✓ Use Django signals to keep databases in sync

✓ Document which data lives where
  (SQLite vs Django ORM)

✓ Test migrations separately
"""


# ============================================================================
# STARTUP INITIALIZATION
# ============================================================================

# File: djproject/settings.py
# Add at the end:

"""
# Initialize SQLite database on startup
import os
from db import initialize_db

# Make sure project.db is created
if os.path.exists(os.path.join(BASE_DIR, 'backend')):
    os.chdir(os.path.join(BASE_DIR, 'backend'))
    try:
        initialize_db()
    except Exception as e:
        print(f"Warning: Could not initialize SQLite: {e}")
    os.chdir(BASE_DIR)
"""

# File: accounts/apps.py
"""
from django.apps import AppConfig
import os

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        # Initialize SQLite database when Django starts
        try:
            os.chdir('backend')
            from db import initialize_db
            initialize_db()
            os.chdir('..')
        except Exception as e:
            print(f"SQLite initialization: {e}")
"""
