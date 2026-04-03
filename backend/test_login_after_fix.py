import requests

def test_login_after_fix():
    print("=== TESTING LOGIN AFTER FIX ===")
    
    login_data = {'email': 'admin@diet-system.com', 'password': 'admin123'}
    
    # Test backend
    r = requests.post('http://localhost:5000/api/auth/login', headers={'Content-Type': 'application/json'}, json=login_data)
    print('Backend Login Status:', r.status_code)
    
    # Test frontend
    r2 = requests.post('http://localhost:3000/api/auth/login', headers={'Content-Type': 'application/json'}, json=login_data)
    print('Frontend Login Status:', r2.status_code)
    
    if r2.status_code == 200:
        print('Frontend Login: SUCCESS')
        data = r2.json()
        user = data.get('user', {})
        print('User:', user.get('name', 'Unknown'))
        print('Email:', user.get('email', 'Unknown'))
        print('Login issue has been FIXED!')
    else:
        print('Frontend Login: FAILED')
        print('Response:', r2.text[:200])

if __name__ == "__main__":
    test_login_after_fix()
