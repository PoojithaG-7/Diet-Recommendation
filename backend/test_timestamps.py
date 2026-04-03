import requests

# Get fresh token
r = requests.post('http://localhost:5000/api/auth/login', headers={'Content-Type': 'application/json'}, json={'email':'admin@diet-system.com','password':'admin123'})
if r.status_code == 200:
    data = r.json()
    token = data['token']
    print('=== CHECKING FIXED TIMESTAMPS ===')
    
    # Check exercise tasks
    r1 = requests.get('http://localhost:5000/api/exercise', headers={'Authorization':f'Bearer {token}'})
    if r1.status_code == 200:
        tasks = r1.json().get('exercise_tasks', [])
        for task in tasks:
            if task.get('completed'):
                print(f'Exercise: {task.get("name", "unknown")} completed at: {task.get("completed_at", "no time")}')
    
    # Check water tasks
    r2 = requests.get('http://localhost:5000/api/water', headers={'Authorization':f'Bearer {token}'})
    if r2.status_code == 200:
        tasks = r2.json().get('water_tasks', [])
        for task in tasks:
            if task.get('completed'):
                print(f'Water: {task.get("time", "unknown")} completed at: {task.get("completed_at", "no time")}')
else:
    print('Login failed:', r.status_code)
