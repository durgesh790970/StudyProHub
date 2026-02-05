# 📱 User Registration Database Setup Guide

## ✅ क्या किया गया है?

आपके Django project में automatic user registration और database saving setup कर दिया है। अब जब कोई user signup करेगा, उसका data automatically SQLite database में save हो जाएगा।

---

## 🔄 कैसे काम करता है?

### 1️⃣ **User Registration Flow**
```
User Registration Form (HTML)
         ↓
    signup_page() View
         ↓
✅ Django Auth User Create करो
         ↓
✅ UserProfile Create करो (Database में save)
         ↓
✅ Data SQLite में Store हो जाता है
```

---

## 📊 Data कहाँ Save होता है?

### **Database File:**
```
backend/db.sqlite3
```

### **Tables:**
- `auth_user` → Django के built-in users
- `accounts_userprofile` → Additional user data (phone, payment status, etc.)

---

## 👨‍💻 User Data देखने के तरीके

### **तरीका 1: Python Script (Terminal)**

```bash
cd backend
python view_users_db.py
```

**Features:**
- ✅ सभी registered users देखें
- ✅ किसी specific user की details देखें
- ✅ Database statistics देखें
- ✅ Interactive menu

**Output Example:**
```
==================================================
📊 ALL REGISTERED USERS
==================================================

✅ Total Users: 5

ID    | Email                           | Full Name        | Joined Date
------|----------------------------------|------------------|---------------------------
1     | john@gmail.com                  | John Doe         | 05-02-2026 10:30:45
2     | jane@gmail.com                  | Jane Smith       | 05-02-2026 11:15:22
```

---

### **तरीका 2: Web Dashboard (Browser)**

**URL:**
```
http://localhost:8000/users-list/
```

**Features:**
- ✅ Beautiful UI में सभी users दिखें
- ✅ Email, Full Name, Phone, Payment Status देखें
- ✅ Registration date देखें
- ✅ Responsive design (mobile-friendly)

---

### **तरीका 3: Django Admin Panel (सबसे बेहतर)**

**URL:**
```
http://localhost:8000/admin/
```

**Steps:**
1. Admin account बनाओ:
   ```bash
   cd backend
   python manage.py createsuperuser
   ```
   (Username, Email, Password दर्ज करो)

2. Login करो: `http://localhost:8000/admin/`

3. **Accounts** → **User Profiles** में users देखो

**Features:**
- ✅ सभी user details
- ✅ Edit/Delete करो
- ✅ Advanced search और filtering
- ✅ Direct database management

---

## 🔧 Technical Details

### **Modified Files:**

#### 1. `backend/accounts/views.py`
```python
# User registration के समय automatic UserProfile बनता है
def signup_page(request):
    # ... email validation ...
    auth_user = User.objects.create_user(...)
    UserProfile.objects.create(auth_user=auth_user)  # ✅ यह line added
```

#### 2. `backend/accounts/urls.py`
```python
path('users-list/', views.view_all_users, name='view_all_users')
```

#### 3. `backend/accounts/admin.py`
```python
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'phone', 'has_paid', 'created_at')
```

#### 4. `frontend/accounts/users_list.html`
- New beautiful HTML template for viewing users

#### 5. `backend/view_users_db.py`
- New Python script for viewing users from terminal

---

## 📋 Database Schema

### **auth_user Table**
```sql
id              INTEGER PRIMARY KEY
username        VARCHAR (username = email)
email           VARCHAR
first_name      VARCHAR
password        VARCHAR (encrypted)
date_joined     DATETIME
is_active       BOOLEAN
```

### **accounts_userprofile Table**
```sql
id              INTEGER PRIMARY KEY
auth_user_id    INTEGER (FK to auth_user)
phone           VARCHAR (unique, optional)
has_paid        BOOLEAN (default: False)
created_at      DATETIME (default: now)
```

---

## 🧪 Testing करने के लिए

### **Step 1: Server Start करो**
```bash
cd backend
python manage.py runserver
```

### **Step 2: New User Register करो**
```
http://localhost:8000/signup/
```
- Form भरो और submit करो
- Data automatically database में save हो जाएगा

### **Step 3: Data को Verify करो**

**Option A: Python Script से**
```bash
python view_users_db.py
# फिर option 1 select करो
```

**Option B: Web Dashboard से**
```
http://localhost:8000/users-list/
```

**Option C: Django Admin से**
```
http://localhost:8000/admin/
# Login करके Accounts > User Profiles देखो
```

---

## ⚙️ Advanced: Database Migration

Agar naye fields add करने हों:

```bash
cd backend

# Migration file बनाओ
python manage.py makemigrations

# Database को update करो
python manage.py migrate
```

---

## 🛡️ Security Tips

1. **Admin panel को secure रखो:**
   - Strong password use करो
   - Admin URL को change करो (optional)

2. **Production के लिए:**
   - SQLite को PostgreSQL में change करो
   - DEBUG = False करो
   - SECRET_KEY को environment variable से load करो

3. **Data Backup:**
   ```bash
   sqlite3 db.sqlite3 .dump > backup.sql
   ```

---

## 📞 Troubleshooting

### **Problem: Users table empty दिख रहा है**
```bash
cd backend
python manage.py migrate
```

### **Problem: Admin login नहीं हो रहा**
```bash
cd backend
python manage.py createsuperuser
```

### **Problem: Database file corrupt है**
```bash
cd backend
rm db.sqlite3
python manage.py migrate
```

---

## 🎯 अगले Steps

1. ✅ **Email Verification** - Signup के बाद email verification add करो
2. ✅ **Phone OTP** - Phone verification implementation
3. ✅ **Data Export** - CSV/Excel में users export करो
4. ✅ **User Analytics** - Charts और graphs add करो

---

## 📝 Quick Reference

| तरीका | URL | Terminal Command | Pros |
|-------|-----|------------------|------|
| Web Dashboard | `/users-list/` | - | Beautiful, Browser-based |
| Terminal Script | - | `python view_users_db.py` | Interactive, Detailed |
| Admin Panel | `/admin/` | - | Most Powerful, Professional |
| Direct SQL | - | `sqlite3 db.sqlite3` | Advanced, Direct Query |

---

**✅ Setup Complete! Your user registration system is now working with automatic database saving! 🎉**

Questions? Check the code comments or the Django documentation.
