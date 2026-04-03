#!/usr/bin/env python3
"""
Test debug login flow to identify exact issue
"""

import requests
import json

def test_debug_flow():
    print("=== DEBUG FLOW TEST ===")
    
    # Test 1: Direct backend call with correct password
    print("\n1. Testing direct backend call...")
    response = requests.get('http://localhost:5000/api/debug/users', 
                         headers={'Authorization': 'Bearer debug123'})
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("Backend accepts debug123 password")
    else:
        print(f"Backend rejects debug123 password")
        print(f"Response: {response.text}")
    
    # Test 2: Check if there are multiple debug endpoints
    print("\n2. Testing debug/data endpoint...")
    response2 = requests.get('http://localhost:5000/api/debug/data', 
                          headers={'Authorization': 'Bearer debug123'})
    print(f"Status: {response2.status_code}")
    
    if response2.status_code == 200:
        print("Debug data endpoint works")
    else:
        print(f"Debug data endpoint fails")
        print(f"Response: {response2.text[:200]}")
    
    # Test 3: Check if frontend is calling wrong endpoint
    print("\n3. Testing frontend debug endpoint...")
    try:
        response3 = requests.get('http://localhost:5000/api/debug/data')
        print(f"Status: {response3.status_code}")
        if response3.status_code == 401:
            print("Frontend debug endpoint requires password (correct)")
        else:
            print(f"Frontend debug endpoint doesn't require password")
            print(f"Response: {response3.text[:200]}")
    except:
        print("Frontend debug endpoint not accessible")

if __name__ == "__main__":
    test_debug_flow()
