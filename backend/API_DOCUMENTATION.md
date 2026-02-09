# Database API Documentation

Complete REST API reference for the StudyPro Hub database system.

## Base URL
```
http://localhost:8000/api/
```

## Response Format
All responses are returned as JSON with the following structure:
```json
{
    "success": true/false,
    "message": "Human readable message",
    "data": { /* endpoint-specific data */ },
    "error": "Error message (if success=false)"
}
```

---

## Authentication APIs

### 1. User Registration
Register a new user in the system.

**Endpoint:** `POST /api/register/`

**Request Body:**
```json
{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "9876543210"
}
```

**Required Fields:**
- `email` - Valid email address
- `username` - Unique username
- `password` - Min 8 chars, 1 uppercase, 1 number
- `first_name` - User's first name

**Optional Fields:**
- `last_name` - User's last name
- `phone` - User's phone number

**Response (Success):**
```json
{
    "success": true,
    "message": "User registered successfully",
    "user_id": 1,
    "email": "user@example.com"
}
```

**Response (Error):**
```json
{
    "success": false,
    "error": "Email already registered"
}
```

**Status Codes:**
- `201` - User created successfully
- `400` - Validation error
- `409` - Email already exists

**JavaScript Example:**
```javascript
const result = await dbAPI.register({
    email: 'user@example.com',
    username: 'johndoe',
    password: 'SecurePass123',
    first_name: 'John',
    last_name: 'Doe',
    phone: '9876543210'
});
```

---

### 2. User Login
Authenticate user and return user information.

**Endpoint:** `POST /api/login/`

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "SecurePass123"
}
```

**Required Fields:**
- `email` - Registered email
- `password` - User's password

**Response (Success):**
```json
{
    "success": true,
    "message": "Login successful",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "9876543210",
        "is_active": true,
        "created_at": "2024-01-15T10:30:00",
        "email_verified": false
    }
}
```

**Response (Error):**
```json
{
    "success": false,
    "error": "Invalid email or password"
}
```

**Status Codes:**
- `200` - Login successful
- `400` - Missing email or password
- `401` - Invalid credentials
- `403` - Account inactive

**JavaScript Example:**
```javascript
const result = await dbAPI.login('user@example.com', 'SecurePass123');
if (result.success) {
    localStorage.setItem('userId', result.data.user.id);
    window.location.href = '/dashboard/';
}
```

---

## User Profile APIs

### 3. Get User Profile
Retrieve complete user profile information.

**Endpoint:** `GET /api/profile/<user_id>/`

**Path Parameters:**
- `user_id` - Integer user ID

**Response (Success):**
```json
{
    "success": true,
    "data": {
        "user": {
            "id": 1,
            "email": "user@example.com",
            "username": "johndoe",
            "first_name": "John",
            "is_active": true
        },
        "profile": {
            "user_id": 1,
            "bio": "Student",
            "picture_url": "/media/profile/1.jpg",
            "college": "IIT Delhi",
            "branch": "Computer Science",
            "cgpa": 8.5,
            "resume_url": "/media/resume/1.pdf",
            "is_premium": true,
            "created_at": "2024-01-15T10:30:00"
        }
    }
}
```

**Status Codes:**
- `200` - Profile retrieved successfully
- `404` - User not found
- `500` - Server error

**JavaScript Example:**
```javascript
const result = await dbAPI.getProfile(1);
if (result.success) {
    console.log(result.data.profile);
}
```

---

### 4. Create User Profile
Create a new user profile.

**Endpoint:** `POST /api/profile/<user_id>/`

**Request Body:**
```json
{
    "bio": "Student at IIT Delhi",
    "college": "IIT Delhi",
    "branch": "Computer Science",
    "cgpa": 8.5,
    "is_premium": false
}
```

**Optional Fields:**
- `bio` - User biography
- `college` - College name
- `branch` - Branch/Department
- `cgpa` - CGPA (0-10)
- `picture_url` - Profile picture URL
- `resume_url` - Resume file URL

**Response (Success):**
```json
{
    "success": true,
    "message": "Profile created successfully",
    "profile": { /* profile data */ }
}
```

**Status Codes:**
- `201` - Profile created
- `400` - Creation failed
- `404` - User not found

**JavaScript Example:**
```javascript
const result = await dbAPI.createProfile(1, {
    bio: 'Computer Science Student',
    college: 'IIT Delhi',
    cgpa: 8.5
});
```

---

### 5. Update User Profile
Update existing user profile.

**Endpoint:** `PUT /api/profile/<user_id>/`

**Request Body:**
```json
{
    "bio": "Updated bio",
    "college": "New College",
    "cgpa": 9.0
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "Profile updated successfully",
    "profile": { /* updated profile data */ }
}
```

**Status Codes:**
- `200` - Profile updated
- `400` - Update failed
- `404` - User not found

**JavaScript Example:**
```javascript
const result = await dbAPI.updateProfile(1, {
    bio: 'Updated bio',
    cgpa: 9.0
});
```

---

## Transaction APIs

### 6. Get User Transactions
Retrieve all transactions for a user.

**Endpoint:** `GET /api/transactions/<user_id>/`

**Response (Success):**
```json
{
    "success": true,
    "transactions": [
        {
            "id": 1,
            "user_id": 1,
            "transaction_id": "TXN_001",
            "amount": 499.00,
            "currency": "INR",
            "status": "COMPLETED",
            "payment_method": "card",
            "item_type": "course",
            "item_id": 5,
            "created_at": "2024-01-15T10:30:00",
            "updated_at": "2024-01-15T10:35:00"
        }
    ],
    "count": 1
}
```

**Status Codes:**
- `200` - Transactions retrieved
- `404` - User not found

**JavaScript Example:**
```javascript
const result = await dbAPI.getTransactions(1);
console.log(`User has ${result.data.count} transactions`);
```

---

### 7. Create Transaction
Create a new transaction record.

**Endpoint:** `POST /api/transactions/<user_id>/`

**Request Body:**
```json
{
    "transaction_id": "TXN_12345",
    "amount": 499.00,
    "currency": "INR",
    "status": "COMPLETED",
    "payment_method": "card",
    "item_type": "course",
    "item_id": 5
}
```

**Required Fields:**
- `transaction_id` - Unique transaction ID
- `amount` - Transaction amount

**Optional Fields:**
- `currency` - Currency code (default: INR)
- `status` - Payment status (PENDING, COMPLETED, FAILED)
- `payment_method` - Payment method (card, upi, etc.)
- `item_type` - Type of item (course, book, etc.)
- `item_id` - Item ID

**Response (Success):**
```json
{
    "success": true,
    "message": "Transaction created successfully"
}
```

**Status Codes:**
- `201` - Transaction created
- `400` - Missing required fields
- `404` - User not found

**JavaScript Example:**
```javascript
const result = await dbAPI.createTransaction(1, {
    transaction_id: 'TXN_12345',
    amount: 499.00,
    status: 'COMPLETED',
    item_type: 'course'
});
```

---

## Test Result APIs

### 8. Get User Test Results
Retrieve all test results for a user.

**Endpoint:** `GET /api/test-results/<user_id>/`

**Response (Success):**
```json
{
    "success": true,
    "test_results": [
        {
            "id": 1,
            "user_id": 1,
            "test_name": "JavaScript Quiz",
            "score_obtained": 80,
            "total_score": 100,
            "score_percent": 80.0,
            "time_taken_seconds": 1800,
            "correct_answers": 20,
            "wrong_answers": 5,
            "unanswered": 0,
            "created_at": "2024-01-15T10:30:00"
        }
    ],
    "count": 1
}
```

**Status Codes:**
- `200` - Results retrieved
- `404` - User not found

**JavaScript Example:**
```javascript
const result = await dbAPI.getTestResults(1);
result.data.test_results.forEach(test => {
    console.log(`${test.test_name}: ${test.score_percent}%`);
});
```

---

### 9. Save Test Result
Record a new test result.

**Endpoint:** `POST /api/test-results/<user_id>/`

**Request Body:**
```json
{
    "test_name": "JavaScript Quiz",
    "score_obtained": 80,
    "total_score": 100,
    "score_percent": 80.0,
    "time_taken_seconds": 1800,
    "correct_answers": 20,
    "wrong_answers": 5,
    "unanswered": 0
}
```

**Required Fields:**
- `test_name` - Name of the test

**Optional Fields:**
- `score_obtained` - Score obtained (0-100)
- `total_score` - Total score (default: 100)
- `score_percent` - Percentage score (0-100)
- `time_taken_seconds` - Time in seconds
- `correct_answers` - Number correct
- `wrong_answers` - Number wrong
- `unanswered` - Number unanswered

**Response (Success):**
```json
{
    "success": true,
    "message": "Test result saved successfully"
}
```

**Status Codes:**
- `201` - Result saved
- `400` - Missing test_name
- `404` - User not found

**JavaScript Example:**
```javascript
const result = await dbAPI.saveTestResult(1, {
    test_name: 'JavaScript Quiz',
    score_percent: 85.0,
    time_taken_seconds: 1800
});
```

---

## User Info APIs

### 10. Get Complete User Information
Retrieve all user information including profile, transactions, and test results.

**Endpoint:** `GET /api/user-info/<user_id>/`

**Response (Success):**
```json
{
    "success": true,
    "data": {
        "user": {
            "id": 1,
            "email": "user@example.com",
            "username": "johndoe",
            "first_name": "John"
        },
        "profile": { /* profile data */ },
        "transactions": [ /* transaction list */ ],
        "test_results": [ /* test results list */ ],
        "activity": [ /* activity logs */ ]
    }
}
```

**Status Codes:**
- `200` - Data retrieved
- `404` - User not found

**JavaScript Example:**
```javascript
const result = await dbAPI.getUserInfo(1);
console.log(result.data.user);
console.log(result.data.transactions);
```

---

## Statistics APIs

### 11. Get Database Statistics
Retrieve overall database statistics.

**Endpoint:** `GET /api/stats/`

**Response (Success):**
```json
{
    "success": true,
    "stats": {
        "total_users": 150,
        "active_users": 120,
        "total_transactions": 450,
        "total_revenue": 225000.00,
        "total_test_attempts": 1200,
        "premium_users": 45,
        "registered_today": 10,
        "db_size_mb": 25.5
    }
}
```

**Status Codes:**
- `200` - Stats retrieved

**JavaScript Example:**
```javascript
const result = await dbAPI.getStats();
console.log(`Total Users: ${result.data.stats.total_users}`);
console.log(`Total Revenue: ₹${result.data.stats.total_revenue}`);
```

---

## Error Handling

All API errors follow this format:

```json
{
    "success": false,
    "error": "Specific error message"
}
```

### Common Error Codes:
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid credentials)
- `403` - Forbidden (account inactive)
- `404` - Not Found (resource doesn't exist)
- `409` - Conflict (duplicate email, etc.)
- `500` - Internal Server Error

---

## Usage Examples

### Complete Signup & Login Flow
```javascript
// Signup
const signupResult = await dbAPI.register({
    email: 'user@example.com',
    username: 'johndoe',
    password: 'SecurePass123',
    first_name: 'John'
});

if (signupResult.success) {
    const userId = signupResult.data.user_id;
    
    // Create profile
    await dbAPI.createProfile(userId, {
        bio: 'Student',
        college: 'IIT Delhi'
    });
    
    // Login
    const loginResult = await dbAPI.login('user@example.com', 'SecurePass123');
    if (loginResult.success) {
        localStorage.setItem('userId', loginResult.data.user.id);
        window.location.href = '/dashboard/';
    }
}
```

### Purchase Flow
```javascript
const userId = localStorage.getItem('userId');

// Create transaction
const txnResult = await dbAPI.createTransaction(userId, {
    transaction_id: 'TXN_' + Date.now(),
    amount: 499.00,
    status: 'COMPLETED',
    item_type: 'course',
    item_id: 5
});

if (txnResult.success) {
    console.log('Purchase successful');
}
```

### Test Result Flow
```javascript
const userId = localStorage.getItem('userId');

// Save test result
const testResult = await dbAPI.saveTestResult(userId, {
    test_name: 'Mock Test 1',
    score_obtained: 80,
    score_percent: 80.0,
    time_taken_seconds: 3600,
    correct_answers: 20,
    wrong_answers: 5
});

// Fetch all results
const allResults = await dbAPI.getTestResults(userId);
console.log(`You have completed ${allResults.data.count} tests`);
```

---

## Frontend Integration

Include the API client in your HTML:
```html
<script src="{% static 'js/api-client.js' %}"></script>
```

The client is automatically initialized and available as `dbAPI` globally:
```javascript
dbAPI.register({...});
dbAPI.login('email', 'password');
// ... etc
```

---

## Troubleshooting

**Issue:** CORS Error
**Solution:** Ensure requests include proper headers (handled automatically by api-client.js)

**Issue:** 404 User Not Found
**Solution:** Verify user_id is correct

**Issue:** Password validation error
**Solution:** Password must have:
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 number

**Issue:** Email already registered
**Solution:** Use a different email address or login with existing account

---

## Rate Limiting
No rate limiting currently implemented. Production deployment should add rate limiting.

## CORS Policy
Currently CSRF-exempt for API endpoints. Production should implement proper CSRF tokens.

## API Version
Current Version: 1.0
Last Updated: 2024-01-15
