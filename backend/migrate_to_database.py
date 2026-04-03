import json
from database import DietDatabase
from datetime import datetime, date

def migrate_from_memory():
    """Migrate data from in-memory storage to database"""
    print("=== MIGRATING TO DATABASE ===")
    
    db = DietDatabase()
    
    # Import current in-memory data (this would need to be adapted based on actual data structure)
    # For now, let's create the admin user in the database
    admin_email = "admin@diet-system.com"
    admin_password = "admin123"  # In production, this should be hashed
    admin_name = "Debug Admin"
    
    # Create admin user
    user_id = db.create_user(admin_email, admin_password, admin_name)
    
    if user_id:
        print(f"Created admin user with ID: {user_id}")
        
        # Create admin profile with existing data
        admin_profile = {
            'name': admin_name,
            'email': admin_email,
            'age': 30,
            'gender': 'other',
            'phone': '',
            'weight': 70,
            'height': 170,
            'activity_level': 'moderate',
            'goal': 'maintenance',
            'dietary_notes': '',
            'diet_plan': {
                'diet_plan_info': {
                    'daily_calorie_needs': 2000,
                    'goal': 'maintenance',
                    'user_metrics': {
                        'bmi': 24.2,
                        'bmi_category': 'normal',
                        'height': 170,
                        'weight': 70
                    }
                },
                'recommended_meals': {
                    'breakfast': 'Oatmeal with fruits',
                    'lunch': 'Grilled chicken salad',
                    'dinner': 'Vegetable curry with rice',
                    'snacks': 'Mixed nuts and seeds'
                }
            }
        }
        
        db.update_user_profile(user_id, admin_profile)
        print("Admin profile created/updated")
        
        # Test the database
        auth_result = db.authenticate_user(admin_email, admin_password)
        if auth_result:
            print("✅ Admin user authentication successful!")
            print(f"User ID: {auth_result['id']}")
            print(f"Name: {auth_result['name']}")
            print(f"Email: {auth_result['email']}")
            if auth_result['profile']:
                print(f"Weight: {auth_result['profile'][6]} kg")
                print(f"Height: {auth_result['profile'][7]} cm")
                print(f"BMI: {auth_result['profile'][8]}")
        else:
            print("❌ Admin user authentication failed")
    else:
        print("❌ Failed to create admin user (might already exist)")
    
    print("\n=== DATABASE MIGRATION COMPLETE ===")
    print("Database is now ready for use!")
    print("All data will persist between server restarts.")

if __name__ == "__main__":
    migrate_from_memory()
