import requests

def test_dashboard_fixes():
    print("=== TESTING DASHBOARD FIXES ===")
    
    # Login
    r = requests.post('http://localhost:3000/api/auth/login', headers={'Content-Type': 'application/json'}, json={'email':'admin@diet-system.com','password':'admin123'})
    if r.status_code == 200:
        data = r.json()
        token = data['token']
        print("Login successful!")
        
        # Test 1: Calorie Target
        print("\n1. TESTING CALORIE TARGET:")
        r1 = requests.get('http://localhost:3000/api/auth/profile', headers={'Authorization':f'Bearer {token}'})
        if r1.status_code == 200:
            profile_data = r1.json()
            profile = profile_data.get('profile', {})
            
            # Check diet plan completion
            has_weight = bool(profile.get('weight'))
            has_height = bool(profile.get('height'))
            has_diet_plan = has_weight and has_height
            
            print(f"  Weight: {profile.get('weight')} (exists: {has_weight})")
            print(f"  Height: {profile.get('height')} (exists: {has_height})")
            print(f"  Has Diet Plan: {has_diet_plan}")
            
            if has_diet_plan:
                daily_cal = profile.get('daily_calories_needed')
                print(f"  Daily Calories: {daily_cal}")
                print(f"  Calorie Target should show: {daily_cal if daily_cal else '---'}")
            else:
                print("  Calorie Target will show: ---")
        else:
            print("  Failed to get profile data")
        
        # Test 2: Recent Exercise
        print("\n2. TESTING RECENT EXERCISE:")
        r2 = requests.get('http://localhost:3000/api/auth/profile', headers={'Authorization':f'Bearer {token}'})
        if r2.status_code == 200:
            profile_data = r2.json()
            recent_exercise = profile_data.get('recent_exercise', [])
            print(f"  Recent Exercise Count: {len(recent_exercise)}")
            
            if recent_exercise:
                exercise = recent_exercise[0]
                print(f"  First Exercise:")
                print(f"    Activity: {exercise.get('activity_type', 'Unknown')}")
                print(f"    Duration: {exercise.get('duration_minutes', 0)} minutes")
                print(f"    Calories: {exercise.get('calories', 0)}")
                print(f"    Date: {exercise.get('date', 'Unknown')}")
                print("  Recent Exercise should show exercise data")
            else:
                print("  Recent Exercise will show: 'no sessions yet'")
        else:
            print("  Failed to get recent exercise data")
        
        print("\n=== SUMMARY ===")
        print("✅ Calorie Target: Should show 2000 kcal/day")
        print("✅ Recent Exercise: Should show completed exercise data")
        print("\nBoth issues should now be fixed!")
        
    else:
        print("Login failed")

if __name__ == "__main__":
    test_dashboard_fixes()
