"""
Simplified Database for Diet Recommendation System
Contains only users and meals functionality
"""

import sqlite3
import os
import json
from datetime import datetime, date
import hashlib
import jwt
import pytz

class SimplifiedDietDatabase:
    def __init__(self, db_path='diet_system.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the simplified database with only users and meals"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Drop unnecessary tables if they exist
        cursor.execute("DROP TABLE IF EXISTS exercise_logs")
        cursor.execute("DROP TABLE IF EXISTS water_logs")
        cursor.execute("DROP TABLE IF EXISTS user_daily_tasks")
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create user_profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name TEXT,
                email TEXT,
                age INTEGER,
                gender TEXT,
                phone TEXT,
                weight REAL,
                height REAL,
                bmi REAL,
                bmi_category TEXT,
                activity_level TEXT,
                goal TEXT,
                dietary_notes TEXT,
                diet_plan TEXT,
                daily_calories_needed INTEGER,
                profile_completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create diet_logs table (only meal functionality)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diet_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                meal_type TEXT NOT NULL,
                food_name TEXT NOT NULL,
                serving_size TEXT,
                calories REAL DEFAULT 0,
                protein REAL DEFAULT 0,
                carbs REAL DEFAULT 0,
                fats REAL DEFAULT 0,
                date DATE NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Simplified database initialized successfully!")
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_user(self, email, password, name):
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Hash password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO users (email, password, name) 
                VALUES (?, ?, ?)
            ''', (email, hashed_password, name))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    def authenticate_user(self, email, password):
        """Authenticate user and return user data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
            SELECT id, email, name FROM users 
            WHERE email = ? AND password = ?
        ''', (email, hashed_password))
        
        user = cursor.fetchone()
        
        if user:
            # Get user profile
            cursor.execute('''
                SELECT age, gender, weight, height, bmi, activity_level, goal,
                       dietary_notes, diet_plan, daily_calories_needed, profile_completed
                FROM user_profiles WHERE user_id = ?
            ''', (user['id'],))
            
            profile = cursor.fetchone()
            conn.close()
            
            return {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'profile': profile
            }
        
        conn.close()
        return None
    
    def update_user_profile(self, user_id, profile_data):
        """Update or create user profile"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Calculate BMI if weight and height provided
        bmi = None
        bmi_category = None
        if profile_data.get('weight') and profile_data.get('height'):
            height_m = profile_data['height'] / 100
            bmi = round(profile_data['weight'] / (height_m ** 2), 1)
            
            if bmi < 18.5:
                bmi_category = 'Underweight'
            elif bmi < 25:
                bmi_category = 'Normal'
            elif bmi < 30:
                bmi_category = 'Overweight'
            else:
                bmi_category = 'Obese'
        
        # Calculate daily calories needed
        daily_calories = 2000  # Default
        if profile_data.get('weight') and profile_data.get('height') and profile_data.get('age'):
            weight = profile_data['weight']
            height = profile_data['height']
            age = profile_data['age']
            gender = profile_data.get('gender', 'male')
            activity_level = profile_data.get('activity_level', 'moderate')
            
            # Mifflin-St Jeor Equation
            if gender.lower() == 'male':
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161
            
            activity_multipliers = {
                'sedentary': 1.2,
                'light': 1.375,
                'moderate': 1.55,
                'active': 1.725,
                'very_active': 1.9
            }
            
            daily_calories = int(bmr * activity_multipliers.get(activity_level, 1.55))
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_profiles 
            (user_id, name, email, age, gender, phone, weight, height, bmi, 
             bmi_category, activity_level, goal, dietary_notes, diet_plan, 
             daily_calories_needed, profile_completed, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            user_id,
            profile_data.get('name'),
            profile_data.get('email'),
            profile_data.get('age'),
            profile_data.get('gender'),
            profile_data.get('phone'),
            profile_data.get('weight'),
            profile_data.get('height'),
            bmi,
            bmi_category,
            profile_data.get('activity_level'),
            profile_data.get('goal'),
            profile_data.get('dietary_notes'),
            json.dumps(profile_data.get('diet_plan', {})),
            daily_calories,
            bool(profile_data.get('weight') and profile_data.get('height'))
        ))
        
        conn.commit()
        conn.close()
    
    def log_meal(self, user_id, meal_data):
        """Log a meal for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO diet_logs 
            (user_id, meal_type, food_name, serving_size, calories, protein, carbs, fats, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            meal_data['meal_type'],
            meal_data['food_name'],
            meal_data.get('serving_size', ''),
            meal_data.get('calories', 0),
            meal_data.get('protein', 0),
            meal_data.get('carbs', 0),
            meal_data.get('fats', 0),
            meal_data.get('date', date.today().isoformat())
        ))
        
        conn.commit()
        conn.close()
    
    def get_meals_for_date(self, user_id, date):
        """Get all meals for a user on a specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, meal_type, food_name, serving_size, calories, protein, carbs, fats, date, completed_at
            FROM diet_logs 
            WHERE user_id = ? AND date = ?
            ORDER BY completed_at ASC
        ''', (user_id, date))
        
        meals = []
        for row in cursor.fetchall():
            meals.append({
                'id': row['id'],
                'meal_type': row['meal_type'],
                'food_name': row['food_name'],
                'serving_size': row['serving_size'],
                'calories': row['calories'],
                'protein': row['protein'],
                'carbs': row['carbs'],
                'fats': row['fats'],
                'date': row['date'],
                'completed_at': row['completed_at']
            })
        
        conn.close()
        return meals
    
    def delete_meal(self, user_id, meal_id):
        """Delete a specific meal"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM diet_logs 
            WHERE id = ? AND user_id = ?
        ''', (meal_id, user_id))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    def get_all_users(self):
        """Get all users with their profiles"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.email, u.name, u.created_at,
                   p.age, p.gender, p.weight, p.height, p.bmi,
                   p.activity_level, p.goal, p.daily_calories_needed,
                   p.profile_completed, p.diet_plan
            FROM users u
            LEFT JOIN user_profiles p ON u.id = p.user_id
            ORDER BY u.created_at DESC
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row['id'],
                'email': row['email'],
                'name': row['name'],
                'age': row['age'],
                'gender': row['gender'],
                'weight': row['weight'],
                'height': row['height'],
                'bmi': row['bmi'],
                'activity_level': row['activity_level'],
                'goal': row['goal'],
                'daily_calories_needed': row['daily_calories_needed'],
                'has_diet_plan': bool(row['diet_plan']),
                'profile_completed': bool(row['profile_completed'])
            })
        
        conn.close()
        return users
    
    def get_database_stats(self):
        """Get database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # User counts
        cursor.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_profiles WHERE profile_completed = 1")
        stats['completed_profiles'] = cursor.fetchone()[0]
        
        # Meal counts
        cursor.execute("SELECT COUNT(*) FROM diet_logs")
        stats['total_meals'] = cursor.fetchone()[0]
        
        # Today's meals
        today = date.today().isoformat()
        cursor.execute("SELECT COUNT(*) FROM diet_logs WHERE date = ?", (today,))
        stats['today_meals'] = cursor.fetchone()[0]
        
        # Table counts
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        stats['tables'] = [table['name'] for table in tables]
        
        conn.close()
        return stats

# Initialize database
if __name__ == "__main__":
    db = SimplifiedDietDatabase()
    print("Simplified database setup complete!")
    print(f"Database file: {os.path.abspath(db.db_path)}")
    
    # Show database statistics
    stats = db.get_database_stats()
    print(f"\nDatabase Statistics:")
    print(f"Total Users: {stats['total_users']}")
    print(f"Completed Profiles: {stats['completed_profiles']}")
    print(f"Total Meals: {stats['total_meals']}")
    print(f"Today's Meals: {stats['today_meals']}")
    print(f"Tables: {stats['tables']}")
