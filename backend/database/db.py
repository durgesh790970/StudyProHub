"""
Database Connection and Configuration Module
Handles SQLite database connection, queries, and utility functions
"""

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime
import json

# Get the database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'app.db')

class DatabaseManager:
    """Manages SQLite database connections and operations"""
    
    def __init__(self, db_path=DB_PATH):
        """Initialize database manager"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with schema"""
        if not os.path.exists(self.db_path):
            # Silently create schema
            self.create_schema()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            # Silently handle database errors
            raise
        finally:
            conn.close()
    
    def create_schema(self):
        """Create database schema from schema.sql"""
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
        if not os.path.exists(schema_path):
            # Schema file missing - will use defaults
            return
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            with self.get_connection() as conn:
                # Remove PRAGMA foreign_keys line from script (handle separately)
                lines = schema_sql.split('\n')
                filtered_lines = [line for line in lines if not line.strip().startswith('PRAGMA')]
                filtered_sql = '\n'.join(filtered_lines)
                
                conn.executescript(filtered_sql)
            
            pass  # Schema created
        except Exception as e:
            import sys
            print(f"ERROR creating schema: {e}", file=sys.stderr)
            raise
    
    def seed_database(self):
        """Load sample data from seed.sql"""
        seed_path = os.path.join(os.path.dirname(__file__), 'seed.sql')
        
        if not os.path.exists(seed_path):
            # Seed file missing - skip seeding
            return
        
        try:
            with open(seed_path, 'r') as f:
                seed_sql = f.read()
            
            with self.get_connection() as conn:
                conn.executescript(seed_sql)
            # Sample data loaded successfully
        except Exception as e:
            # Error seeding database - not critical
            pass
    
    # ========================================================================
    # USER OPERATIONS
    # ========================================================================
    
    def create_user(self, email, username, password_hash, first_name, last_name=None, phone=None):
        """Create a new user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (email, username, password_hash, first_name, last_name, phone)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (email, username, password_hash, first_name, last_name, phone))
                
                user_id = cursor.lastrowid
                print(f"✅ User created with ID: {user_id}")
                return user_id
        except sqlite3.IntegrityError as e:
            print(f"❌ User creation failed: {str(e)}")
            return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_user(self, user_id, **kwargs):
        """Update user information"""
        try:
            allowed_fields = ['email', 'first_name', 'last_name', 'phone', 'is_active', 'is_verified']
            updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            if not updates:
                return False
            
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [user_id]
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'UPDATE users SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?', values)
            
            print(f"✅ User {user_id} updated successfully")
            return True
        except Exception as e:
            print(f"❌ Error updating user: {str(e)}")
            return False
    
    def get_all_users(self):
        """Get all users"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]
    
    # ========================================================================
    # USER PROFILE OPERATIONS
    # ========================================================================
    
    def create_user_profile(self, user_id, **kwargs):
        """Create user profile"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Build dynamic insert
                fields = ['user_id'] + list(kwargs.keys())
                placeholders = ', '.join(['?' for _ in fields])
                values = [user_id] + list(kwargs.values())
                
                cursor.execute(f'''
                    INSERT INTO user_profiles ({', '.join(fields)})
                    VALUES ({placeholders})
                ''', values)
            
            print(f"✅ Profile created for user {user_id}")
            return True
        except Exception as e:
            print(f"❌ Error creating profile: {str(e)}")
            return False
    
    def get_user_profile(self, user_id):
        """Get user profile"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_user_profile(self, user_id, **kwargs):
        """Update user profile"""
        try:
            allowed_fields = ['bio', 'profile_picture', 'date_of_birth', 'gender', 'address', 
                            'city', 'state', 'country', 'postal_code', 'college_name', 
                            'branch', 'semester', 'cgpa', 'resume_url', 'linkedin_url', 
                            'github_url', 'is_premium']
            
            updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            if not updates:
                return False
            
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [user_id]
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    UPDATE user_profiles 
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
                    WHERE user_id = ?
                ''', values)
            
            print(f"✅ Profile for user {user_id} updated")
            return True
        except Exception as e:
            print(f"❌ Error updating profile: {str(e)}")
            return False
    
    # ========================================================================
    # TRANSACTION OPERATIONS
    # ========================================================================
    
    def create_transaction(self, user_id, transaction_id, amount, **kwargs):
        """Create a transaction"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO transactions 
                    (user_id, transaction_id, amount, currency, payment_method, status, company_name, item_type, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, transaction_id, amount,
                    kwargs.get('currency', 'INR'),
                    kwargs.get('payment_method', 'card'),
                    kwargs.get('status', 'pending'),
                    kwargs.get('company_name', ''),
                    kwargs.get('item_type', ''),
                    kwargs.get('description', '')
                ))
            
            print(f"✅ Transaction {transaction_id} created")
            return True
        except Exception as e:
            print(f"❌ Error creating transaction: {str(e)}")
            return False
    
    def get_user_transactions(self, user_id):
        """Get all transactions for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM transactions 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            ''', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_transaction_status(self, transaction_id, status):
        """Update transaction status"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE transactions 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE transaction_id = ?
                ''', (status, transaction_id))
            
            print(f"✅ Transaction {transaction_id} status updated to {status}")
            return True
        except Exception as e:
            print(f"❌ Error updating transaction: {str(e)}")
            return False
    
    # ========================================================================
    # ACTIVITY LOG OPERATIONS
    # ========================================================================
    
    def log_activity(self, user_id, action_type, action_description=None, **kwargs):
        """Log user activity"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO activity_logs 
                    (user_id, action_type, action_description, resource_type, ip_address, status_code)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, action_type, action_description,
                    kwargs.get('resource_type'),
                    kwargs.get('ip_address'),
                    kwargs.get('status_code', 200)
                ))
            
            return True
        except Exception as e:
            print(f"❌ Error logging activity: {str(e)}")
            return False
    
    def get_user_activity(self, user_id, limit=50):
        """Get user activity logs"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM activity_logs 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    # ========================================================================
    # TEST RESULT OPERATIONS
    # ========================================================================
    
    def save_test_result(self, user_id, test_name, **kwargs):
        """Save test result"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO test_results 
                    (user_id, test_name, company, difficulty, total_questions, correct_answers, score_percent, time_taken_seconds)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, test_name,
                    kwargs.get('company'),
                    kwargs.get('difficulty'),
                    kwargs.get('total_questions', 0),
                    kwargs.get('correct_answers', 0),
                    kwargs.get('score_percent', 0),
                    kwargs.get('time_taken_seconds', 0)
                ))
            
            print(f"✅ Test result saved for user {user_id}")
            return True
        except Exception as e:
            print(f"❌ Error saving test result: {str(e)}")
            return False
    
    def get_user_test_results(self, user_id):
        """Get all test results for user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM test_results 
                WHERE user_id = ? 
                ORDER BY attempted_on DESC
            ''', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ========================================================================
    # STATISTICS AND REPORTING
    # ========================================================================
    
    def get_user_complete_info(self, user_id):
        """Get complete user information"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        profile = self.get_user_profile(user_id)
        transactions = self.get_user_transactions(user_id)
        test_results = self.get_user_test_results(user_id)
        
        return {
            'user': user,
            'profile': profile,
            'transactions': transactions,
            'test_results': test_results,
            'stats': {
                'total_transactions': len(transactions),
                'total_spent': sum(t['amount'] for t in transactions if t['status'] == 'success'),
                'tests_attempted': len(test_results),
                'avg_score': sum(t['score_percent'] for t in test_results) / len(test_results) if test_results else 0
            }
        }
    
    def get_database_stats(self):
        """Get overall database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Count users
            cursor.execute('SELECT COUNT(*) as count FROM users WHERE is_active = 1')
            stats['active_users'] = cursor.fetchone()['count']
            
            # Count total transactions
            cursor.execute('SELECT COUNT(*) as count FROM transactions WHERE status = "success"')
            stats['successful_transactions'] = cursor.fetchone()['count']
            
            # Total revenue
            cursor.execute('SELECT SUM(amount) as total FROM transactions WHERE status = "success"')
            stats['total_revenue'] = cursor.fetchone()['total'] or 0
            
            # Count test attempts
            cursor.execute('SELECT COUNT(*) as count FROM test_results')
            stats['test_attempts'] = cursor.fetchone()['count']
            
            # Premium users
            cursor.execute('SELECT COUNT(*) as count FROM user_profiles WHERE is_premium = 1')
            stats['premium_users'] = cursor.fetchone()['count']
            
            return stats
    
    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================
    
    def reset_database(self):
        """Reset database (for development only)"""
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                print("✅ Database deleted")
            
            self.create_schema()
            self.seed_database()
            print("✅ Database reset and seeded")
        except Exception as e:
            print(f"❌ Error resetting database: {str(e)}")
    
    def get_database_size(self):
        """Get database file size"""
        if os.path.exists(self.db_path):
            size_bytes = os.path.getsize(self.db_path)
            size_mb = size_bytes / (1024 * 1024)
            return f"{size_mb:.2f} MB"
        return "Database not found"


# Create global database instance
db = DatabaseManager()


# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_database():
    """Test database functionality"""
    print("\n" + "="*50)
    print("🧪 TESTING DATABASE")
    print("="*50)
    
    # Get stats
    stats = db.get_database_stats()
    print(f"\n📊 Database Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Get sample user
    user = db.get_user_by_email('john@example.com')
    if user:
        print(f"\n👤 Sample User: {user['first_name']} {user['last_name']} ({user['email']})")
        
        # Get user complete info
        complete_info = db.get_user_complete_info(user['id'])
        if complete_info:
            print(f"   Tests Attempted: {complete_info['stats']['tests_attempted']}")
            print(f"   Total Spent: ₹{complete_info['stats']['total_spent']}")
            print(f"   Avg Score: {complete_info['stats']['avg_score']:.2f}%")


if __name__ == '__main__':
    print("✅ Database module loaded successfully")
    test_database()
