"""
Quick API Testing Script
Tests all database API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(test_name):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}[OK] {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}[FAIL] {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.YELLOW}[INFO] {msg}{Colors.END}")

def print_response(resp):
    try:
        print(f"Status: {resp.status_code}")
        print(f"Response:\n{json.dumps(resp.json(), indent=2)}")
    except:
        print(f"Response:\n{resp.text}")

# ============================================================================
# TEST 1: USER REGISTRATION
# ============================================================================

def test_registration():
    print_test("User Registration")
    
    test_email = f"testuser{int(time.time())}@example.com"
    
    payload = {
        "email": test_email,
        "username": f"testuser_{int(time.time())}",
        "password": "TestPass123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "9876543210"
    }
    
    print_info(f"Registering: {test_email}")
    
    try:
        resp = requests.post(f"{API_BASE}/register/", json=payload)
        
        if resp.status_code == 201:
            data = resp.json()
            if data.get('success'):
                user_id = data.get('user_id')
                print_success(f"Registration successful! User ID: {user_id}")
                return user_id, test_email, payload['password']
            else:
                print_error(f"API returned success=false: {data.get('error')}")
                return None, test_email, payload['password']
        else:
            print_error(f"Status {resp.status_code}")
            print_response(resp)
            return None, test_email, payload['password']
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return None, test_email, payload['password']

# ============================================================================
# TEST 2: USER LOGIN
# ============================================================================

def test_login(email, password):
    print_test("User Login")
    
    payload = {
        "email": email,
        "password": password
    }
    
    print_info(f"Logging in: {email}")
    
    try:
        resp = requests.post(f"{API_BASE}/login/", json=payload)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                print_success(f"Login successful!")
                print_info(f"User: {data['user']['first_name']} {data['user']['last_name']}")
                return True
            else:
                print_error(f"Login failed: {data.get('error')}")
                return False
        else:
            print_error(f"Status {resp.status_code}")
            print_response(resp)
            return False
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

# ============================================================================
# TEST 3: GET USER PROFILE
# ============================================================================

def test_get_profile(user_id):
    print_test("Get User Profile")
    
    print_info(f"Fetching profile for user ID: {user_id}")
    
    try:
        resp = requests.get(f"{API_BASE}/profile/{user_id}/")
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                print_success(f"Profile retrieved successfully!")
                return True
            else:
                print_error(f"Failed: {data.get('error')}")
                return False
        else:
            print_error(f"Status {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

# ============================================================================
# TEST 4: UPDATE USER PROFILE
# ============================================================================

def test_update_profile(user_id):
    print_test("Update User Profile")
    
    payload = {
        "bio": "Test user profile",
        "college": "IIT Delhi",
        "branch": "Computer Science",
        "cgpa": 8.5
    }
    
    print_info(f"Updating profile for user ID: {user_id}")
    
    try:
        resp = requests.put(f"{API_BASE}/profile/{user_id}/", json=payload)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                print_success(f"Profile updated successfully!")
                return True
            else:
                print_error(f"Update failed: {data.get('error')}")
                return False
        elif resp.status_code == 404:
            print_error(f"User not found (404)")
            return False
        else:
            print_error(f"Status {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

# ============================================================================
# TEST 5: CREATE TRANSACTION
# ============================================================================

def test_create_transaction(user_id):
    print_test("Create Transaction")
    
    payload = {
        "transaction_id": f"TXN_{int(time.time())}",
        "amount": 499.00,
        "currency": "INR",
        "status": "COMPLETED",
        "payment_method": "card",
        "item_type": "course",
        "item_id": 1
    }
    
    print_info(f"Creating transaction for user ID: {user_id}")
    
    try:
        resp = requests.post(f"{API_BASE}/transactions/{user_id}/", json=payload)
        
        if resp.status_code == 201:
            data = resp.json()
            if data.get('success'):
                print_success(f"Transaction created successfully!")
                return True
            else:
                print_error(f"Failed: {data.get('error')}")
                return False
        else:
            print_error(f"Status {resp.status_code}")
            print_response(resp)
            return False
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

# ============================================================================
# TEST 6: GET TRANSACTIONS
# ============================================================================

def test_get_transactions(user_id):
    print_test("Get User Transactions")
    
    print_info(f"Fetching transactions for user ID: {user_id}")
    
    try:
        resp = requests.get(f"{API_BASE}/transactions/{user_id}/")
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                count = data.get('count', 0)
                print_success(f"Found {count} transactions")
                return True
            else:
                print_error(f"Failed: {data.get('error')}")
                return False
        else:
            print_error(f"Status {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

# ============================================================================
# TEST 7: SAVE TEST RESULT
# ============================================================================

def test_save_test_result(user_id):
    print_test("Save Test Result")
    
    payload = {
        "test_name": "JavaScript Quiz",
        "score_obtained": 80,
        "total_score": 100,
        "score_percent": 80.0,
        "time_taken_seconds": 1800,
        "correct_answers": 20,
        "wrong_answers": 5
    }
    
    print_info(f"Saving test result for user ID: {user_id}")
    
    try:
        resp = requests.post(f"{API_BASE}/test-results/{user_id}/", json=payload)
        
        if resp.status_code == 201:
            data = resp.json()
            if data.get('success'):
                print_success(f"Test result saved successfully!")
                return True
            else:
                print_error(f"Failed: {data.get('error')}")
                return False
        else:
            print_error(f"Status {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

# ============================================================================
# TEST 8: GET TEST RESULTS
# ============================================================================

def test_get_test_results(user_id):
    print_test("Get Test Results")
    
    print_info(f"Fetching test results for user ID: {user_id}")
    
    try:
        resp = requests.get(f"{API_BASE}/test-results/{user_id}/")
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                count = data.get('count', 0)
                print_success(f"Found {count} test results")
                return True
            else:
                print_error(f"Failed: {data.get('error')}")
                return False
        else:
            print_error(f"Status {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

# ============================================================================
# TEST 9: GET COMPLETE USER INFO
# ============================================================================

def test_get_user_info(user_id):
    print_test("Get Complete User Information")
    
    print_info(f"Fetching complete info for user ID: {user_id}")
    
    try:
        resp = requests.get(f"{API_BASE}/user-info/{user_id}/")
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                print_success(f"Complete user info retrieved!")
                user_data = data.get('data', {})
                print_info(f"User email: {user_data.get('user', {}).get('email')}")
                print_info(f"Transactions: {len(user_data.get('transactions', []))}")
                print_info(f"Test results: {len(user_data.get('test_results', []))}")
                return True
            else:
                print_error(f"Failed: {data.get('error')}")
                return False
        else:
            print_error(f"Status {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

# ============================================================================
# TEST 10: GET DATABASE STATS
# ============================================================================

def test_get_stats():
    print_test("Get Database Statistics")
    
    try:
        resp = requests.get(f"{API_BASE}/stats/")
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                stats = data.get('stats', {})
                print_success(f"Database stats retrieved!")
                print_info(f"Total users: {stats.get('total_users', 0)}")
                print_info(f"Active users: {stats.get('active_users', 0)}")
                print_info(f"Premium users: {stats.get('premium_users', 0)}")
                return True
            else:
                print_error(f"Failed: {data.get('error')}")
                return False
        else:
            print_error(f"Status {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    print(f"\n{Colors.BLUE}")
    print("=" * 60)
    print("STUDYPRO HUB - DATABASE API TEST SUITE v1.0")
    print("=" * 60)
    print(f"{Colors.END}")
    
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"API Base: {API_BASE}")
    
    # Check if server is running
    try:
        resp = requests.get(BASE_URL, timeout=5)
        print_success("Server is running")
    except:
        print_error("Server is not running!")
        print_info("Please start the server with: python manage.py runserver")
        return
    
    # Run tests
    results = {}
    
    # Test 1: Register
    user_id, email, password = test_registration()
    results['registration'] = user_id is not None
    
    if not user_id:
        print_error("Cannot continue without user ID")
        return
    
    # Test 2: Login
    results['login'] = test_login(email, password)
    
    # Test 3: Get Profile
    results['get_profile'] = test_get_profile(user_id)
    
    # Test 4: Update Profile
    results['update_profile'] = test_update_profile(user_id)
    
    # Test 5: Create Transaction
    results['create_transaction'] = test_create_transaction(user_id)
    
    # Test 6: Get Transactions
    results['get_transactions'] = test_get_transactions(user_id)
    
    # Test 7: Save Test Result
    results['save_test_result'] = test_save_test_result(user_id)
    
    # Test 8: Get Test Results
    results['get_test_results'] = test_get_test_results(user_id)
    
    # Test 9: Get User Info
    results['get_user_info'] = test_get_user_info(user_id)
    
    # Test 10: Get Stats
    results['get_stats'] = test_get_stats()
    
    # Print Summary
    print(f"\n{Colors.BLUE}")
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"{Colors.END}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASSED{Colors.END}" if result else f"{Colors.RED}FAILED{Colors.END}"
        print(f"{test_name.ljust(30)} : {status}")
    
    print(f"\n{Colors.BLUE}Total: {passed}/{total} passed{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}[SUCCESS] ALL TESTS PASSED!{Colors.END}")
    else:
        print(f"{Colors.RED}[FAILURE] Some tests failed{Colors.END}")

if __name__ == "__main__":
    main()
