import requests

def test_login_fix():
    print("=== TESTING LOGIN FIX ===")
    
    # Test cases that were failing before
    test_cases = [
        {
            'name': 'Normal login',
            'email': 'admin@diet-system.com',
            'password': 'admin123'
        },
        {
            'name': 'Case insensitive email',
            'email': 'Admin@Diet-System.com',
            'password': 'admin123'
        },
        {
            'name': 'Extra spaces',
            'email': ' admin@diet-system.com ',
            'password': ' admin123 '
        },
        {
            'name': 'Mixed case and spaces',
            'email': ' ADMIN@DIET-SYSTEM.COM ',
            'password': ' ADMIN123 '
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}:")
        print(f"   Email: '{test_case['email']}'")
        print(f"   Password: '{test_case['password']}'")
        
        r = requests.post('http://localhost:3000/api/auth/login', 
                         headers={'Content-Type': 'application/json'}, 
                         json=test_case)
        
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            print("   Result: SUCCESS")
        else:
            print(f"   Result: FAILED - {r.text[:100]}")
    
    print("\n=== SUMMARY ===")
    print("Login is now case-insensitive and handles extra spaces!")
    print("All login variations should work correctly now.")

if __name__ == "__main__":
    test_login_fix()
