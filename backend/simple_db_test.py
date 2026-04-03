from database import DietDatabase

def quick_database_test():
    print("=== QUICK DATABASE ACCESS TEST ===")
    
    db = DietDatabase()
    
    # Test 1: Show all users
    print("1. All Users:")
    users = db.get_all_users()
    for user in users:
        status = "Complete" if user['has_diet_plan'] else "Incomplete"
        print(f"   {user['name']} ({user['email']}) - {status}")
    
    print(f"\nTotal Users: {len(users)}")
    
    # Test 2: Show database statistics
    print("\n2. Database Statistics:")
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM diet_logs")
    meals = cursor.fetchone()[0]
    print(f"   Total Meals Logged: {meals}")
    
    cursor.execute("SELECT COUNT(*) FROM exercise_logs")
    exercises = cursor.fetchone()[0]
    print(f"   Total Exercises: {exercises}")
    
    cursor.execute("SELECT COUNT(*) FROM water_logs")
    water = cursor.fetchone()[0]
    print(f"   Total Water Logs: {water}")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"   Database Tables: {len(tables)}")
    for table in tables:
        print(f"     - {table[0]}")
    
    conn.close()
    
    print("\n=== DATABASE ACCESS METHODS ===")
    print("1. Command Line: Double-click access_database.bat")
    print("2. Python Viewer: python view_database.py")
    print("3. Web Interface: Open database_viewer.html")
    print("4. Direct SQLite: sqlite3 diet_system.db")
    
    print("\n=== DATABASE LOCATION ===")
    import os
    db_path = os.path.abspath(db.db_path)
    print(f"Database File: {db_path}")
    print(f"File Size: {os.path.getsize(db_path)} bytes")
    
    print("\n=== ACCESS COMPLETE ===")

if __name__ == "__main__":
    quick_database_test()
