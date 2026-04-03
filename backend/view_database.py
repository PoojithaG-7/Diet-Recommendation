import sqlite3
from tabulate import tabulate
from datetime import datetime, date

class DatabaseViewer:
    def __init__(self, db_path='diet_system.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Enable row factory for better access
    
    def show_tables(self):
        """Show all tables in the database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📊 Database Tables:")
        print("=" * 50)
        for table in tables:
            print(f"  📋 {table[0]}")
        print()
    
    def show_table_structure(self, table_name):
        """Show the structure of a specific table"""
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        print(f"🏗️  Table Structure: {table_name}")
        print("=" * 50)
        headers = ["Column", "Type", "NotNull", "Default", "PK"]
        rows = [[col[1], col[2], col[3], col[4], col[5]] for col in columns]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        print()
    
    def show_users(self):
        """Show all users"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, email, name, created_at 
            FROM users 
            ORDER BY created_at DESC
        ''')
        users = cursor.fetchall()
        
        print("👥 All Users:")
        print("=" * 80)
        headers = ["ID", "Email", "Name", "Created At"]
        rows = [[user[0], user[1], user[2], user[3]] for user in users]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        print()
    
    def show_user_profiles(self):
        """Show all user profiles"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT u.email, p.age, p.gender, p.weight, p.height, p.bmi, 
                   p.activity_level, p.goal, p.profile_completed
            FROM users u
            LEFT JOIN user_profiles p ON u.id = p.user_id
            ORDER BY u.created_at DESC
        ''')
        profiles = cursor.fetchall()
        
        print("📋 User Profiles:")
        print("=" * 100)
        headers = ["Email", "Age", "Gender", "Weight", "Height", "BMI", "Activity", "Goal", "Completed"]
        rows = [[p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], "✅" if p[8] else "❌"] for p in profiles]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        print()
    
    def show_recent_meals(self, limit=10):
        """Show recent meal logs"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT u.email, dl.meal_type, dl.food_name, dl.calories, 
                   dl.protein, dl.carbs, dl.fats, dl.date
            FROM diet_logs dl
            JOIN users u ON dl.user_id = u.id
            ORDER BY dl.completed_at DESC
            LIMIT ?
        ''', (limit,))
        meals = cursor.fetchall()
        
        print(f"🍽️  Recent Meals (Last {limit}):")
        print("=" * 120)
        headers = ["Email", "Meal Type", "Food", "Calories", "Protein", "Carbs", "Fats", "Date"]
        rows = [[m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7]] for m in meals]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        print()
    
    def show_recent_exercises(self, limit=10):
        """Show recent exercise logs"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT u.email, el.activity_type, el.duration_minutes, 
                   el.calories_burned, el.date, el.completed_at
            FROM exercise_logs el
            JOIN users u ON el.user_id = u.id
            ORDER BY el.completed_at DESC
            LIMIT ?
        ''', (limit,))
        exercises = cursor.fetchall()
        
        print(f"🏃 Recent Exercises (Last {limit}):")
        print("=" * 100)
        headers = ["Email", "Activity", "Duration", "Calories", "Date", "Completed At"]
        rows = [[e[0], e[1], f"{e[2]} min", e[3], e[4], e[5]] for e in exercises]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        print()
    
    def show_water_intake(self, days=7):
        """Show water intake for recent days"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT u.email, wl.date, SUM(wl.glasses) as total_glasses, 
                   SUM(wl.ml) as total_ml
            FROM water_logs wl
            JOIN users u ON wl.user_id = u.id
            WHERE wl.date >= date('now', '-{} days')
            GROUP BY u.email, wl.date
            ORDER BY wl.date DESC, u.email
        '''.format(days))
        water_data = cursor.fetchall()
        
        print(f"💧 Water Intake (Last {days} days):")
        print("=" * 80)
        headers = ["Email", "Date", "Glasses", "ML"]
        rows = [[w[0], w[1], w[2], w[3]] for w in water_data]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        print()
    
    def show_statistics(self):
        """Show database statistics"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # User counts
        cursor.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_profiles WHERE profile_completed = 1")
        stats['completed_profiles'] = cursor.fetchone()[0]
        
        # Activity counts
        cursor.execute("SELECT COUNT(*) FROM diet_logs")
        stats['total_meals'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM exercise_logs")
        stats['total_exercises'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM water_logs")
        stats['total_water_logs'] = cursor.fetchone()[0]
        
        # Today's activity
        today = date.today().isoformat()
        cursor.execute("SELECT COUNT(*) FROM diet_logs WHERE date = ?", (today,))
        stats['today_meals'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM exercise_logs WHERE date = ?", (today,))
        stats['today_exercises'] = cursor.fetchone()[0]
        
        print("📊 Database Statistics:")
        print("=" * 50)
        print(f"  👥 Total Users: {stats['total_users']}")
        print(f"  ✅ Completed Profiles: {stats['completed_profiles']}")
        print(f"  🍽️  Total Meals Logged: {stats['total_meals']}")
        print(f"  🏃 Total Exercises: {stats['total_exercises']}")
        print(f"  💧 Total Water Logs: {stats['total_water_logs']}")
        print(f"  📅 Today's Meals: {stats['today_meals']}")
        print(f"  🏃 Today's Exercises: {stats['today_exercises']}")
        print()
    
    def search_user(self, email):
        """Search for a specific user and show their data"""
        cursor = self.conn.cursor()
        
        # Get user info
        cursor.execute("SELECT id, email, name, created_at FROM users WHERE email LIKE ?", (f'%{email}%',))
        users = cursor.fetchall()
        
        if not users:
            print(f"❌ No users found with email containing: {email}")
            return
        
        for user in users:
            print(f"👤 User: {user[1]} ({user[2]})")
            print("=" * 80)
            
            # Get profile
            cursor.execute('''
                SELECT age, gender, weight, height, bmi, activity_level, goal
                FROM user_profiles WHERE user_id = ?
            ''', (user[0],))
            profile = cursor.fetchone()
            
            if profile:
                print("📋 Profile:")
                print(f"  Age: {profile[0]}")
                print(f"  Gender: {profile[1]}")
                print(f"  Weight: {profile[2]} kg")
                print(f"  Height: {profile[3]} cm")
                print(f"  BMI: {profile[4]}")
                print(f"  Activity Level: {profile[5]}")
                print(f"  Goal: {profile[6]}")
                print()
            
            # Get recent meals
            cursor.execute('''
                SELECT meal_type, food_name, calories, date
                FROM diet_logs WHERE user_id = ?
                ORDER BY completed_at DESC LIMIT 5
            ''', (user[0],))
            meals = cursor.fetchall()
            
            if meals:
                print("🍽️  Recent Meals:")
                headers = ["Meal Type", "Food", "Calories", "Date"]
                rows = [[m[0], m[1], m[2], m[3]] for m in meals]
                print(tabulate(rows, headers=headers, tablefmt="grid"))
                print()
            
            # Get recent exercises
            cursor.execute('''
                SELECT activity_type, duration_minutes, calories_burned, date
                FROM exercise_logs WHERE user_id = ?
                ORDER BY completed_at DESC LIMIT 5
            ''', (user[0],))
            exercises = cursor.fetchall()
            
            if exercises:
                print("🏃 Recent Exercises:")
                headers = ["Activity", "Duration", "Calories", "Date"]
                rows = [[e[0], f"{e[1]} min", e[2], e[3]] for e in exercises]
                print(tabulate(rows, headers=headers, tablefmt="grid"))
                print()
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    print("🗄️  Diet Recommendation System - Database Viewer")
    print("=" * 60)
    
    try:
        viewer = DatabaseViewer()
        
        while True:
            print("\n📋 Menu:")
            print("1. Show all tables")
            print("2. Show table structure")
            print("3. Show all users")
            print("4. Show user profiles")
            print("5. Show recent meals")
            print("6. Show recent exercises")
            print("7. Show water intake")
            print("8. Show statistics")
            print("9. Search user")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-9): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                viewer.show_tables()
            elif choice == '2':
                table = input("Enter table name: ").strip()
                viewer.show_table_structure(table)
            elif choice == '3':
                viewer.show_users()
            elif choice == '4':
                viewer.show_user_profiles()
            elif choice == '5':
                viewer.show_recent_meals()
            elif choice == '6':
                viewer.show_recent_exercises()
            elif choice == '7':
                viewer.show_water_intake()
            elif choice == '8':
                viewer.show_statistics()
            elif choice == '9':
                email = input("Enter email (or part of email): ").strip()
                viewer.search_user(email)
            else:
                print("❌ Invalid choice. Please try again.")
        
        viewer.close()
        print("\n👋 Goodbye!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
