# 🗄️ Database Access Guide

## 🎯 Overview

The Diet Recommendation System uses SQLite database for persistent data storage. Here are all the ways you can access and interact with the database.

## 📍 Database Location

**File Path:** `c:\project4\Diet Recommendation System\backend\diet_system.db`
**File Size:** ~40KB (varies with data)
**Type:** SQLite (file-based database)

## 🚀 Access Methods

### Method 1: Command Line SQLite (Easiest)

**Step 1:** Double-click `access_database.bat`
**Step 2:** Use SQLite commands:

```sql
-- Show all tables
.tables

-- Show table structure
.schema users

-- View all users
SELECT * FROM users;

-- View user profiles
SELECT * FROM user_profiles;

-- View recent meals
SELECT * FROM diet_logs ORDER BY completed_at DESC LIMIT 10;

-- View exercises
SELECT * FROM exercise_logs ORDER BY completed_at DESC LIMIT 10;

-- View water logs
SELECT * FROM water_logs ORDER BY completed_at DESC LIMIT 10;

-- Exit SQLite
.quit
```

### Method 2: Python Database Viewer

**Step 1:** Run `python view_database.py`
**Step 2:** Choose from menu:
- 1: Show all tables
- 2: Show table structure
- 3: Show all users
- 4: Show user profiles
- 5: Show recent meals
- 6: Show recent exercises
- 7: Show water intake
- 8: Show statistics
- 9: Search user
- 0: Exit

### Method 3: Web Database Interface

**Step 1:** Open `database_viewer.html` in browser
**Step 2:** Click buttons to view:
- Statistics
- Users
- Profiles
- Meals
- Exercises
- Water
- Tables

### Method 4: Direct SQLite Commands

**Step 1:** Open Command Prompt
**Step 2:** Navigate to backend directory
**Step 3:** Run SQLite commands:

```bash
cd "c:\project4\Diet Recommendation System\backend"
sqlite3 diet_system.db
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

### Diet Logs Table
```sql
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
```

### Exercise Logs Table
```sql
CREATE TABLE exercise_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    calories_burned INTEGER DEFAULT 0,
    date DATE NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Water Logs Table
```sql
CREATE TABLE water_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    glasses INTEGER NOT NULL,
    ml INTEGER NOT NULL,
    date DATE NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔍 Common Queries

### User Statistics
```sql
-- Total users
SELECT COUNT(*) FROM users;

-- Users with completed profiles
SELECT COUNT(*) FROM user_profiles WHERE profile_completed = 1;

-- Average BMI
SELECT AVG(bmi) FROM user_profiles WHERE bmi IS NOT NULL;
```

### Activity Statistics
```sql
-- Meals logged today
SELECT COUNT(*) FROM diet_logs WHERE date = date('now');

-- Exercises logged today
SELECT COUNT(*) FROM exercise_logs WHERE date = date('now');

-- Water intake today
SELECT SUM(ml) FROM water_logs WHERE date = date('now');
```

### User Activity
```sql
-- Most active users (by meals)
SELECT u.name, COUNT(dl.id) as meal_count
FROM users u
LEFT JOIN diet_logs dl ON u.id = dl.user_id
GROUP BY u.id
ORDER BY meal_count DESC
LIMIT 5;

-- Recent activity
SELECT 'Meal' as type, food_name as activity, completed_at
FROM diet_logs
UNION
SELECT 'Exercise', activity_type, completed_at
FROM exercise_logs
ORDER BY completed_at DESC
LIMIT 10;
```

## 🛠️ Database Management

### Backup Database
```bash
-- Copy database file
cp diet_system.db diet_system_backup.db

-- Or export to SQL
sqlite3 diet_system.db .dump > backup.sql
```

### Restore Database
```bash
-- Restore from backup
cp diet_system_backup.db diet_system.db

-- Or from SQL dump
sqlite3 diet_system_new.db < backup.sql
```

### Reset Database
```bash
-- Delete database file (will be recreated)
rm diet_system.db
python database.py
```

### Database Maintenance
```sql
-- Check integrity
PRAGMA integrity_check;

-- Analyze database
ANALYZE;

-- Vacuum database
VACUUM;

-- Check database size
SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();
```

## 📈 Current Database Status

**Total Users:** 2
- Debug Admin (admin@diet-system.com) - Complete
- Test User (test@example.com) - Complete

**Database Tables:** 7
- users (user accounts)
- user_profiles (user details)
- diet_logs (meal tracking)
- exercise_logs (activity tracking)
- water_logs (hydration tracking)
- user_daily_tasks (daily tasks)
- sqlite_sequence (auto-increment counters)

**Data Records:**
- Meals Logged: 2
- Exercises Logged: 1
- Water Logs: 1

## 🔧 Tools Created

### 1. `access_database.bat`
- Opens SQLite command line
- Shows available commands
- Easy database access

### 2. `view_database.py`
- Interactive Python viewer
- Menu-driven interface
- Rich data formatting
- Search capabilities

### 3. `database_viewer.html`
- Web-based interface
- Visual data display
- Real-time statistics
- User-friendly navigation

### 4. `simple_db_test.py`
- Quick database test
- Shows current status
- Lists all access methods
- Database statistics

## 🚨 Troubleshooting

### Database Locked
```bash
-- Check if database is in use
lsof diet_system.db  # Linux/Mac
-- Or restart the application
```

### Permission Issues
```bash
-- Check file permissions
ls -la diet_system.db
-- Fix permissions if needed
chmod 664 diet_system.db
```

### Corrupted Database
```bash
-- Check integrity
sqlite3 diet_system.db "PRAGMA integrity_check;"
-- If corrupted, restore from backup
```

## 📞 Quick Access Commands

### Quick Start
```bash
# Method 1: Easiest
Double-click: access_database.bat

# Method 2: Python viewer
python view_database.py

# Method 3: Web interface
Open: database_viewer.html

# Method 4: Direct SQLite
sqlite3 diet_system.db
```

### Quick Queries
```sql
-- Show everything
.tables
SELECT * FROM users;
SELECT * FROM diet_logs;
SELECT * FROM exercise_logs;
SELECT * FROM water_logs;

-- Quick stats
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM diet_logs;
SELECT COUNT(*) FROM exercise_logs;
SELECT COUNT(*) FROM water_logs;
```

## 🎯 Recommendation

**For Beginners:** Use Method 1 (access_database.bat)
**For Advanced Users:** Use Method 2 (view_database.py)
**For Visual Users:** Use Method 3 (database_viewer.html)
**For Developers:** Use Method 4 (direct SQLite)

---

**🗄️ Your Diet Recommendation System database is fully accessible!**

**Choose any method above to explore and manage your data.** ✅
