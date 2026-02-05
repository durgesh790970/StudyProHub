# Database Schema Documentation

This directory contains database schema definitions for the Youtube Manage application. Choose based on your database system.

---

## 📊 Available Schemas

### 1. **schema.sql** - SQLite (Current/Default)
- **File**: `schema.sql`
- **Database**: SQLite3
- **Status**: ✅ Currently Used in Development
- **Best For**: Development, testing, small deployments

**Tables Include:**
- Users & Authentication
- Mock Tests & Interview Sessions
- Questions & Test Results
- User Answers/Responses
- Payments & Transactions
- B.Tech Semester Content
- Companies & Placement Papers
- Job Applications
- Interview Sessions
- Feedback System
- Items & User Purchases

**Key Features:**
- 12 main tables + relationships
- Indexes for performance
- Views for common queries
- Support for all application features

---

### 2. **mongo.js** - MongoDB
- **File**: `mongo.js`
- **Database**: MongoDB
- **Status**: ⚠️ Alternative Option (Not Currently Used)
- **Best For**: High scalability, flexible schemas, cloud deployments

**Collections Include:**
- users
- mockTests
- questions
- testResults
- transactions
- companies
- placementPapers
- jobApplications
- interviewSessions
- feedback
- items
- userPurchases
- bTechContent

**Key Features:**
- Schema validation using JSON Schema
- Indexes for performance
- Support for nested documents
- Flexible data structure

---

## � Using SQLite (Default)

### Setup & Initialize

```bash
# Navigate to backend
cd backend

# Initialize database (Django will use db.sqlite3)
python manage.py migrate

# This creates all necessary tables automatically
```

### Backup Database

```bash
# Copy database for backup
copy db.sqlite3 db.sqlite3.backup

# Or use the fixed version provided
dir db.sqlite3.fixed
```

### Access SQLite Database

**Using Django Shell:**
```bash
python manage.py shell
```

**Using SQLite CLI:**
```bash
sqlite3 db.sqlite3
.tables
.schema accounts_user
SELECT * FROM accounts_user;
```

**Using a GUI Tool:**
- DB Browser for SQLite
- SQL Server Management Studio
- VS Code SQLite Extension

---

## 🗄️ Using MongoDB (Alternative)

### Prerequisites

```bash
# Install MongoDB
# Download from: https://www.mongodb.com/try/download/community

# Install Python driver
pip install pymongo mongoengine
```

### Setup MongoDB

```bash
# Start MongoDB service
mongod

# Connect with mongo shell
mongosh

# Load the schema
mongosh < mongo.js
```

### Update Django Configuration

Edit `backend/djproject/settings.py`:

```python
# Install django-mongodb or use raw pymongo
# For MongoEngine integration:
INSTALLED_APPS = [
    # ... other apps
    'django_mongodb_engine',
]

# MongoDB connection
MONGODB_DATABASES = {
    'default': {
        'name': 'youtube_manage',
        'host': 'localhost',
        'port': 27017,
        'tz_aware': True,
    }
}
```

---

## 📋 Schema Comparison

| Feature | SQLite | MongoDB |
|---------|--------|---------|
| **Type** | Relational | NoSQL (Document) |
| **Scalability** | Low-Medium | High |
| **Setup Complexity** | Simple | Medium |
| **Data Consistency** | ACID | Eventually Consistent |
| **Query Language** | SQL | MongoDB Query Language |
| **Best For** | Development | Production/Cloud |
| **Deployment** | Embedded | Server |
| **File Size** | Small (file-based) | Large (server-based) |

---

## 📊 Database Statistics

### Tables/Collections (Both)
- 13 main tables/collections
- 20+ indexes
- Support for 10+ different data types
- Full CRUD operations

### Estimated Capacity

**SQLite:**
- Suitable for: ~100,000 records per table
- Database size: ~50-100 MB
- Users: 1-10 concurrent

**MongoDB:**
- Suitable for: Unlimited records
- Database size: Variable
- Users: 1000+ concurrent

---

## 🔄 Migration Path

### SQLite → MongoDB

If you want to migrate from SQLite to MongoDB:

```python
# Use Django's serialization
python manage.py dumpdata > data.json

# Then load into MongoDB
# This requires custom script for JSON → MongoDB format
```

### MongoDB → SQLite

For smaller datasets, export collections and import to SQLite:

```javascript
// MongoDB
db.users.find().forEach(doc => {
  print(JSON.stringify(doc));
});
```

---

## 🔐 Security Considerations

### SQLite
- ✅ File-based, no network access
- ⚠️ Less suitable for multi-user environments
- ✅ Good for development/testing

### MongoDB
- ✅ Network authentication available
- ✅ Role-based access control
- ✅ Encryption support
- ⚠️ Requires proper firewall rules

---

## 📈 Performance Tips

### SQLite
```sql
-- Create indexes for frequently searched columns
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_user_active ON users(is_active);
```

### MongoDB
```javascript
// Create indexes
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ isActive: 1 });
```

---

## 🛠️ Database Management

### Backup

**SQLite:**
```bash
# Simple file copy
copy db.sqlite3 db.sqlite3.backup_DATE
```

**MongoDB:**
```bash
# MongoDB backup
mongodump --uri="mongodb://localhost:27017/youtube_manage"
```

### Restore

**SQLite:**
```bash
# Restore from backup
copy db.sqlite3.backup db.sqlite3
```

**MongoDB:**
```bash
# MongoDB restore
mongorestore --uri="mongodb://localhost:27017/youtube_manage"
```

---

## 📚 Related Documentation

- [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md) - Overall project structure
- [SETUP.md](../SETUP.md) - Setup and getting started
- [Django Documentation](https://docs.djangoproject.com/en/stable/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [MongoDB Documentation](https://docs.mongodb.com/)

---

## ❓ FAQ

**Q: Which database should I use?**
- A: Start with SQLite for development. Use MongoDB for production/scaling.

**Q: How do I switch databases?**
- A: Modify Django's DATABASES setting in settings.py.

**Q: Can I use both simultaneously?**
- A: Yes, but requires routing configuration.

**Q: How do I create new tables/collections?**
- A: Use Django migrations for SQLite, or modify schema.sql/mongo.js

**Q: How do I backup my database?**
- A: Use provided backup scripts or native tools.

---

## 📞 Support

For database-related issues:
1. Check Django documentation
2. Review schema files for table definitions
3. Use DB Browser or Studio 3T for visual inspection
4. Enable Django logging for SQL queries

---

**Version**: 1.0.0  
**Last Updated**: February 5, 2026  
**Status**: ✅ Production Ready
