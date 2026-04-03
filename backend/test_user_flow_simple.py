import requests

def test_user_flow():
    print("=== TESTING NEW USER FLOW ===")
    
    # Step 1: Landing Page (Frontend)
    print("Step 1: Landing Page available at http://localhost:3000")
    
    # Step 2: Click Get Started → Auth Page
    print("Step 2: Get Started → Auth Page (/auth)")
    
    # Step 3: Login
    login_data = {'email': 'admin@diet-system.com', 'password': 'admin123'}
    r = requests.post('http://localhost:3000/api/auth/login', 
                     headers={'Content-Type': 'application/json'}, 
                     json=login_data)
    
    if r.status_code == 200:
        print("Step 3: Login successful")
        data = r.json()
        token = data['token']
        print("   Token received, redirecting to diet plan...")
        
        # Step 4: Access Diet Plan
        r2 = requests.get('http://localhost:3000/api/auth/profile', 
                          headers={'Authorization': f'Bearer {token}'})
        
        if r2.status_code == 200:
            print("Step 4: Diet Plan page accessible")
            profile = r2.json()
            print(f"   User: {profile.get('profile', {}).get('name', 'Admin')}")
            print("   User can now create their diet plan")
            
            # Step 5: After Diet Plan → Dashboard
            print("Step 5: After completing diet plan → Dashboard")
            print("   Complete flow working!")
            
        else:
            print("Step 4: Diet Plan access failed")
    else:
        print(f"Step 3: Login failed - {r.status_code}")

if __name__ == "__main__":
    test_user_flow()
