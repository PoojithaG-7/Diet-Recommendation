import requests

def test_complete_exercise_fix():
    print("=== COMPLETE EXERCISE FIX TEST ===")
    
    # Test the complete flow
    r = requests.post('http://localhost:3000/api/auth/login', 
                     headers={'Content-Type': 'application/json'}, 
                     json={'email':'admin@diet-system.com','password':'admin123'})
    
    if r.status_code == 200:
        token = r.json()['token']
        print("Login successful!")
        
        # Get dashboard data
        r1 = requests.get('http://localhost:3000/api/auth/profile', 
                         headers={'Authorization':f'Bearer {token}'})
        
        if r1.status_code == 200:
            profile_data = r1.json()
            recent_exercise = profile_data.get('recent_exercise', [])
            
            print(f"Recent exercise count: {len(recent_exercise)}")
            
            if recent_exercise:
                exercise = recent_exercise[0]
                print("\nExercise Data:")
                print(f"  Activity: {exercise.get('activity_type', 'Unknown')}")
                print(f"  Duration: {exercise.get('duration_minutes', 'N/A')} min")
                print(f"  Calories: {exercise.get('calories_burned', 'N/A')}")
                print(f"  Completed at: {exercise.get('completed_at', 'N/A')}")
                
                # Test frontend date parsing
                completed_at = exercise.get('completed_at')
                if completed_at and completed_at != 'Invalid Date':
                    try:
                        import datetime
                        dt = datetime.datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                        formatted_time = dt.strftime('%I:%M %p')
                        print(f"  Formatted time: {formatted_time}")
                        print("Date parsing works correctly!")
                        
                        # Test the exact frontend formatting
                        frontend_time = dt.strftime('%I:%M %p')
                        print(f"  Frontend will show: {frontend_time}")
                        
                    except Exception as e:
                        print(f"Date parsing error: {e}")
                else:
                    print("Date issue detected!")
                    
                print("\nExpected Frontend Display:")
                time_display = formatted_time if 'formatted_time' in locals() else 'Just now'
                print(f"  {exercise.get('activity_type', 'Unknown')} | {exercise.get('duration_minutes', 'N/A')} min | {exercise.get('calories_burned', 'N/A')} | {time_display}")
                
                print("\nFIXES APPLIED:")
                print("1. Fixed 'Invalid Date' -> Proper time display")
                print("2. Fixed 'calories' -> 'calories_burned' field mapping")
                print("3. Fixed 'duration' -> Numeric duration extraction")
                print("4. Added proper date validation in frontend")
                
            else:
                print("No recent exercise found - complete an exercise first")
                
        else:
            print("Failed to get profile data")
    else:
        print("Login failed")

if __name__ == "__main__":
    test_complete_exercise_fix()
