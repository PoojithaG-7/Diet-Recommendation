import requests

def test_exercise_fix():
    print("=== TESTING EXERCISE FIX ===")
    
    # Login as admin
    r = requests.post('http://localhost:5000/api/auth/login', 
                     headers={'Content-Type': 'application/json'}, 
                     json={'email':'admin@diet-system.com','password':'admin123'})
    
    if r.status_code == 200:
        token = r.json()['token']
        print("Login successful!")
        
        # Get exercise tasks
        r1 = requests.get('http://localhost:5000/api/exercise', 
                          headers={'Authorization':f'Bearer {token}'})
        
        if r1.status_code == 200:
            tasks = r1.json().get('exercise_tasks', [])
            print(f'Found {len(tasks)} exercise tasks')
            
            # Find an uncompleted task
            uncompleted = [t for t in tasks if not t.get('completed')]
            if uncompleted:
                task = uncompleted[0]
                print(f'Completing: {task.get("name", "Unknown")}')
                print(f'Duration: {task.get("duration", "N/A")} min')
                print(f'Calories: {task.get("calories", "N/A")}')
                
                # Complete the task
                r2 = requests.post('http://localhost:5000/api/exercise', 
                                  headers={'Content-Type': 'application/json', 'Authorization':f'Bearer {token}'}, 
                                  json={'task_id': task['id']})
                print(f'Completion status: {r2.status_code}')
                
                # Check recent exercise
                r3 = requests.get('http://localhost:5000/api/auth/profile', 
                                  headers={'Authorization':f'Bearer {token}'})
                
                if r3.status_code == 200:
                    profile_data = r3.json()
                    recent_exercise = profile_data.get('recent_exercise', [])
                    print(f'Recent exercise count: {len(recent_exercise)}')
                    
                    if recent_exercise:
                        exercise = recent_exercise[0]
                        print(f'Latest exercise:')
                        print(f'  Activity: {exercise.get("activity_type", "Unknown")}')
                        print(f'  Duration: {exercise.get("duration_minutes", "N/A")} min')
                        print(f'  Calories: {exercise.get("calories_burned", "N/A")}')
                        print(f'  Completed at: {exercise.get("completed_at", "N/A")}')
                        
                        # Test the date parsing
                        completed_at = exercise.get("completed_at")
                        if completed_at and completed_at != "Invalid Date":
                            try:
                                import datetime
                                dt = datetime.datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                                print(f'  Parsed time: {dt.strftime("%I:%M %p")}')
                                print("Date parsing works correctly!")
                            except Exception as e:
                                print(f'  Date parsing error: {e}')
                        else:
                            print("Date issue detected!")
                    else:
                        print("No recent exercise found")
                else:
                    print("Failed to get profile data")
            else:
                print("No uncompleted tasks found")
        else:
            print("Failed to get exercise tasks")
    else:
        print("Login failed")

if __name__ == "__main__":
    test_exercise_fix()
