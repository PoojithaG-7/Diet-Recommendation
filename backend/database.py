import sqlite3
import json
from datetime import datetime
import os

class DietDatabase:
    def __init__(self, db_path='diet_system.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User profiles table
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
        
        # Diet logs table
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
        
        # Exercise logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercise_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                calories_burned INTEGER DEFAULT 0,
                date DATE NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Water logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS water_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                glasses INTEGER NOT NULL,
                ml INTEGER NOT NULL,
                date DATE NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # User daily tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_daily_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                task_type TEXT NOT NULL,
                task_id TEXT NOT NULL,
                task_name TEXT NOT NULL,
                task_data TEXT,
                completed BOOLEAN DEFAULT FALSE,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, date, task_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"Database initialized at {self.db_path}")
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def create_user(self, email, password, name):
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)',
                         (email, password, name))
            user_id = cursor.lastrowid
            
            # Create empty profile
            cursor.execute('''
                INSERT INTO user_profiles (user_id, email, name) 
                VALUES (?, ?, ?)
            ''', (user_id, email, name))
            
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
        finally:
            conn.close()
    
    def authenticate_user(self, email, password):
        """Authenticate user and return user data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, email, password, name FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if user and user[2] == password:  # In production, use proper password hashing
            cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user[0],))
            profile = cursor.fetchone()
            
            conn.close()
            
            return {
                'id': user[0],
                'email': user[1],
                'name': user[3],
                'profile': self._dict_from_row(profile) if profile else None
            }
        else:
            conn.close()
            return None
    
    def update_user_profile(self, user_id, profile_data):
        """Update user profile"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Calculate BMI if weight and height provided
        bmi = None
        bmi_category = None
        if profile_data.get('weight') and profile_data.get('height'):
            height_m = profile_data['height'] / 100
            bmi = profile_data['weight'] / (height_m * height_m)
            
            if bmi < 18.5:
                bmi_category = 'underweight'
            elif bmi < 25:
                bmi_category = 'normal'
            elif bmi < 30:
                bmi_category = 'overweight'
            else:
                bmi_category = 'obese'
        
        # Calculate daily calories (simplified formula)
        daily_calories = 2000  # Default
        if bmi:
            if profile_data.get('goal') == 'weight_loss':
                daily_calories = int(daily_calories * 0.8)
            elif profile_data.get('goal') == 'muscle_gain':
                daily_calories = int(daily_calories * 1.2)
        
        cursor.execute('''
            UPDATE user_profiles SET 
                name = ?, age = ?, gender = ?, phone = ?, weight = ?, height = ?,
                bmi = ?, bmi_category = ?, activity_level = ?, goal = ?,
                dietary_notes = ?, diet_plan = ?, daily_calories_needed = ?,
                profile_completed = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (
            profile_data.get('name'), profile_data.get('age'), profile_data.get('gender'),
            profile_data.get('phone'), profile_data.get('weight'), profile_data.get('height'),
            bmi, bmi_category, profile_data.get('activity_level'), profile_data.get('goal'),
            profile_data.get('dietary_notes'), json.dumps(profile_data.get('diet_plan', {})),
            daily_calories, bool(profile_data.get('weight') and profile_data.get('height')),
            user_id
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
            user_id, meal_data['meal_type'], meal_data['food_name'],
            meal_data.get('serving_size', ''), meal_data.get('calories', 0),
            meal_data.get('protein', 0), meal_data.get('carbs', 0), meal_data.get('fats', 0),
            meal_data['date']
        ))
        
        conn.commit()
        conn.close()
    
    def get_meals_for_date(self, user_id, date):
        """Get all meals for a user on a specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM diet_logs 
            WHERE user_id = ? AND date = ?
            ORDER BY completed_at DESC
        ''', (user_id, date))
        
        meals = [self._dict_from_row(row) for row in cursor.fetchall()]
        conn.close()
        return meals
    
    def log_exercise(self, user_id, exercise_data):
        """Log an exercise for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO exercise_logs 
            (user_id, activity_type, duration_minutes, calories_burned, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id, exercise_data['activity_type'], exercise_data['duration_minutes'],
            exercise_data.get('calories_burned', 0), exercise_data['date']
        ))
        
        conn.commit()
        conn.close()
    
    def get_recent_exercises(self, user_id, days=7):
        """Get recent exercises for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM exercise_logs 
            WHERE user_id = ? AND date >= date('now', '-{} days')
            ORDER BY completed_at DESC
            LIMIT 10
        '''.format(days), (user_id,))
        
        exercises = [self._dict_from_row(row) for row in cursor.fetchall()]
        conn.close()
        return exercises
    
    def log_water(self, user_id, water_data):
        """Log water intake for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO water_logs 
            (user_id, glasses, ml, date)
            VALUES (?, ?, ?, ?)
        ''', (
            user_id, water_data['glasses'], water_data['ml'], water_data['date']
        ))
        
        conn.commit()
        conn.close()
    
    def get_water_for_date(self, user_id, date):
        """Get water intake for a user on a specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT SUM(glasses), SUM(ml) FROM water_logs 
            WHERE user_id = ? AND date = ?
        ''', (user_id, date))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'glasses': result[0] or 0,
            'ml': result[1] or 0
        }
    
    def save_daily_task(self, user_id, date, task_type, task_id, task_name, task_data):
        """Save a daily task for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_daily_tasks 
            (user_id, date, task_type, task_id, task_name, task_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, date, task_type, task_id, task_name, json.dumps(task_data)))
        
        conn.commit()
        conn.close()
    
    def complete_daily_task(self, user_id, date, task_id):
        """Mark a daily task as completed"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_daily_tasks 
            SET completed = TRUE, completed_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND date = ? AND task_id = ?
        ''', (user_id, date, task_id))
        
        conn.commit()
        conn.close()
    
    def get_daily_tasks(self, user_id, date):
        """Get all daily tasks for a user on a specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_daily_tasks 
            WHERE user_id = ? AND date = ?
            ORDER BY task_type, task_name
        ''', (user_id, date))
        
        tasks = []
        for row in cursor.fetchall():
            task = self._dict_from_row(row)
            task['task_data'] = json.loads(task['task_data']) if task['task_data'] else {}
            tasks.append(task)
        
        conn.close()
        return tasks
    
    def get_all_users(self):
        """Get all users (for admin dashboard)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.email, u.name, u.created_at,
                   p.age, p.gender, p.phone, p.weight, p.height, p.bmi,
                   p.activity_level, p.goal, p.daily_calories_needed,
                   p.profile_completed
            FROM users u
            LEFT JOIN user_profiles p ON u.id = p.user_id
            ORDER BY u.created_at DESC
        ''')
        
        users = []
        for row in cursor.fetchall():
            user = {
                'id': row[0],
                'email': row[1],
                'name': row[2],
                'created_at': row[3],
                'age': row[4],
                'gender': row[5],
                'phone': row[6],
                'weight': row[7],
                'height': row[8],
                'bmi': row[9],
                'activity_level': row[10],
                'goal': row[11],
                'daily_calories_needed': row[12],
                'has_diet_plan': bool(row[13])
            }
            users.append(user)
        
        conn.close()
        return users
    
    def _dict_from_row(self, row):
        """Convert sqlite3.Row to dictionary"""
        if hasattr(row, 'keys'):
            return dict(zip(row.keys(), row))
        else:
            # For regular tuples, use column names from cursor description
            # This is a fallback for when description is not available
            if hasattr(row, 'description'):
                columns = [desc[0] for desc in row.description]
                return dict(zip(columns, row))
            else:
                # Default column mapping for known tables
                if len(row) >= 8:  # diet_logs table
                    return {
                        'id': row[0], 'user_id': row[1], 'meal_type': row[2],
                        'food_name': row[3], 'serving_size': row[4], 'calories': row[5],
                        'protein': row[6], 'carbs': row[7], 'fats': row[8] if len(row) > 8 else 0,
                        'date': row[9] if len(row) > 9 else None, 'completed_at': row[10] if len(row) > 10 else None
                    }
                elif len(row) >= 6:  # exercise_logs table
                    return {
                        'id': row[0], 'user_id': row[1], 'activity_type': row[2],
                        'duration_minutes': row[3], 'calories_burned': row[4],
                        'date': row[5], 'completed_at': row[6] if len(row) > 6 else None
                    }
                else:
                    # Return as dict with numbered keys
                    return {f'col_{i}': val for i, val in enumerate(row)}

# Initialize database
if __name__ == "__main__":
    db = DietDatabase()
    print("Database setup complete!")
    print(f"Database file: {os.path.abspath(db.db_path)}")
