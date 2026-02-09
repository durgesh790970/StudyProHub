#!/usr/bin/env python
"""
Database Viewer Script - SQLite से सभी users को देखने के लिए
Run करने के लिए: python view_users_db.py
"""

import sqlite3
from datetime import datetime
import os

DB_PATH = "db.sqlite3"  # Database file का path

def view_all_users():
    """SQLite database से सभी users को fetch करता है"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file नहीं मिला: {DB_PATH}")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Django User table से data निकालो
        cursor.execute('''
            SELECT id, username, email, first_name, date_joined 
            FROM auth_user 
            ORDER BY date_joined DESC
        ''')
        
        users = cursor.fetchall()
        
        if users:
            print("\n" + "="*100)
            print("📊 ALL REGISTERED USERS".center(100))
            print("="*100)
            print(f"\n✅ Total Users: {len(users)}\n")
            
            # Header
            print(f"{'ID':<5} | {'Email':<35} | {'Full Name':<20} | {'Joined Date':<25}")
            print("-" * 100)
            
            # Data
            for user in users:
                user_id, username, email, fullname, date_joined = user
                # Format date
                try:
                    date_obj = datetime.fromisoformat(date_joined.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime("%d-%m-%Y %H:%M:%S")
                except:
                    formatted_date = date_joined
                
                print(f"{user_id:<5} | {email:<35} | {fullname:<20} | {formatted_date:<25}")
            
            print("-" * 100)
            print(f"\n✅ कुल Users: {len(users)}")
            
        else:
            print("\n❌ कोई users नहीं मिले!")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def view_user_details():
    """किसी एक user की पूरी details देखता है"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file नहीं मिला: {DB_PATH}")
        return
    
    try:
        email = input("\nEmail address दर्ज करें: ").strip()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # User को find करो
        cursor.execute('''
            SELECT id, username, email, first_name, date_joined 
            FROM auth_user 
            WHERE email = ?
        ''', (email,))
        
        user = cursor.fetchone()
        
        if user:
            user_id, username, fullname_or_username, fullname, date_joined = user
            
            print("\n" + "="*50)
            print("👤 USER DETAILS".center(50))
            print("="*50)
            print(f"ID: {user_id}")
            print(f"Email: {email}")
            print(f"Username: {username}")
            print(f"Full Name: {fullname or 'Not Set'}")
            print(f"Joined: {date_joined}")
            
            # UserProfile से extra details निकालो
            cursor.execute('''
                SELECT phone, has_paid, created_at 
                FROM accounts_userprofile 
                WHERE auth_user_id = ?
            ''', (user_id,))
            
            profile = cursor.fetchone()
            if profile:
                phone, has_paid, profile_created = profile
                print(f"\nPhone: {phone or 'Not Set'}")
                print(f"Payment Status: {'✅ PAID' if has_paid else '❌ NOT PAID'}")
                print(f"Profile Created: {profile_created}")
            else:
                print("\n⚠️  No additional profile data found")
            
            print("="*50 + "\n")
        else:
            print(f"\n❌ Email '{email}' से कोई user नहीं मिला!")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def get_user_count():
    """कुल users की संख्या दिखाता है"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file नहीं मिला: {DB_PATH}")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM auth_user')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM accounts_userprofile')
        profiles = cursor.fetchone()[0]
        
        print(f"\n📊 Database Statistics:")
        print(f"   Total Auth Users: {total}")
        print(f"   User Profiles: {profiles}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("🗄️  SQLite USER DATABASE VIEWER".center(50))
    print("="*50)
    
    while True:
        print("\n📌 विकल्प चुनें:")
        print("1. सभी Users देखें")
        print("2. किसी User की Details देखें")
        print("3. Database Statistics")
        print("4. Exit")
        
        choice = input("\nअपनी पसंद दर्ज करें (1-4): ").strip()
        
        if choice == "1":
            view_all_users()
        elif choice == "2":
            view_user_details()
        elif choice == "3":
            get_user_count()
        elif choice == "4":
            print("\n👋 Thank you! Goodbye!\n")
            break
        else:
            print("❌ Invalid choice! कृपया 1-4 के बीच चुनें।")
