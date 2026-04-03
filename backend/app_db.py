"""
Database-Enabled Diet Recommendation System
This version replaces in-memory storage with SQLite database
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import hashlib
from datetime import datetime, timedelta
import pytz
from database import DietDatabase
import json

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Initialize database
db = DietDatabase()

# Helper functions
def get_ist_time():
    """Get current time in IST"""
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(user_id):
    """Generate JWT token for user"""
    payload = {
        'user_id': str(user_id),
        'exp': get_ist_time() + timedelta(days=7)
    }
    try:
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        return token
    except Exception as e:
        raise e

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

# Authentication routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user with database"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Authenticate user from database
        auth_result = db.authenticate_user(email, password)
        
        if not auth_result:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        user_id = auth_result['id']
        token = generate_token(user_id)
        
        # Get complete user profile
        profile = auth_result.get('profile', {})
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': profile[0] if profile else user_id,
                'name': profile[1] if profile else auth_result['name'],
                'email': auth_result['email'],
                'age': profile[2] if profile else None,
                'gender': profile[3] if profile else None,
                'phone': profile[4] if profile else None,
                'weight': profile[5] if profile else None,
                'height': profile[6] if profile else None,
                'bmi': profile[7] if profile else None,
                'activity_level': profile[8] if profile else None,
                'goal': profile[9] if profile else None,
                'dietary_notes': profile[10] if profile else None,
                'diet_plan': json.loads(profile[11]) if profile and profile[11] else {},
                'daily_calories_needed': profile[12] if profile else None,
                'profile_completed': bool(profile[5] and profile[6]) if profile else False
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user with database"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'age', 'gender']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create user
        user_id = db.create_user(data['email'], data['password'], data['name'])
        
        if not user_id:
            return jsonify({'error': 'User with this email already exists'}), 400
        
        # Create profile
        profile_data = {
            'name': data['name'],
            'email': data['email'],
            'age': data['age'],
            'gender': data['gender'],
            'phone': data.get('phone', ''),
            'weight': None,
            'height': None,
            'activity_level': 'moderate',
            'goal': 'maintenance',
            'dietary_notes': '',
            'diet_plan': {}
        }
        
        db.update_user_profile(user_id, profile_data)
        
        # Generate token
        token = generate_token(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'token': token,
            'user': {
                'id': user_id,
                'name': data['name'],
                'email': data['email']
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/auth/profile', methods=['GET'])
def get_profile():
    """Get user profile from database"""
    try:
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Authorization token required'}), 401
        
        token = token.replace('Bearer ', '')
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get user profile from database
        auth_result = db.authenticate_user(request.headers.get('X-Email', ''), '')
        
        # For now, let's get profile directly
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.email, u.name, u.created_at,
                   p.age, p.gender, p.phone, p.weight, p.height, p.bmi,
                   p.bmi_category, p.activity_level, p.goal, p.dietary_notes,
                   p.diet_plan, p.daily_calories_needed, p.profile_completed
            FROM users u
            LEFT JOIN user_profiles p ON u.id = p.user_id
            WHERE u.id = ?
        ''', (int(user_id),))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'error': 'User profile not found'}), 404
        
        profile = {
            'id': result[0],
            'email': result[1],
            'name': result[2],
            'age': result[4],
            'gender': result[5],
            'phone': result[6],
            'weight': result[7],
            'height': result[8],
            'bmi': result[9],
            'bmi_category': result[10],
            'activity_level': result[11],
            'goal': result[12],
            'dietary_notes': result[13],
            'diet_plan': json.loads(result[14]) if result[14] else {},
            'daily_calories_needed': result[15],
            'profile_completed': bool(result[16])
        }
        
        # Get recent exercise
        recent_exercise = db.get_recent_exercises(int(user_id), 7)
        
        # Format recent exercise for frontend
        formatted_exercise = []
        for exercise in recent_exercise:
            formatted_exercise.append({
                'id': exercise['id'],
                'activity_type': exercise['activity_type'],
                'duration_minutes': exercise['duration_minutes'],
                'calories_burned': exercise['calories_burned'],
                'date': exercise['date'],
                'completed_at': exercise['completed_at']
            })
        
        # Get today's water intake
        today = get_ist_time().date().isoformat()
        water_data = db.get_water_for_date(int(user_id), today)
        
        # Get today's meals
        today_meals = db.get_meals_for_date(int(user_id), today)
        
        # Format meals for frontend with IDs
        formatted_meals = []
        for meal in today_meals:
            formatted_meals.append({
                'id': meal['id'],
                'meal_type': meal['meal_type'],
                'food_name': meal['food_name'],
                'serving_size': meal['serving_size'],
                'calories': meal['calories'],
                'protein': meal['protein'],
                'carbs': meal['carbs'],
                'fats': meal['fats'],
                'date': meal['date'],
                'completed_at': meal['completed_at']
            })
        
        return jsonify({
            'success': True,
            'user': profile,
            'profile': profile,
            'recent_exercise': formatted_exercise,
            'water_today_ml': water_data['ml'],
            'water_goal_ml': 2000,  # Default goal
            'meals': formatted_meals
        })
        
    except Exception as e:
        return jsonify({'error': f'Profile fetch failed: {str(e)}'}), 500

# Food nutrition endpoint
@app.route('/api/foods/nutrition', methods=['GET'])
def get_food_nutrition():
    """Get nutrition information for a food"""
    try:
        food_name = request.args.get('food', '').lower().strip()
        serving_size = request.args.get('serving', 100, type=int)
        
        if not food_name:
            return jsonify({'error': 'Food name is required'}), 400
        
        # Food database with nutrition per 100g
        food_database = {
            'rice': {'calories': 130, 'protein': 2.7, 'carbs': 28, 'fats': 0.3},
            'chapati': {'calories': 104, 'protein': 3.0, 'carbs': 18.0, 'fats': 1.5},
            'dal': {'calories': 116, 'protein': 8.0, 'carbs': 20.0, 'fats': 0.5},
            'samosa': {'calories': 262, 'protein': 4.0, 'carbs': 24.0, 'fats': 16.0},
            'paneer tikka': {'calories': 265, 'protein': 18.0, 'carbs': 8.0, 'fats': 20.0},
            'butter chicken': {'calories': 238, 'protein': 27.0, 'carbs': 3.0, 'fats': 14.0},
            'idli': {'calories': 112, 'protein': 4.0, 'carbs': 18.0, 'fats': 3.0},
            'dosa': {'calories': 133, 'protein': 2.6, 'carbs': 25.0, 'fats': 2.7},
            'sambhar': {'calories': 87, 'protein': 2.5, 'carbs': 13.0, 'fats': 3.0},
            'chicken breast': {'calories': 165, 'protein': 31.0, 'carbs': 0.0, 'fats': 3.6},
            'egg': {'calories': 155, 'protein': 13.0, 'carbs': 1.1, 'fats': 11.0},
            'banana': {'calories': 89, 'protein': 1.1, 'carbs': 23.0, 'fats': 0.3},
            'apple': {'calories': 52, 'protein': 0.3, 'carbs': 14.0, 'fats': 0.2},
            'milk': {'calories': 42, 'protein': 3.4, 'carbs': 5.0, 'fats': 1.0},
            'bread': {'calories': 265, 'protein': 9.0, 'carbs': 49.0, 'fats': 3.2},
            'yogurt': {'calories': 59, 'protein': 10.0, 'carbs': 3.6, 'fats': 0.4},
            'aloo paratha': {'calories': 208, 'protein': 3.0, 'carbs': 32.0, 'fats': 8.0},
            'rajma': {'calories': 140, 'protein': 9.0, 'carbs': 20.0, 'fats': 4.0},
            'vegetable curry': {'calories': 95, 'protein': 3.0, 'carbs': 12.0, 'fats': 4.0},
            'salad': {'calories': 17, 'protein': 1.4, 'carbs': 3.0, 'fats': 0.2},
            'orange': {'calories': 47, 'protein': 0.9, 'carbs': 12.0, 'fats': 0.1},
            'tea': {'calories': 2, 'protein': 0.0, 'carbs': 0.5, 'fats': 0.0},
            'coffee': {'calories': 1, 'protein': 0.1, 'carbs': 0.0, 'fats': 0.0}
        }
        
        # Find the food in database
        nutrition = food_database.get(food_name)
        
        if not nutrition:
            # Return default values for unknown foods
            nutrition = {'calories': 100, 'protein': 2.0, 'carbs': 20.0, 'fats': 1.0}
        
        # Scale nutrition based on serving size
        scaled_nutrition = {
            'calories': round(nutrition['calories'] * serving_size / 100),
            'protein': round(nutrition['protein'] * serving_size / 100, 1),
            'carbs': round(nutrition['carbs'] * serving_size / 100, 1),
            'fats': round(nutrition['fats'] * serving_size / 100, 1)
        }
        
        return jsonify({
            'success': True,
            'food': food_name,
            'serving_size': serving_size,
            'nutrition': scaled_nutrition
        })
        
    except Exception as e:
        return jsonify({'error': f'Nutrition lookup failed: {str(e)}'}), 500

# Food search endpoint
@app.route('/api/foods/search', methods=['GET'])
def search_foods():
    """Search for foods in the database"""
    try:
        query = request.args.get('q', '').lower().strip()
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        food_database = [
            'rice', 'chapati', 'dal', 'samosa', 'paneer tikka', 'butter chicken',
            'idli', 'dosa', 'sambhar', 'chicken breast', 'egg', 'banana', 'apple',
            'milk', 'bread', 'yogurt', 'aloo paratha', 'rajma', 'vegetable curry',
            'salad', 'orange', 'tea', 'coffee'
        ]
        
        # Find foods that match the query
        suggestions = [food for food in food_database if query in food]
        
        return jsonify({
            'success': True,
            'query': query,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return jsonify({'error': f'Food search failed: {str(e)}'}), 500

# Diet logging routes
@app.route('/api/diet-log', methods=['GET', 'POST'])
def diet_log():
    """Handle diet logging with database"""
    try:
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Authorization token required'}), 401
        
        token = token.replace('Bearer ', '')
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        if request.method == 'GET':
            # Get meals for date
            date = request.args.get('date', get_ist_time().date().isoformat())
            meals = db.get_meals_for_date(int(user_id), date)
            
            # Format meals with IDs
            formatted_meals = []
            for meal in meals:
                formatted_meals.append({
                    'id': meal['id'],
                    'meal_type': meal['meal_type'],
                    'food_name': meal['food_name'],
                    'serving_size': meal['serving_size'],
                    'calories': meal['calories'],
                    'protein': meal['protein'],
                    'carbs': meal['carbs'],
                    'fats': meal['fats'],
                    'date': meal['date'],
                    'completed_at': meal['completed_at']
                })
            
            return jsonify({
                'success': True,
                'meals': formatted_meals,
                'date': date
            })
        
        elif request.method == 'POST':
            # Log new meal
            data = request.get_json()
            
            meal_data = {
                'meal_type': data['meal_type'],
                'food_name': data['food_name'],
                'serving_size': data.get('serving_size', ''),
                'calories': data.get('calories', 0),
                'protein': data.get('protein', 0),
                'carbs': data.get('carbs', 0),
                'fats': data.get('fats', 0),
                'date': data.get('date', get_ist_time().date().isoformat())
            }
            
            db.log_meal(int(user_id), meal_data)
            
            return jsonify({
                'success': True,
                'message': 'Meal logged successfully'
            })
            
    except Exception as e:
        return jsonify({'error': f'Diet log error: {str(e)}'}), 500

@app.route('/api/diet-log/<int:meal_id>', methods=['DELETE'])
def delete_meal(meal_id):
    """Delete a specific meal"""
    try:
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Authorization token required'}), 401
        
        token = token.replace('Bearer ', '')
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Delete the meal from database
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM diet_logs WHERE id = ? AND user_id = ?', (meal_id, int(user_id)))
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return jsonify({
                'success': True,
                'message': 'Meal deleted successfully'
            })
        else:
            conn.close()
            return jsonify({'error': 'Meal not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Delete meal error: {str(e)}'}), 500

# Exercise routes
@app.route('/api/exercise', methods=['GET', 'POST'])
def exercise():
    """Handle exercise logging with database"""
    try:
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Authorization token required'}), 401
        
        token = token.replace('Bearer ', '')
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        if request.method == 'GET':
            # Get exercise tasks (simplified for now)
            return jsonify({
                'success': True,
                'exercise_tasks': [
                    {
                        'id': 'exercise_0',
                        'name': 'Walking',
                        'duration': '30 min',
                        'calories': 150,
                        'completed': False
                    },
                    {
                        'id': 'exercise_1',
                        'name': 'Push-ups',
                        'duration': '15 min',
                        'calories': 100,
                        'completed': False
                    }
                ]
            })
        
        elif request.method == 'POST':
            # Complete exercise
            data = request.get_json()
            task_id = data.get('task_id')
            
            # For now, create a simple exercise log
            exercise_data = {
                'activity_type': 'Exercise',
                'duration_minutes': 30,
                'calories_burned': 200,
                'date': get_ist_time().date().isoformat()
            }
            
            db.log_exercise(int(user_id), exercise_data)
            
            return jsonify({
                'success': True,
                'message': 'Exercise logged successfully'
            })
            
    except Exception as e:
        return jsonify({'error': f'Exercise error: {str(e)}'}), 500

# Water routes
@app.route('/api/water', methods=['GET', 'POST'])
def water():
    """Handle water logging with database"""
    try:
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Authorization token required'}), 401
        
        token = token.replace('Bearer ', '')
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        if request.method == 'GET':
            # Get water data for today
            today = get_ist_time().date().isoformat()
            water_data = db.get_water_for_date(int(user_id), today)
            
            return jsonify({
                'success': True,
                'water_today_ml': water_data['ml'],
                'water_goal_ml': 2000,
                'glasses_today': water_data['glasses']
            })
        
        elif request.method == 'POST':
            # Log water intake
            data = request.get_json()
            
            water_data = {
                'glasses': data.get('glasses', 1),
                'ml': data.get('glasses', 1) * 250,  # 250ml per glass
                'date': get_ist_time().date().isoformat()
            }
            
            db.log_water(int(user_id), water_data)
            
            return jsonify({
                'success': True,
                'message': 'Water intake logged successfully'
            })
            
    except Exception as e:
        return jsonify({'error': f'Water error: {str(e)}'}), 500

# Admin routes
@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    """Get all users for admin dashboard"""
    try:
        # This should require admin authentication
        users = db.get_all_users()
        
        return jsonify({
            'success': True,
            'users': users,
            'total_count': len(users)
        })
        
    except Exception as e:
        return jsonify({'error': f'Admin users error: {str(e)}'}), 500

# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Database-Enabled Diet API is running',
        'database': 'SQLite',
        'timestamp': get_ist_time().isoformat()
    })

# Root endpoint
@app.route('/')
def home():
    """Home page with API information"""
    return jsonify({
        'message': 'Diet Recommendation System API (Database-Enabled)',
        'version': '2.0.0',
        'status': 'running',
        'database': 'SQLite',
        'features': [
            'Persistent data storage',
            'User authentication',
            'Diet logging',
            'Exercise tracking',
            'Water monitoring',
            'Admin dashboard'
        ],
        'endpoints': {
            'auth': {
                'login': 'POST /api/auth/login',
                'register': 'POST /api/auth/register',
                'profile': 'GET /api/auth/profile'
            },
            'features': {
                'diet_log': 'GET/POST /api/diet-log',
                'exercise': 'GET/POST /api/exercise',
                'water': 'GET/POST /api/water'
            },
            'admin': {
                'users': 'GET /api/admin/users'
            }
        },
        'frontend_url': 'http://localhost:3000',
        'health_check': '/api/health'
    })

if __name__ == '__main__':
    print("Starting Database-Enabled Diet Recommendation System...")
    print("Database: SQLite")
    print("Backend will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
