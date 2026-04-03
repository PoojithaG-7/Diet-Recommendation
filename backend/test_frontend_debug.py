#!/usr/bin/env python3
"""
Test frontend debug login simulation
"""

import requests
import json

def test_frontend_simulation():
    print("=== FRONTEND DEBUG LOGIN SIMULATION ===")
    
    # Test 1: Simulate frontend debug login
    print("\n1. Testing frontend debug login simulation...")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer debug123'
    }
    
    response = requests.get('http://localhost:5000/api/debug/data', headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    # Test 2: Test with wrong password
    print("\n2. Testing with wrong password...")
    headers_wrong = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer wrongpassword'
    }
    
    response_wrong = requests.get('http://localhost:5000/api/debug/data', headers=headers_wrong)
    print(f"Status: {response_wrong.status_code}")
    print(f"Response: {response_wrong.text[:200]}")
    
    # Test 3: Test without authorization
    print("\n3. Testing without authorization...")
    response_no_auth = requests.get('http://localhost:5000/api/debug/data')
    print(f"Status: {response_no_auth.status_code}")
    print(f"Response: {response_no_auth.text[:200]}")

if __name__ == "__main__":
    test_frontend_simulation()
