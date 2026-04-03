import requests

def test_login_final():
    print("=== FINAL LOGIN TEST ===")
    
    # Working credentials
    print("WORKING CREDENTIALS:")
    print("Email: admin@diet-system.com")
    print("Password: admin123")
    print("")
    
    test_cases = [
        {
            'name': 'Exact credentials',
            'email': 'admin@diet-system.com',
            'password': 'admin123',
            'should_work': True
        },
        {
            'name': 'Email with different case',
            'email': 'ADMIN@diet-system.com',
            'password': 'admin123',
            'should_work': True
        },
        {
            'name': 'Email with spaces',
            'email': ' admin@diet-system.com ',
            'password': 'admin123',
            'should_work': True
        },
        {
            'name': 'Wrong password',
            'email': 'admin@diet-system.com',
            'password': 'wrong',
            'should_work': False
        },
        {
            'name': 'Wrong email',
            'email': 'wrong@email.com',
            'password': 'admin123',
            'should_work': False
        }
    ]
    
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}:")
        
        r = requests.post('http://localhost:3000/api/auth/login', 
                         headers={'Content-Type': 'application/json'}, 
                         json={'email': test_case['email'], 'password': test_case['password']})
        
        success = r.status_code == 200
        expected = test_case['should_work']
        
        if success == expected:
            print(f"   Status: {r.status_code} - CORRECT")
        else:
            print(f"   Status: {r.status_code} - INCORRECT")
            all_passed = False
    
    print(f"\n=== RESULT ===")
    if all_passed:
        print("All login tests PASSED!")
        print("Login issue has been FIXED!")
    else:
        print("Some tests failed - needs more investigation")

if __name__ == "__main__":
    test_login_final()
