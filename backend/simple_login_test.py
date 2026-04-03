#!/usr/bin/env python3
"""
Simple test to bypass authentication and test basic functionality
"""

import requests
import json

def test_login():
    """Test login without JWT complications"""
    url = "http://localhost:5000/api/auth/login"
    headers = {"Content-Type": "application/json"}
    data = {
        "email": "admin@diet-system.com",
        "password": "admin123"
    }
    
    try:
        print(f"Sending request to: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        print(f"Headers: {headers}")
        
        response = requests.post(url, headers=headers, json=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"JSON Response: {json.dumps(result, indent=2)}")
                
                if 'token' in result:
                    print(f"SUCCESS: Token received: {result['token'][:50]}...")
                    print("Login should work with this token")
                else:
                    print("ERROR: No token in response")
            except json.JSONDecodeError as e:
                print(f"ERROR: Invalid JSON: {e}")
        else:
            print(f"ERROR: HTTP {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"ERROR: Request failed: {e}")

if __name__ == "__main__":
    test_login()
