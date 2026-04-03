#!/usr/bin/env python3
"""
Test login with curl to bypass any frontend caching
"""

import subprocess
import json

# Test login with curl
result = subprocess.run([
    'curl', '-X', 'POST',
    '-H', 'Content-Type: application/json',
    '-d', '{"email":"admin@diet-system.com","password":"admin123"}',
    'http://localhost:5000/api/auth/login'
], capture_output=True, text=True)

print("CURL Command:")
print("Status:", result.returncode)
print("Output:", result.stdout)
print("Error:", result.stderr)

# Parse JSON response if possible
if result.returncode == 0:
    try:
        response = json.loads(result.stdout)
        print("Parsed Response:", json.dumps(response, indent=2))
    except:
        print("Could not parse JSON response")
