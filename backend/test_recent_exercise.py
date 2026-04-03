import requests

def test_recent_exercise():
    print("=== TESTING RECENT EXERCISE FIX ===")
    
    # Login
    r = requests.post('http://localhost:5000/api/auth/login', headers={'Content-Type': 'application/json'}, json={'email':'admin@diet-system.com','password':'admin123'})
    if r.status_code == 200:
        data = r.json()
        token = data['token']
        
        # Get exercise tasks
        r1 = requests.get('http://localhost:5000/api/exercise', headers={'Authorization':f'Bearer {token}'})
        if r1.status_code == 200:
            tasks = r1.json().get('exercise_tasks', [])
            print(f'Found {len(tasks)} exercise tasks')
            
            # Find an uncompleted task
            uncompleted_tasks = [t for t in tasks if not t.get('completed')]
            if uncompleted_tasks:
                task = uncompleted_tasks[0]
                task_id = task['id']
                task_name = task.get('name', 'Unknown')
                print(f'Completing task: {task_name} ({task_id})')
                
                # Complete exercise
                r2 = requests.post('http://localhost:5000/api/exercise', headers={'Content-Type': 'application/json', 'Authorization':f'Bearer {token}'}, json={'task_id': task_id})
                print('Exercise completion status:', r2.status_code)
                
                # Check profile for recent exercise
                r3 = requests.get('http://localhost:5000/api/auth/profile', headers={'Authorization':f'Bearer {token}'})
                if r3.status_code == 200:
                    profile_data = r3.json()
                    recent_exercise = profile_data.get('recent_exercise', [])
                    print('Recent exercise count after completion:', len(recent_exercise))
                    if recent_exercise:
                        print('First recent exercise:')
                        exercise = recent_exercise[0]
                        print(f'  Activity: {exercise.get("activity_type", "Unknown")}')
                        print(f'  Duration: {exercise.get("duration_minutes", 0)} minutes')
                        print(f'  Calories: {exercise.get("calories", 0)}')
                        print(f'  Date: {exercise.get("date", "Unknown")}')
                        print(f'  Completed at: {exercise.get("completed_at", "Unknown")}')
                    else:
                        print('No recent exercise found')
                else:
                    print('Profile check failed')
            else:
                print('No uncompleted tasks found')
        else:
            print('Failed to get exercise tasks')
    else:
        print('Login failed')

if __name__ == "__main__":
    test_recent_exercise()
