from database import DietDatabase
from datetime import datetime, date

def show_all_data():
    print("🗄️  DIET SYSTEM DATABASE VIEWER")
    print("=" * 50)
    
    db = DietDatabase()
    
    while True:
        print("\n📋 MENU:")
        print("1. 👥 View All Users")
        print("2. 📋 View User Profiles")
        print("3. 🍽️  View Recent Meals")
        print("4. 🏃 View Recent Exercises")
        print("5. 💧 View Water Intake")
        print("6. 📊 View Statistics")
        print("7. 🔍 Search User")
        print("0. 🚪 Exit")
        
        choice = input("\nEnter your choice (0-7): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            show_users(db)
        elif choice == '2':
            show_profiles(db)
        elif choice == '3':
            show_meals(db)
        elif choice == '4':
            show_exercises(db)
        elif choice == '5':
            show_water(db)
        elif choice == '6':
            show_statistics(db)
        elif choice == '7':
            search_user(db)
        else:
            print("❌ Invalid choice. Please try again.")
    
    print("\n👋 Goodbye!")

def show_users(db):
    print("\n👥 ALL USERS:")
    print("-" * 50)
    users = db.get_all_users()
    
    if not users:
        print("No users found.")
        return
    
    print(f"{'ID':<5} {'Name':<20} {'Email':<25} {'Status':<10}")
    print("-" * 70)
    
    for user in users:
        status = "Complete" if user['has_diet_plan'] else "Incomplete"
        print(f"{user['id']:<5} {user['name']:<20} {user['email']:<25} {status:<10}")

def show_profiles(db):
    print("\n📋 USER PROFILES:")
    print("-" * 50)
    users = db.get_all_users()
    
    completed_users = [u for u in users if u['has_diet_plan']]
    
    if not completed_users:
        print("No completed profiles found.")
        return
    
    print(f"{'Name':<20} {'Age':<5} {'Gender':<8} {'Weight':<8} {'Height':<8} {'BMI':<6}")
    print("-" * 75)
    
    for user in completed_users:
        print(f"{user['name']:<20} {user['age'] or 'N/A':<5} {user['gender'] or 'N/A':<8} "
              f"{user['weight'] or 'N/A':<8} {user['height'] or 'N/A':<8} {user['bmi'] or 'N/A':<6}")

def show_meals(db):
    print("\n🍽️  RECENT MEALS:")
    print("-" * 50)
    
    # Get recent meals from all users
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.email, dl.meal_type, dl.food_name, dl.calories, dl.date
        FROM diet_logs dl
        JOIN users u ON dl.user_id = u.id
        ORDER BY dl.completed_at DESC
        LIMIT 10
    ''')
    
    meals = cursor.fetchall()
    conn.close()
    
    if not meals:
        print("No meals found.")
        return
    
    print(f"{'Email':<20} {'Meal Type':<12} {'Food':<20} {'Calories':<10} {'Date':<12}")
    print("-" * 84)
    
    for meal in meals:
        print(f"{meal[0]:<20} {meal[1]:<12} {meal[2]:<20} {meal[3] or 0:<10} {meal[4]:<12}")

def show_exercises(db):
    print("\n🏃 RECENT EXERCISES:")
    print("-" * 50)
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.email, el.activity_type, el.duration_minutes, el.calories_burned, el.date
        FROM exercise_logs el
        JOIN users u ON el.user_id = u.id
        ORDER BY el.completed_at DESC
        LIMIT 10
    ''')
    
    exercises = cursor.fetchall()
    conn.close()
    
    if not exercises:
        print("No exercises found.")
        return
    
    print(f"{'Email':<20} {'Activity':<20} {'Duration':<10} {'Calories':<10} {'Date':<12}")
    print("-" * 82)
    
    for exercise in exercises:
        print(f"{exercise[0]:<20} {exercise[1]:<20} {exercise[2]} min {exercise[3] or 0:<10} {exercise[4]:<12}")

def show_water(db):
    print("\n💧 WATER INTAKE:")
    print("-" * 50)
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.email, wl.date, SUM(wl.glasses) as total_glasses, SUM(wl.ml) as total_ml
        FROM water_logs wl
        JOIN users u ON wl.user_id = u.id
        WHERE wl.date >= date('now', '-7 days')
        GROUP BY u.email, wl.date
        ORDER BY wl.date DESC, u.email
    ''')
    
    water_data = cursor.fetchall()
    conn.close()
    
    if not water_data:
        print("No water data found.")
        return
    
    print(f"{'Email':<20} {'Date':<12} {'Glasses':<10} {'ML':<10}")
    print("-" * 62)
    
    for water in water_data:
        print(f"{water[0]:<20} {water[1]:<12} {water[2]:<10} {water[3]:<10}")

def show_statistics(db):
    print("\n📊 DATABASE STATISTICS:")
    print("-" * 50)
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # User counts
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM user_profiles WHERE profile_completed = 1")
    completed_profiles = cursor.fetchone()[0]
    
    # Activity counts
    cursor.execute("SELECT COUNT(*) FROM diet_logs")
    total_meals = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM exercise_logs")
    total_exercises = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM water_logs")
    total_water_logs = cursor.fetchone()[0]
    
    # Today's activity
    today = date.today().isoformat()
    cursor.execute("SELECT COUNT(*) FROM diet_logs WHERE date = ?", (today,))
    today_meals = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM exercise_logs WHERE date = ?", (today,))
    today_exercises = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"👥 Total Users: {total_users}")
    print(f"✅ Completed Profiles: {completed_profiles}")
    print(f"🍽️  Total Meals Logged: {total_meals}")
    print(f"🏃 Total Exercises: {total_exercises}")
    print(f"💧 Total Water Logs: {total_water_logs}")
    print(f"📅 Today's Meals: {today_meals}")
    print(f"🏃 Today's Exercises: {today_exercises}")

def search_user(db):
    email = input("🔍 Enter email (or part of email): ").strip()
    
    if not email:
        print("Please enter an email address.")
        return
    
    users = db.get_all_users()
    found_users = [u for u in users if email.lower() in u['email'].lower()]
    
    if not found_users:
        print(f"❌ No users found with email containing: {email}")
        return
    
    for user in found_users:
        print(f"\n👤 User: {user['email']} ({user['name']})")
        print("=" * 50)
        
        # Get user details
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get profile
        cursor.execute('''
            SELECT age, gender, weight, height, bmi, activity_level, goal
            FROM user_profiles WHERE user_id = ?
        ''', (user['id'],))
        profile = cursor.fetchone()
        
        if profile:
            print("📋 Profile:")
            print(f"  Age: {profile[0] or 'N/A'}")
            print(f"  Gender: {profile[1] or 'N/A'}")
            print(f"  Weight: {profile[2] or 'N/A'} kg")
            print(f"  Height: {profile[3] or 'N/A'} cm")
            print(f"  BMI: {profile[4] or 'N/A'}")
            print(f"  Activity Level: {profile[5] or 'N/A'}")
            print(f"  Goal: {profile[6] or 'N/A'}")
        
        # Get recent meals
        cursor.execute('''
            SELECT meal_type, food_name, calories, date
            FROM diet_logs WHERE user_id = ?
            ORDER BY completed_at DESC LIMIT 5
        ''', (user['id'],))
        meals = cursor.fetchall()
        
        if meals:
            print("\n🍽️  Recent Meals:")
            print(f"{'Meal Type':<12} {'Food':<20} {'Calories':<10} {'Date':<12}")
            print("-" * 64)
            for meal in meals:
                print(f"{meal[0]:<12} {meal[1]:<20} {meal[2] or 0:<10} {meal[3]:<12}")
        
        # Get recent exercises
        cursor.execute('''
            SELECT activity_type, duration_minutes, calories_burned, date
            FROM exercise_logs WHERE user_id = ?
            ORDER BY completed_at DESC LIMIT 5
        ''', (user['id'],))
        exercises = cursor.fetchall()
        
        if exercises:
            print("\n🏃 Recent Exercises:")
            print(f"{'Activity':<20} {'Duration':<10} {'Calories':<10} {'Date':<12}")
            print("-" * 62)
            for exercise in exercises:
                print(f"{exercise[0]:<20} {exercise[1]} min {exercise[2] or 0:<10} {exercise[3]:<12}")
        
        conn.close()

if __name__ == "__main__":
    try:
        show_all_data()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
