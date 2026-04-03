import requests

# Get fresh token from frontend
r = requests.post('http://localhost:3000/api/auth/login', headers={'Content-Type': 'application/json'}, json={'email':'admin@diet-system.com','password':'admin123'})
if r.status_code == 200:
    data = r.json()
    token = data['token']
    print('=== TESTING MEAL DISPLAY FIX ===')
    
    # Log a new meal
    meal_data = {
        'meal_type': 'breakfast',
        'food_name': 'rice',
        'serving_size': 100,
        'calories': 130,
        'protein': 2.7,
        'carbs': 28,
        'fats': 0.3
    }
    r1 = requests.post('http://localhost:3000/api/diet-log', headers={'Content-Type': 'application/json', 'Authorization':f'Bearer {token}'}, json=meal_data)
    print('Log Meal Status:', r1.status_code)
    
    # Get all meals to verify
    r2 = requests.get('http://localhost:3000/api/diet-log', headers={'Authorization':f'Bearer {token}'})
    print('Get Meals Status:', r2.status_code)
    if r2.status_code == 200:
        meals = r2.json().get('meals', [])
        print(f'Total meals now: {len(meals)}')
        for meal in meals:
            print(f'- {meal.get("meal_type", "unknown")}: {meal.get("food_name", "unknown")} ({meal.get("calories", 0)} cal)')
else:
    print('Login failed:', r.status_code)
