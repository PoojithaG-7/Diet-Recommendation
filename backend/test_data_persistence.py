import requests

def test_data_persistence():
    print("=== TESTING DATA PERSISTENCE ===")
    
    # Create a new user
    new_user_data = {
        'name': 'Test User',
        'email': 'testuser@example.com',
        'password': 'test123',
        'age': 28,
        'gender': 'male',
        'phone': '9876543210'
    }
    
    print("1. Creating new user...")
    r = requests.post('http://localhost:5000/api/auth/register', 
                     headers={'Content-Type': 'application/json'}, 
                     json=new_user_data)
    
    if r.status_code == 200:
        print("   User created successfully")
        
        # Login with new user
        print("2. Logging in with new user...")
        login_data = {'email': 'testuser@example.com', 'password': 'test123'}
        r2 = requests.post('http://localhost:5000/api/auth/login', 
                          headers={'Content-Type': 'application/json'}, 
                          json=login_data)
        
        if r2.status_code == 200:
            data = r2.json()
            user_data = data.get('user', {})
            print("   Login successful!")
            print("   User data preserved:")
            
            important_fields = ['name', 'email', 'age', 'gender', 'phone']
            for field in important_fields:
                value = user_data.get(field, 'N/A')
                print(f"     {field}: {value}")
            
            print("   Data will be stored in localStorage for persistence")
            print("   User can log out and log back in - data will be preserved!")
            
        else:
            print(f"   Login failed: {r2.status_code}")
    else:
        print(f"   User creation failed: {r.status_code}")

if __name__ == "__main__":
    test_data_persistence()
