import requests

# Get fresh token from frontend
r = requests.post('http://localhost:3000/api/auth/login', headers={'Content-Type': 'application/json'}, json={'email':'admin@diet-system.com','password':'admin123'})
if r.status_code == 200:
    data = r.json()
    token = data['token']
    print('=== TESTING FRONTEND TIME DISPLAY ===')
    
    # Check exercise tasks through frontend
    r1 = requests.get('http://localhost:3000/api/exercise', headers={'Authorization':f'Bearer {token}'})
    print('Exercise Status:', r1.status_code)
    if r1.status_code == 200:
        tasks = r1.json().get('exercise_tasks', [])
        for task in tasks:
            if task.get('completed'):
                print(f'Exercise: {task.get("name", "unknown")} completed at: {task.get("completed_at", "no time")}')
    
    # Check water tasks through frontend
    r2 = requests.get('http://localhost:3000/api/water', headers={'Authorization':f'Bearer {token}'})
    print('Water Status:', r2.status_code)
    if r2.status_code == 200:
        tasks = r2.json().get('water_tasks', [])
        for task in tasks:
            if task.get('completed'):
                print(f'Water: {task.get("time", "unknown")} completed at: {task.get("completed_at", "no time")}')
else:
    print('Login failed:', r.status_code)
