#!/usr/bin/env python3
"""
Setup script to create default debug admin user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import users, user_profiles, hash_password, get_ist_time

def create_debug_admin():
    """Create default debug admin user"""
    admin_email = 'admin@diet-system.com'
    admin_password = 'admin123'
    
    # Check if admin already exists
    if admin_email in users:
        print(f"Admin user {admin_email} already exists")
        return
    
    # Create admin user
    user_id = str(len(users) + 1)
    hashed_password = hash_password(admin_password)
    
    # Store user authentication
    users[admin_email] = hashed_password
    
    # Store user profile with admin role
    user_profiles[user_id] = {
        'id': user_id,
        'name': 'Debug Admin',
        'email': admin_email,
        'age': 30,
        'gender': 'other',
        'phone': '',
        'weight': 70,
        'height': 170,
        'activity_level': 'moderate',
        'goal': 'maintenance',
        'diet_plan': {},
        'created_at': get_ist_time().isoformat(),
        'updated_at': get_ist_time().isoformat(),
        'allergies': '',
        'dietary_preferences': '',
        'diseases': '',
        'medical_conditions': '',
        'role': 'admin'
    }
    
    print(f"Created debug admin user:")
    print(f"   Email: {admin_email}")
    print(f"   Password: {admin_password}")
    print(f"   Role: admin")
    print(f"   User ID: {user_id}")
    print(f"   Created at: {get_ist_time().isoformat()}")
    
    return user_id

if __name__ == '__main__':
    create_debug_admin()
