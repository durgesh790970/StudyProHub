#!/usr/bin/env python
"""
⚡ QUICK SETUP - User Registration Database
Run यह script एक बार करो। बाद में सब automatically काम करेगा।
"""

import os
import subprocess
import sys

def run_command(cmd, description):
    """Command को execute करता है"""
    print(f"\n📍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🚀 USER REGISTRATION DATABASE QUICK SETUP".center(60))
    print("="*60)
    
    print("\n📋 यह script करेगा:")
    print("  1️⃣  Database migrations")
    print("  2️⃣  Tables बनाएगा")
    print("  3️⃣  Setup complete करेगा")
    
    # Step 1: Migrations
    if not run_command(
        "python manage.py migrate",
        "Database Migrations"
    ):
        print("\n⚠️  Migrations failed. Continuing...")
    
    # Step 2: Create Superuser (Optional)
    print("\n" + "-"*60)
    create_admin = input("\n👤 क्या आप Admin Account बनाना चाहते हैं? (yes/no): ").strip().lower()
    
    if create_admin == 'yes':
        print("\n📝 Admin Account Details दर्ज करो:")
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        
        # Password prompt (masked)
        import getpass
        password = getpass.getpass("Password: ")
        
        cmd = f'python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser(\'{username}\', \'{email}\', \'{password}\') if not User.objects.filter(username=\'{username}\').exists() else print(\'User already exists\')"'
        
        if run_command(cmd, "Admin Account Creation"):
            print(f"\n✅ Admin Account Created!")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
    
    # Final steps
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!".center(60))
    print("="*60)
    
    print("\n📌 अगला Step:")
    print("\n1️⃣  Server शुरू करो:")
    print("   python manage.py runserver")
    
    print("\n2️⃣  Signup Page पर जाओ:")
    print("   http://localhost:8000/signup/")
    
    print("\n3️⃣  नया user register करो")
    
    print("\n4️⃣  Users को देखो (कोई एक तरीका):")
    print("   • Web Dashboard: http://localhost:8000/users-list/")
    print("   • Admin Panel: http://localhost:8000/admin/")
    print("   • Terminal: python view_users_db.py")
    
    print("\n📚 Details के लिए देखो: USER_REGISTRATION_GUIDE.md")
    print("="*60 + "\n")

if __name__ == "__main__":
    # Check if we're in the backend directory
    if not os.path.exists("manage.py"):
        print("\n❌ Error: Run यह script 'backend' folder से करो!")
        print("   cd backend")
        print("   python quick_setup.py")
        sys.exit(1)
    
    main()
