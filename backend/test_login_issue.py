import requests

def test_login_issue():
    print("=== TESTING LOGIN ISSUE ===")
    
    # Test exact same format as frontend
    login_data = {
        'email': 'admin@diet-system.com',
        'password': 'admin123'
    }
    
    print("Testing with admin credentials...")
    print(f"Email: {login_data['email']}")
    print(f"Password: {login_data['password']}")
    
    # Test backend directly
    print("\n1. Backend Direct Test:")
    r = requests.post('http://localhost:5000/api/auth/login', 
                     headers={'Content-Type': 'application/json'}, 
                     json=login_data)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:200]}")
    
    # Test through frontend proxy
    print("\n2. Frontend Proxy Test:")
    r2 = requests.post('http://localhost:3000/api/auth/login', 
                      headers={'Content-Type': 'application/json'}, 
                      json=login_data)
    print(f"Status: {r2.status_code}")
    print(f"Response: {r2.text[:200]}")
    
    # Test with different email case
    print("\n3. Testing with different email case:")
    login_data_case = {
        'email': 'Admin@Diet-System.com',
        'password': 'admin123'
    }
    r3 = requests.post('http://localhost:5000/api/auth/login', 
                     headers={'Content-Type': 'application/json'}, 
                     json=login_data_case)
    print(f"Status: {r3.status_code}")
    print(f"Response: {r3.text[:100]}")
    
    # Test with extra spaces
    print("\n4. Testing with extra spaces:")
    login_data_spaces = {
        'email': ' admin@diet-system.com ',
        'password': ' admin123 '
    }
    r4 = requests.post('http://localhost:5000/api/auth/login', 
                     headers={'Content-Type': 'application/json'}, 
                     json=login_data_spaces)
    print(f"Status: {r4.status_code}")
    print(f"Response: {r4.text[:100]}")

if __name__ == "__main__":
    test_login_issue()
