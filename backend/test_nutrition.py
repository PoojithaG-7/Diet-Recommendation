import requests

# Get fresh token
r = requests.post('http://localhost:3000/api/auth/login', headers={'Content-Type': 'application/json'}, json={'email':'admin@diet-system.com','password':'admin123'})
if r.status_code == 200:
    data = r.json()
    token = data['token']
    print('=== TESTING AUTOMATIC NUTRITION ===')
    # Test different serving sizes
    serving_sizes = [50, 100, 150, 200]
    for size in serving_sizes:
        r1 = requests.get(f'http://localhost:3000/api/foods/nutrition?food=rice&serving={size}', headers={'Authorization':f'Bearer {token}'})
        if r1.status_code == 200:
            nutrition = r1.json().get('nutrition', {})
            print(f'Serving {size}g: {nutrition.get("calories", 0)} cal, {nutrition.get("protein", 0)}g protein')
else:
    print('Login failed:', r.status_code)
