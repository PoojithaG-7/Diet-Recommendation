import requests

def test_meal_functionality():
    print("=== TESTING FIXED MEAL FUNCTIONALITY ===")
    
    # Test login
    login_data = {'email': 'admin@diet-system.com', 'password': 'admin123'}
    r = requests.post('http://localhost:5000/api/auth/login', headers={'Content-Type': 'application/json'}, json=login_data)
    
    if r.status_code == 200:
        token = r.json()['token']
        print("Login successful!")
        
        # Test food nutrition endpoint
        r1 = requests.get('http://localhost:5000/api/foods/nutrition?food=rice&serving=100')
        print(f"Food nutrition status: {r1.status_code}")
        if r1.status_code == 200:
            data = r1.json()
            nutrition = data.get("nutrition", {})
            print(f"Rice nutrition: {nutrition}")
        
        # Test food search endpoint
        r2 = requests.get('http://localhost:5000/api/foods/search?q=ric')
        print(f"Food search status: {r2.status_code}")
        if r2.status_code == 200:
            data = r2.json()
            suggestions = data.get("suggestions", [])
            print(f"Search results: {suggestions}")
        
        # Test diet-log GET
        r3 = requests.get('http://localhost:5000/api/diet-log', headers={'Authorization': f'Bearer {token}'})
        print(f"Diet log GET status: {r3.status_code}")
        if r3.status_code == 200:
            data = r3.json()
            meals = data.get('meals', [])
            print(f"Found {len(meals)} meals")
            if meals:
                print(f"First meal ID: {meals[0].get('id', 'No ID')}")
        
        # Test diet-log POST
        meal_data = {
            'meal_type': 'breakfast',
            'food_name': 'Test Rice',
            'serving_size': 100,
            'calories': 130,
            'protein': 2.7,
            'carbs': 28,
            'fats': 0.3
        }
        r4 = requests.post('http://localhost:5000/api/diet-log', headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}, json=meal_data)
        print(f"Diet log POST status: {r4.status_code}")
        if r4.status_code == 200:
            print("Meal logged successfully!")
        
        print("All meal functionality tests completed!")
    else:
        print("Login failed")

if __name__ == "__main__":
    test_meal_functionality()
