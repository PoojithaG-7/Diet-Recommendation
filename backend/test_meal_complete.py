import requests

# Get fresh token from frontend
r = requests.post('http://localhost:3000/api/auth/login', headers={'Content-Type': 'application/json'}, json={'email':'admin@diet-system.com','password':'admin123'})
if r.status_code == 200:
    data = r.json()
    token = data['token']
    print('=== TESTING COMPLETE MEAL FLOW ===')
    # Test getting meals after logging
    r1 = requests.get('http://localhost:3000/api/diet-log', headers={'Authorization':f'Bearer {token}'})
    print('Get Meals Status:', r1.status_code)
    if r1.status_code == 200:
        meals = r1.json().get('meals', [])
        print(f'Total meals logged: {len(meals)}')
        for meal in meals:
            print(f'- {meal.get("meal_type", "unknown")}: {meal.get("food_name", "unknown")} ({meal.get("calories", 0)} cal)')
else:
    print('Login failed:', r.status_code)
