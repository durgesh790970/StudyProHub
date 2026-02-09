"""
Database Seed Script
====================

Inserts sample data into the SQLite database for development and testing.
Includes sample users, profiles, transactions, and activity logs.

Run: python backend/seeds/seed.py
"""

import sys
from pathlib import Path
import hashlib
import json
from datetime import datetime, timedelta

# Add backend to path
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from config.db import (
    initialize_database, 
    insert_record, 
    get_all_records,
    get_database_info,
    verify_database
)

# ============================================================================
# PASSWORD HASHING UTILITY
# ============================================================================

def hash_password(password):
    """
    Hash password using SHA256 (for demo - use bcrypt in production).
    
    Args:
        password (str): Plain text password
    
    Returns:
        str: Hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()


# ============================================================================
# SAMPLE DATA
# ============================================================================

SAMPLE_USERS = [
    {
        'full_name': 'Admin User',
        'email': 'admin@studypro.com',
        'password_hash': hash_password('Admin123!@'),
        'phone': '+91-9999999999',
        'role': 'admin',
        'is_active': 1
    },
    {
        'full_name': 'Raj Kumar',
        'email': 'raj.kumar@gmail.com',
        'password_hash': hash_password('Raj@12345'),
        'phone': '+91-9876543210',
        'role': 'user',
        'is_active': 1
    },
    {
        'full_name': 'Priya Singh',
        'email': 'priya.singh@gmail.com',
        'password_hash': hash_password('Priya@12345'),
        'phone': '+91-9765432109',
        'role': 'user',
        'is_active': 1
    },
    {
        'full_name': 'Amit Patel',
        'email': 'amit.patel@gmail.com',
        'password_hash': hash_password('Amit@12345'),
        'phone': '+91-9654321098',
        'role': 'user',
        'is_active': 1
    },
    {
        'full_name': 'Neha Sharma',
        'email': 'neha.sharma@gmail.com',
        'password_hash': hash_password('Neha@12345'),
        'phone': '+91-9543210987',
        'role': 'user',
        'is_active': 1
    },
    {
        'full_name': 'Rahul Verma',
        'email': 'rahul.verma@gmail.com',
        'password_hash': hash_password('Rahul@12345'),
        'phone': '+91-9432109876',
        'role': 'user',
        'is_active': 1
    },
]

SAMPLE_PROFILES = [
    {
        'user_id': 1,
        'address': '123 Admin Street',
        'city': 'Delhi',
        'state': 'Delhi',
        'pincode': '110001',
        'date_of_birth': '1990-05-15',
        'gender': 'Male',
        'bio': 'Platform Administrator',
        'phone_verified': 1
    },
    {
        'user_id': 2,
        'address': '456 Raj Nagar',
        'city': 'Bangalore',
        'state': 'Karnataka',
        'pincode': '560001',
        'date_of_birth': '1998-07-22',
        'gender': 'Male',
        'bio': 'Software Engineer | Interview Prep',
        'phone_verified': 1
    },
    {
        'user_id': 3,
        'address': '789 Priya Complex',
        'city': 'Mumbai',
        'state': 'Maharashtra',
        'pincode': '400001',
        'date_of_birth': '1997-03-10',
        'gender': 'Female',
        'bio': 'Data Analyst | Learning & Development',
        'phone_verified': 1
    },
    {
        'user_id': 4,
        'address': '321 Amit Plaza',
        'city': 'Hyderabad',
        'state': 'Telangana',
        'pincode': '500001',
        'date_of_birth': '1996-11-28',
        'gender': 'Male',
        'bio': 'Product Manager Aspirant',
        'phone_verified': 0
    },
    {
        'user_id': 5,
        'address': '654 Neha Heights',
        'city': 'Pune',
        'state': 'Maharashtra',
        'pincode': '411001',
        'date_of_birth': '1999-09-14',
        'gender': 'Female',
        'bio': 'Full Stack Developer',
        'phone_verified': 1
    },
    {
        'user_id': 6,
        'address': '987 Rahul Mansion',
        'city': 'Chennai',
        'state': 'Tamil Nadu',
        'pincode': '600001',
        'date_of_birth': '1995-01-30',
        'gender': 'Male',
        'bio': 'DevOps Engineer | Cloud Enthusiast',
        'phone_verified': 1
    },
]

SAMPLE_TRANSACTIONS = [
    {
        'user_id': 2,
        'amount': 499.00,
        'payment_method': 'credit_card',
        'transaction_id': 'TXN001_RAJ_20240115',
        'status': 'success',
        'description': 'Premium Plan Subscription - 3 Months',
        'currency': 'INR'
    },
    {
        'user_id': 3,
        'amount': 999.00,
        'payment_method': 'debit_card',
        'transaction_id': 'TXN002_PRIYA_20240114',
        'status': 'success',
        'description': 'Pro Plan Subscription - 6 Months',
        'currency': 'INR'
    },
    {
        'user_id': 4,
        'amount': 299.00,
        'payment_method': 'upi',
        'transaction_id': 'TXN003_AMIT_20240113',
        'status': 'pending',
        'description': 'Basic Plan Subscription - 1 Month',
        'currency': 'INR'
    },
    {
        'user_id': 5,
        'amount': 1999.00,
        'payment_method': 'net_banking',
        'transaction_id': 'TXN004_NEHA_20240112',
        'status': 'success',
        'description': 'Enterprise Plan Subscription - 1 Year',
        'currency': 'INR'
    },
    {
        'user_id': 6,
        'amount': 499.00,
        'payment_method': 'credit_card',
        'transaction_id': 'TXN005_RAHUL_20240111',
        'status': 'success',
        'description': 'Premium Plan Subscription - 3 Months',
        'currency': 'INR'
    },
    {
        'user_id': 2,
        'amount': 199.00,
        'payment_method': 'upi',
        'transaction_id': 'TXN006_RAJ_20240110',
        'status': 'failed',
        'description': 'Mock Test Package Purchase',
        'currency': 'INR'
    },
]

SAMPLE_ACTIVITY_LOGS = [
    {
        'user_id': 1,
        'activity': 'Admin login',
        'activity_type': 'login',
        'ip_address': '192.168.1.100',
        'details': 'Successful admin login'
    },
    {
        'user_id': 2,
        'activity': 'User signup',
        'activity_type': 'signup',
        'ip_address': '203.0.113.45',
        'details': 'New user registration completed'
    },
    {
        'user_id': 2,
        'activity': 'User login',
        'activity_type': 'login',
        'ip_address': '203.0.113.45',
        'details': 'Successful user login'
    },
    {
        'user_id': 2,
        'activity': 'Quiz attempted - Aptitude',
        'activity_type': 'quiz_attempt',
        'ip_address': '203.0.113.45',
        'details': 'Aptitude quiz started - 15 minute test'
    },
    {
        'user_id': 2,
        'activity': 'Quiz submitted - Aptitude',
        'activity_type': 'quiz_submit',
        'ip_address': '203.0.113.45',
        'details': 'Aptitude quiz completed with score 28/30'
    },
    {
        'user_id': 3,
        'activity': 'User signup',
        'activity_type': 'signup',
        'ip_address': '198.51.100.82',
        'details': 'New user registration completed'
    },
    {
        'user_id': 3,
        'activity': 'Profile updated',
        'activity_type': 'profile_update',
        'ip_address': '198.51.100.82',
        'details': 'User profile information updated'
    },
    {
        'user_id': 3,
        'activity': 'Quiz attempted - Technical',
        'activity_type': 'quiz_attempt',
        'ip_address': '198.51.100.82',
        'details': 'Technical quiz started - Java section'
    },
    {
        'user_id': 4,
        'activity': 'User signup',
        'activity_type': 'signup',
        'ip_address': '192.0.2.123',
        'details': 'New user registration completed'
    },
    {
        'user_id': 5,
        'activity': 'User login',
        'activity_type': 'login',
        'ip_address': '198.51.100.99',
        'details': 'Successful user login'
    },
    {
        'user_id': 5,
        'activity': 'Interview session started',
        'activity_type': 'interview_start',
        'ip_address': '198.51.100.99',
        'details': 'Mock interview session for HR round'
    },
    {
        'user_id': 6,
        'activity': 'User login',
        'activity_type': 'login',
        'ip_address': '203.0.113.200',
        'details': 'Successful user login'
    },
]


# ============================================================================
# SEED FUNCTIONS
# ============================================================================

def seed_users():
    """Insert sample users into the database."""
    print("\n📝 Seeding Users...")
    user_ids = []
    
    for user in SAMPLE_USERS:
        user_id = insert_record('users', user)
        user_ids.append(user_id)
        print(f"  ✅ Added user: {user['full_name']} (ID: {user_id})")
    
    return user_ids


def seed_profiles():
    """Insert sample user profiles into the database."""
    print("\n👤 Seeding User Profiles...")
    
    for profile in SAMPLE_PROFILES:
        profile_id = insert_record('user_profiles', profile)
        print(f"  ✅ Added profile for user ID {profile['user_id']}")


def seed_transactions():
    """Insert sample transactions into the database."""
    print("\n💳 Seeding Transactions...")
    
    for transaction in SAMPLE_TRANSACTIONS:
        txn_id = insert_record('transactions', transaction)
        print(f"  ✅ Added transaction: {transaction['transaction_id']} (ID: {txn_id})")


def seed_activity_logs():
    """Insert sample activity logs into the database."""
    print("\n📊 Seeding Activity Logs...")
    
    # Add timestamps spread over the last 30 days
    base_time = datetime.now()
    
    for i, log in enumerate(SAMPLE_ACTIVITY_LOGS):
        # Spread logs over last 30 days
        days_ago = i % 30
        created_at = (base_time - timedelta(days=days_ago)).isoformat()
        log['created_at'] = created_at
        
        log_id = insert_record('activity_logs', log)
        print(f"  ✅ Added activity log: {log['activity']}")


def seed_settings():
    """Insert default settings into the database."""
    print("\n⚙️  Seeding Settings...")
    
    default_settings = [
        {
            'key': 'app_name',
            'value': 'StudyPro Hub',
            'description': 'Application name'
        },
        {
            'key': 'version',
            'value': '1.0.0',
            'description': 'Application version'
        },
        {
            'key': 'maintenance_mode',
            'value': 'false',
            'description': 'Enable/disable maintenance mode'
        },
        {
            'key': 'max_quiz_attempts',
            'value': '5',
            'description': 'Maximum quiz attempts per user'
        },
        {
            'key': 'quiz_time_limit_minutes',
            'value': '15',
            'description': 'Quiz time limit in minutes'
        },
    ]
    
    for setting in default_settings:
        setting_id = insert_record('settings', setting)
        print(f"  ✅ Added setting: {setting['key']}")


# ============================================================================
# MAIN SEED FUNCTION
# ============================================================================

def seed_database():
    """
    Run all seed functions to populate the database with sample data.
    """
    print("=" * 70)
    print("🌱 STARTING DATABASE SEEDING...")
    print("=" * 70)
    
    try:
        # Initialize database
        print("\n🗄️  Initializing database...")
        if initialize_database():
            print("  ✅ Database initialized successfully")
        else:
            print("  ⚠️  Database already exists or initialization warning")
        
        # Verify database
        if not verify_database():
            print("  ❌ Database verification failed")
            return False
        
        # Seed data
        seed_users()
        seed_profiles()
        seed_transactions()
        seed_activity_logs()
        seed_settings()
        
        # Display summary
        print("\n" + "=" * 70)
        print("✅ DATABASE SEEDING COMPLETED")
        print("=" * 70)
        
        info = get_database_info()
        print(f"\n📊 Database Summary:")
        print(f"  Database: {info['database']}")
        print(f"  Size: {info['file_size_kb']} KB")
        print(f"  Total Tables: {len(info['tables'])}")
        print(f"  Total Records: {info['total_records']}")
        print(f"\n  Record Count by Table:")
        for table, count in info['table_records'].items():
            print(f"    • {table}: {count}")
        
        print("\n🎯 Sample Data:")
        print(f"  • Users: {len(SAMPLE_USERS)}")
        print(f"  • Profiles: {len(SAMPLE_PROFILES)}")
        print(f"  • Transactions: {len(SAMPLE_TRANSACTIONS)}")
        print(f"  • Activity Logs: {len(SAMPLE_ACTIVITY_LOGS)}")
        
        print("\n🔐 Test Credentials (for development only):")
        print("  • Admin Email: admin@studypro.com")
        print("  • Admin Password: Admin123!@")
        print("  • User Email: raj.kumar@gmail.com")
        print("  • User Password: Raj@12345")
        
        print("\n✨ Database is ready for development!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Seeding error: {e}")
        return False


# ============================================================================
# RESET FUNCTION
# ============================================================================

def reset_and_seed():
    """
    Reset the database and reseed with sample data.
    Use with caution - this will delete all existing data!
    """
    print("⚠️  WARNING: This will delete all existing data!")
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response == 'yes':
        from config.db import reset_database
        
        print("\n🔄 Resetting database...")
        if reset_database():
            print("✅ Database reset successful")
            seed_database()
        else:
            print("❌ Database reset failed")
    else:
        print("Cancelled.")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Seed Script')
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset database before seeding (WARNING: deletes all data)'
    )
    
    args = parser.parse_args()
    
    if args.reset:
        reset_and_seed()
    else:
        seed_database()
