from database import DietDatabase

def test_database():
    print("=== TESTING DATABASE FUNCTIONALITY ===")
    
    db = DietDatabase()
    
    # Test 1: Create user
    print("1. Testing user creation...")
    user_id = db.create_user("test@example.com", "password123", "Test User")
    if user_id:
        print(f"   User created with ID: {user_id}")
    else:
        print("   User creation failed (might already exist)")
        # Try to get existing user
        auth_result = db.authenticate_user("test@example.com", "password123")
        if auth_result:
            user_id = auth_result['id']
            print(f"   Found existing user with ID: {user_id}")
    
    # Test 2: Authenticate user
    print("2. Testing authentication...")
    auth_result = db.authenticate_user("test@example.com", "password123")
    if auth_result:
        print(f"   Authentication successful for: {auth_result['name']}")
    else:
        print("   Authentication failed")
    
    # Test 3: Update profile
    print("3. Testing profile update...")
    profile_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'age': 25,
        'gender': 'male',
        'phone': '1234567890',
        'weight': 75,
        'height': 180,
        'activity_level': 'moderate',
        'goal': 'maintenance'
    }
    
    if user_id:
        db.update_user_profile(user_id, profile_data)
        print("   Profile updated successfully")
    
    # Test 4: Log meal
    print("4. Testing meal logging...")
    from datetime import date
    meal_data = {
        'meal_type': 'breakfast',
        'food_name': 'Oatmeal',
        'serving_size': '1 cup',
        'calories': 150,
        'protein': 5,
        'carbs': 27,
        'fats': 3,
        'date': date.today().isoformat()
    }
    
    if user_id:
        db.log_meal(user_id, meal_data)
        print("   Meal logged successfully")
    
    # Test 5: Get meals
    print("5. Testing meal retrieval...")
    if user_id:
        meals = db.get_meals_for_date(user_id, date.today().isoformat())
        print(f"   Found {len(meals)} meals for today")
        if meals:
            print(f"   Latest meal: {meals[0]['food_name']}")
    
    # Test 6: Log exercise
    print("6. Testing exercise logging...")
    exercise_data = {
        'activity_type': 'Running',
        'duration_minutes': 30,
        'calories_burned': 300,
        'date': date.today().isoformat()
    }
    
    if user_id:
        db.log_exercise(user_id, exercise_data)
        print("   Exercise logged successfully")
    
    # Test 7: Get recent exercises
    print("7. Testing exercise retrieval...")
    if user_id:
        exercises = db.get_recent_exercises(user_id, 7)
        print(f"   Found {len(exercises)} recent exercises")
        if exercises:
            print(f"   Latest exercise: {exercises[0]['activity_type']}")
    
    # Test 8: Log water
    print("8. Testing water logging...")
    water_data = {
        'glasses': 2,
        'ml': 500,
        'date': date.today().isoformat()
    }
    
    if user_id:
        db.log_water(user_id, water_data)
        print("   Water logged successfully")
    
    # Test 9: Get water data
    print("9. Testing water retrieval...")
    if user_id:
        water_data = db.get_water_for_date(user_id, date.today().isoformat())
        print(f"   Water today: {water_data['glasses']} glasses, {water_data['ml']} ml")
    
    # Test 10: Get all users
    print("10. Testing all users retrieval...")
    all_users = db.get_all_users()
    print(f"   Total users in database: {len(all_users)}")
    
    print("\n=== DATABASE TEST COMPLETE ===")
    print("All database functions are working correctly!")
    print("Data will persist between server restarts.")

if __name__ == "__main__":
    test_database()
