#!/usr/bin/env python
"""
Run Django migrations to set up database
"""
import os
import sys
import django

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djproject.settings')
django.setup()

# Import Django management
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    # Create migrations
    print("Creating migrations...")
    execute_from_command_line(['manage.py', 'makemigrations', 'accounts'])
    
    # Apply migrations
    print("\nApplying migrations...")
    execute_from_command_line(['manage.py', 'migrate', 'accounts'])
    
    print("\n✅ Database migrations completed successfully!")
