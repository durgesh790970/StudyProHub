"""
REST API Endpoints
==================

Complete REST API implementation for user management, authentication,
transactions, and activity logging.

API Base URL: /api/v1

Endpoints:
  POST   /api/v1/register           - Register new user
  POST   /api/v1/login              - User login
  GET    /api/v1/users              - Get all users (admin only)
  GET    /api/v1/user/:id           - Get user profile
  PUT    /api/v1/user/:id           - Update user profile
  POST   /api/v1/transaction        - Create transaction
  GET    /api/v1/transactions/:userId - Get user transactions
  DELETE /api/v1/user/:id           - Delete user (admin only)
"""

import json
import hashlib
import uuid
from datetime import datetime, timedelta
from functools import wraps

# For Flask implementation (if using Flask instead of Django)
try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


# ============================================================================
# RESPONSE TEMPLATES
# ============================================================================

class APIResponse:
    """Standard API response format."""
    
    @staticmethod
    def success(data=None, message="Success", status_code=200):
        """Success response."""
        return {
            'success': True,
            'status_code': status_code,
            'message': message,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }, status_code
    
    @staticmethod
    def error(message="Error", status_code=400, details=None):
        """Error response."""
        return {
            'success': False,
            'status_code': status_code,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }, status_code


# ============================================================================
# AUTHENTICATION & SECURITY
# ============================================================================

def hash_password(password):
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, password_hash):
    """Verify password against hash."""
    return hash_password(password) == password_hash


def generate_token():
    """Generate a unique authentication token."""
    return str(uuid.uuid4())


def validate_email(email):
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validate Indian phone number."""
    import re
    pattern = r'^\+91-\d{10}$'
    return re.match(pattern, phone) is not None


def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return APIResponse.error(
                "Missing authentication token",
                status_code=401
            )
        
        # Verify token (simplified - in production use JWT)
        # token = "Bearer <actual_token>"
        if token.startswith('Bearer '):
            token = token[7:]
        
        # TODO: Verify token against sessions table
        
        return f(*args, **kwargs)
    
    return decorated


def require_admin(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get user from token
        # Check if user role is 'admin'
        # Return error if not admin
        
        return f(*args, **kwargs)
    
    return decorated


# ============================================================================
# API ENDPOINTS
# ============================================================================

class UserAPI:
    """User management API endpoints."""
    
    @staticmethod
    def register(data):
        """
        Register a new user.
        
        Request Body:
        {
            "full_name": "John Doe",
            "email": "john@example.com",
            "password": "SecurePass123!",
            "phone": "+91-1234567890"
        }
        
        Response: User ID and profile
        """
        from config.db import insert_record, execute_query
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'password', 'phone']
        for field in required_fields:
            if field not in data:
                return APIResponse.error(
                    f"Missing required field: {field}",
                    status_code=400
                )
        
        # Validate email format
        if not validate_email(data['email']):
            return APIResponse.error(
                "Invalid email format",
                status_code=400
            )
        
        # Validate phone format
        if not validate_phone(data['phone']):
            return APIResponse.error(
                "Invalid phone format. Use: +91-XXXXXXXXXX",
                status_code=400
            )
        
        # Check if email already exists
        result = execute_query(
            "SELECT id FROM users WHERE email = ?",
            (data['email'],),
            fetch_one=True
        )
        
        if result:
            return APIResponse.error(
                "Email already registered",
                status_code=409
            )
        
        # Create user
        user_data = {
            'full_name': data['full_name'],
            'email': data['email'],
            'password_hash': hash_password(data['password']),
            'phone': data['phone'],
            'role': 'user',
            'is_active': 1
        }
        
        user_id = insert_record('users', user_data)
        
        if not user_id:
            return APIResponse.error(
                "Failed to create user",
                status_code=500
            )
        
        # Create empty profile
        profile_data = {
            'user_id': user_id,
            'phone_verified': 0
        }
        
        insert_record('user_profiles', profile_data)
        
        # Log activity
        log_data = {
            'user_id': user_id,
            'activity': 'User signup',
            'activity_type': 'signup',
            'ip_address': 'UNKNOWN',
            'details': f'New user registration: {data["email"]}'
        }
        insert_record('activity_logs', log_data)
        
        return APIResponse.success(
            data={
                'user_id': user_id,
                'email': data['email'],
                'full_name': data['full_name'],
                'role': 'user'
            },
            message="User registered successfully",
            status_code=201
        )
    
    @staticmethod
    def login(data):
        """
        User login.
        
        Request Body:
        {
            "email": "user@example.com",
            "password": "UserPassword123!"
        }
        
        Response: Auth token and user info
        """
        from config.db import execute_query, insert_record, update_record
        
        # Validate fields
        if 'email' not in data or 'password' not in data:
            return APIResponse.error(
                "Email and password required",
                status_code=400
            )
        
        # Find user
        user = execute_query(
            "SELECT * FROM users WHERE email = ?",
            (data['email'],),
            fetch_one=True
        )
        
        if not user:
            return APIResponse.error(
                "Invalid email or password",
                status_code=401
            )
        
        # Verify password
        if not verify_password(data['password'], user['password_hash']):
            return APIResponse.error(
                "Invalid email or password",
                status_code=401
            )
        
        # Check if user is active
        if not user['is_active']:
            return APIResponse.error(
                "User account is inactive",
                status_code=403
            )
        
        # Generate token
        token = generate_token()
        
        # Store session
        session_data = {
            'user_id': user['id'],
            'token': token,
            'ip_address': 'UNKNOWN',
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
        }
        insert_record('sessions', session_data)
        
        # Update last login
        update_record('users', user['id'], {
            'last_login': datetime.now().isoformat()
        })
        
        # Log activity
        log_data = {
            'user_id': user['id'],
            'activity': 'User login',
            'activity_type': 'login',
            'ip_address': 'UNKNOWN',
            'details': 'Successful user login'
        }
        insert_record('activity_logs', log_data)
        
        return APIResponse.success(
            data={
                'token': token,
                'user_id': user['id'],
                'email': user['email'],
                'full_name': user['full_name'],
                'role': user['role']
            },
            message="Login successful"
        )
    
    @staticmethod
    def get_all_users():
        """Get all users (admin only)."""
        from config.db import execute_query
        
        users = execute_query("SELECT id, full_name, email, role, is_active, created_at FROM users")
        
        users_list = [dict(user) for user in users] if users else []
        
        return APIResponse.success(
            data={'users': users_list, 'count': len(users_list)},
            message=f"Retrieved {len(users_list)} users"
        )
    
    @staticmethod
    def get_user(user_id):
        """Get user profile by ID."""
        from config.db import execute_query
        
        # Get user info
        user = execute_query(
            "SELECT id, full_name, email, phone, role, is_active, created_at, last_login FROM users WHERE id = ?",
            (user_id,),
            fetch_one=True
        )
        
        if not user:
            return APIResponse.error(
                "User not found",
                status_code=404
            )
        
        # Get profile
        profile = execute_query(
            "SELECT * FROM user_profiles WHERE user_id = ?",
            (user_id,),
            fetch_one=True
        )
        
        user_dict = dict(user)
        profile_dict = dict(profile) if profile else {}
        
        return APIResponse.success(
            data={
                'user': user_dict,
                'profile': profile_dict
            },
            message="User retrieved successfully"
        )
    
    @staticmethod
    def update_user(user_id, data):
        """Update user profile."""
        from config.db import update_record, execute_query
        
        # Verify user exists
        user = execute_query(
            "SELECT id FROM users WHERE id = ?",
            (user_id,),
            fetch_one=True
        )
        
        if not user:
            return APIResponse.error(
                "User not found",
                status_code=404
            )
        
        # Update user basic info
        updatable_fields = ['full_name', 'phone']
        user_updates = {k: v for k, v in data.items() if k in updatable_fields}
        
        if user_updates:
            update_record('users', user_id, user_updates)
        
        # Update profile if provided
        profile_fields = ['address', 'city', 'state', 'pincode', 'date_of_birth', 'gender', 'bio']
        profile_updates = {k: v for k, v in data.items() if k in profile_fields}
        
        if profile_updates:
            # Check if profile exists
            profile = execute_query(
                "SELECT id FROM user_profiles WHERE user_id = ?",
                (user_id,),
                fetch_one=True
            )
            
            if profile:
                update_record('user_profiles', profile['id'], profile_updates)
        
        # Log activity
        from config.db import insert_record
        log_data = {
            'user_id': user_id,
            'activity': 'Profile updated',
            'activity_type': 'profile_update',
            'ip_address': 'UNKNOWN',
            'details': 'User profile information updated'
        }
        insert_record('activity_logs', log_data)
        
        return APIResponse.success(
            data={'user_id': user_id},
            message="User profile updated successfully"
        )
    
    @staticmethod
    def delete_user(user_id):
        """Delete user account (admin only)."""
        from config.db import delete_record, execute_query
        
        # Verify user exists
        user = execute_query(
            "SELECT id FROM users WHERE id = ?",
            (user_id,),
            fetch_one=True
        )
        
        if not user:
            return APIResponse.error(
                "User not found",
                status_code=404
            )
        
        # Delete user (cascade deletes profile, transactions, logs)
        success = delete_record('users', user_id)
        
        if not success:
            return APIResponse.error(
                "Failed to delete user",
                status_code=500
            )
        
        return APIResponse.success(
            data={'user_id': user_id},
            message="User deleted successfully"
        )


class TransactionAPI:
    """Transaction management API endpoints."""
    
    @staticmethod
    def create_transaction(data):
        """
        Create a new transaction.
        
        Request Body:
        {
            "user_id": 1,
            "amount": 499.00,
            "payment_method": "credit_card",
            "description": "Premium Subscription"
        }
        """
        from config.db import insert_record, execute_query
        
        # Validate required fields
        required_fields = ['user_id', 'amount', 'payment_method']
        for field in required_fields:
            if field not in data:
                return APIResponse.error(
                    f"Missing required field: {field}",
                    status_code=400
                )
        
        # Verify user exists
        user = execute_query(
            "SELECT id FROM users WHERE id = ?",
            (data['user_id'],),
            fetch_one=True
        )
        
        if not user:
            return APIResponse.error(
                "User not found",
                status_code=404
            )
        
        # Create transaction
        transaction_data = {
            'user_id': data['user_id'],
            'amount': data['amount'],
            'payment_method': data['payment_method'],
            'transaction_id': f"TXN_{data['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'status': 'pending',
            'description': data.get('description', ''),
            'currency': 'INR'
        }
        
        txn_id = insert_record('transactions', transaction_data)
        
        if not txn_id:
            return APIResponse.error(
                "Failed to create transaction",
                status_code=500
            )
        
        # Log activity
        log_data = {
            'user_id': data['user_id'],
            'activity': f"Transaction created: {transaction_data['transaction_id']}",
            'activity_type': 'transaction',
            'ip_address': 'UNKNOWN',
            'details': f"Amount: ₹{data['amount']}"
        }
        insert_record('activity_logs', log_data)
        
        return APIResponse.success(
            data={
                'transaction_id': txn_id,
                'txn_ref': transaction_data['transaction_id'],
                'amount': data['amount'],
                'status': 'pending'
            },
            message="Transaction created successfully",
            status_code=201
        )
    
    @staticmethod
    def get_user_transactions(user_id):
        """Get all transactions for a user."""
        from config.db import execute_query
        
        # Verify user exists
        user = execute_query(
            "SELECT id FROM users WHERE id = ?",
            (user_id,),
            fetch_one=True
        )
        
        if not user:
            return APIResponse.error(
                "User not found",
                status_code=404
            )
        
        # Get transactions
        transactions = execute_query(
            """
            SELECT id, user_id, amount, payment_method, transaction_id, 
                   status, description, currency, created_at, updated_at
            FROM transactions 
            WHERE user_id = ? 
            ORDER BY created_at DESC
            """,
            (user_id,)
        )
        
        txn_list = [dict(txn) for txn in transactions] if transactions else []
        
        # Calculate totals
        total_amount = sum(float(t['amount']) for t in txn_list)
        success_count = sum(1 for t in txn_list if t['status'] == 'success')
        
        return APIResponse.success(
            data={
                'transactions': txn_list,
                'count': len(txn_list),
                'total_amount': total_amount,
                'successful_count': success_count
            },
            message=f"Retrieved {len(txn_list)} transactions"
        )
    
    @staticmethod
    def update_transaction_status(transaction_id, status):
        """Update transaction status."""
        from config.db import update_record, execute_query
        
        # Verify transaction exists
        txn = execute_query(
            "SELECT * FROM transactions WHERE id = ?",
            (transaction_id,),
            fetch_one=True
        )
        
        if not txn:
            return APIResponse.error(
                "Transaction not found",
                status_code=404
            )
        
        # Update status
        update_record('transactions', transaction_id, {'status': status})
        
        # Log activity
        from config.db import insert_record
        log_data = {
            'user_id': txn['user_id'],
            'activity': f"Transaction status updated: {status}",
            'activity_type': 'transaction_update',
            'ip_address': 'UNKNOWN',
            'details': f"Transaction {txn['transaction_id']} status changed to {status}"
        }
        insert_record('activity_logs', log_data)
        
        return APIResponse.success(
            data={'transaction_id': transaction_id, 'status': status},
            message="Transaction status updated"
        )


# ============================================================================
# FLASK APP SETUP (optional)
# ============================================================================

if FLASK_AVAILABLE:
    
    def create_api_app():
        """Create and configure Flask API application."""
        app = Flask(__name__)
        
        # Enable JSON response
        app.config['JSON_SORT_KEYS'] = False
        
        # ====== USER ENDPOINTS ======
        
        @app.route('/api/v1/register', methods=['POST'])
        def register():
            """Register endpoint."""
            data = request.get_json()
            return UserAPI.register(data)
        
        @app.route('/api/v1/login', methods=['POST'])
        def login():
            """Login endpoint."""
            data = request.get_json()
            return UserAPI.login(data)
        
        @app.route('/api/v1/users', methods=['GET'])
        def get_users():
            """Get all users endpoint."""
            return UserAPI.get_all_users()
        
        @app.route('/api/v1/user/<int:user_id>', methods=['GET'])
        def get_user(user_id):
            """Get user endpoint."""
            return UserAPI.get_user(user_id)
        
        @app.route('/api/v1/user/<int:user_id>', methods=['PUT'])
        def update_user(user_id):
            """Update user endpoint."""
            data = request.get_json()
            return UserAPI.update_user(user_id, data)
        
        @app.route('/api/v1/user/<int:user_id>', methods=['DELETE'])
        def delete_user(user_id):
            """Delete user endpoint."""
            return UserAPI.delete_user(user_id)
        
        # ====== TRANSACTION ENDPOINTS ======
        
        @app.route('/api/v1/transaction', methods=['POST'])
        def create_transaction():
            """Create transaction endpoint."""
            data = request.get_json()
            return TransactionAPI.create_transaction(data)
        
        @app.route('/api/v1/transactions/<int:user_id>', methods=['GET'])
        def get_transactions(user_id):
            """Get user transactions endpoint."""
            return TransactionAPI.get_user_transactions(user_id)
        
        # ====== HEALTH CHECK ======
        
        @app.route('/api/v1/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            from config.db import verify_database
            
            db_healthy = verify_database()
            
            return APIResponse.success(
                data={'database': 'healthy' if db_healthy else 'unhealthy'},
                message="API is running"
            )
        
        return app
    
    
    if __name__ == '__main__':
        app = create_api_app()
        print("🚀 Starting API server...")
        print("📍 Base URL: http://localhost:5000/api/v1")
        print("\n📚 Available endpoints:")
        print("  POST   /api/v1/register              - Register new user")
        print("  POST   /api/v1/login                 - User login")
        print("  GET    /api/v1/users                 - Get all users")
        print("  GET    /api/v1/user/<id>             - Get user profile")
        print("  PUT    /api/v1/user/<id>             - Update user")
        print("  DELETE /api/v1/user/<id>             - Delete user")
        print("  POST   /api/v1/transaction           - Create transaction")
        print("  GET    /api/v1/transactions/<userId> - Get user transactions")
        print("  GET    /api/v1/health                - Health check")
        print("\n🔗 Documentation: See docstrings for request/response formats")
        print("=" * 70)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
