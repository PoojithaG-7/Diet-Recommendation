# 🗄️ Database Setup Guide for Diet Recommendation System

## 🎯 Overview

The Diet Recommendation System now supports **persistent data storage** using SQLite database. This means all user data, meals, exercise logs, and water intake will be saved permanently and won't be lost when the server restarts.

## ✅ What's Been Created

### Database Files
- **`database.py`** - Core database class with all CRUD operations
- **`app_db.py`** - Database-enabled Flask application
- **`diet_system.db`** - SQLite database file (created automatically)
- **`run_database_backend.bat`** - Startup script for database version

### Migration Tools
- **`migrate_to_database.py`** - Migrates existing data to database
- **`test_database.py`** - Tests all database functions

## 🚀 Quick Start

### Method 1: Use Database Version (Recommended)
```bash
1. Double-click: run_database_backend.bat
2. Backend starts at: http://localhost:5000
3. All data persists between restarts
```

### Method 2: Manual Start
```bash
cd "c:\project4\Diet Recommendation System\backend"
python app_db.py
```

### Method 3: Initialize Database First
```bash
python database.py          # Create database
python migrate_to_database.py  # Migrate existing data
python app_db.py             # Start server
```

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### User Profiles Table
```sql
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT,
    email TEXT,
    age INTEGER,
    gender TEXT,
    phone TEXT,
    weight REAL,
    height REAL,
    bmi REAL,
    bmi_category TEXT,
    activity_level TEXT,
    goal TEXT,
    dietary_notes TEXT,
    diet_plan TEXT,
    daily_calories_needed INTEGER,
    profile_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Activity Logs
```sql
-- Diet Logs
CREATE TABLE diet_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    meal_type TEXT NOT NULL,
    food_name TEXT NOT NULL,
    serving_size TEXT,
    calories REAL DEFAULT 0,
    protein REAL DEFAULT 0,
    carbs REAL DEFAULT 0,
    fats REAL DEFAULT 0,
    date DATE NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exercise Logs
CREATE TABLE exercise_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    calories_burned INTEGER DEFAULT 0,
    date DATE NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Water Logs
CREATE TABLE water_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    glasses INTEGER NOT NULL,
    ml INTEGER NOT NULL,
    date DATE NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Database Features

### ✅ Persistent Storage
- **User Data**: Names, emails, profiles, preferences
- **Diet Logs**: All meals with nutrition information
- **Exercise Logs**: Activities, duration, calories burned
- **Water Logs**: Daily water intake tracking
- **User Tasks**: Daily tasks and completion status

### ✅ Data Integrity
- **Foreign Key Constraints**: Ensures data relationships
- **Unique Constraints**: Prevents duplicate emails
- **Data Types**: Proper data types for all fields
- **Timestamps**: Automatic creation and update timestamps

### ✅ Performance
- **SQLite**: Fast, file-based database
- **Indexes**: Optimized for common queries
- **Connection Pooling**: Efficient database connections
- **Caching**: Frequently accessed data cached

## 📱 API Endpoints (Database Version)

### Authentication
```
POST /api/auth/login      - User login
POST /api/auth/register   - User registration
GET  /api/auth/profile    - Get user profile
```

### Features
```
GET/POST /api/diet-log    - Meal logging
GET/POST /api/exercise    - Exercise tracking
GET/POST /api/water       - Water monitoring
```

### Admin
```
GET /api/admin/users     - Get all users (admin dashboard)
```

### System
```
GET /api/health           - Health check
GET  /                   - API information
```

## 🔄 Migration from In-Memory Storage

### Current Data Preserved
- ✅ Admin user (admin@diet-system.com)
- ✅ User profiles and preferences
- ✅ Diet plans and meal data
- ✅ Exercise and water logs
- ✅ All user settings

### Migration Steps
1. **Database Initialization**: `python database.py`
2. **Data Migration**: `python migrate_to_database.py`
3. **Start New Server**: `python app_db.py`

## 🚀 Benefits of Database Storage

### ✅ Data Persistence
- **No Data Loss**: Server restarts don't lose data
- **Crash Recovery**: Data survives application crashes
- **Backup Support**: Easy database backups
- **Data Export**: Export data for analysis

### ✅ Scalability
- **Multiple Users**: Supports unlimited users
- **Large Data Sets**: Handles millions of records
- **Concurrent Access**: Multiple users simultaneously
- **Fast Queries**: Optimized database queries

### ✅ Data Analysis
- **Historical Data**: Track trends over time
- **User Analytics**: Analyze user behavior
- **Reports**: Generate detailed reports
- **Export Options**: CSV, JSON, Excel exports

## 🛠️ Database Management

### View Database Contents
```bash
sqlite3 diet_system.db
.tables
SELECT * FROM users;
SELECT * FROM user_profiles;
```

### Backup Database
```bash
cp diet_system.db diet_system_backup.db
```

### Reset Database
```bash
rm diet_system.db
python database.py
```

### Query Examples
```sql
-- Get user statistics
SELECT COUNT(*) as total_users FROM users;

-- Get most active users
SELECT u.name, COUNT(dl.id) as meal_count
FROM users u
LEFT JOIN diet_logs dl ON u.id = dl.user_id
GROUP BY u.id
ORDER BY meal_count DESC;

-- Get today's activity
SELECT activity_type, COUNT(*) as count
FROM exercise_logs
WHERE date = date('now')
GROUP BY activity_type;
```

## 🔍 Troubleshooting

### Database Locked
```bash
# Check if database is in use
lsof diet_system.db  # Linux/Mac
# or restart the application
```

### Corrupted Database
```bash
# Check database integrity
sqlite3 diet_system.db "PRAGMA integrity_check;"
# If corrupted, restore from backup
```

### Performance Issues
```bash
# Analyze database
sqlite3 diet_system.db "ANALYZE;"
# Optimize database
sqlite3 diet_system.db "VACUUM;"
```

## 📋 Comparison: In-Memory vs Database

| Feature | In-Memory | Database |
|---------|------------|----------|
| **Data Persistence** | ❌ Lost on restart | ✅ Permanent |
| **Multiple Users** | ❌ Limited | ✅ Unlimited |
| **Data Analysis** | ❌ No history | ✅ Full analytics |
| **Backup/Recovery** | ❌ Not possible | ✅ Easy backup |
| **Scalability** | ❌ Limited | ✅ Highly scalable |
| **Performance** | ✅ Fast | ✅ Fast |
| **Setup Complexity** | ✅ Simple | ✅ Moderate |

## 🎯 Recommendation

**For Production Use**: Use the database version (`app_db.py`)
**For Development**: Either version works
**For Testing**: In-memory version is fine

## 📞 Support

### Database Issues
1. Check if `diet_system.db` file exists
2. Verify database permissions
3. Check for database locks
4. Restart the application

### API Issues
1. Verify database backend is running
2. Check API endpoints with curl/Postman
3. Review database logs
4. Test with sample data

---

**🎉 Your Diet Recommendation System now has persistent database storage!**

**All user data will be safely stored and available even after server restarts.** ✅
