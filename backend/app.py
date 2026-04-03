from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import random
import csv
import requests
from datetime import datetime, timedelta
import hashlib
import jwt
import pytz
import os

# Inline food database to avoid import issues
FOOD_DATABASE = {
    'rice': {'calories': 130, 'protein': 2.7, 'carbs': 28, 'fats': 0.3},
    'chapati': {'calories': 104, 'protein': 3.0, 'carbs': 18.0, 'fats': 1.5},
    'dal': {'calories': 116, 'protein': 8.0, 'carbs': 20.0, 'fats': 0.5},
    'samosa': {'calories': 262, 'protein': 4.0, 'carbs': 24.0, 'fats': 16.0},
    'paneer tikka': {'calories': 265, 'protein': 18.0, 'carbs': 8.0, 'fats': 20.0},
    'butter chicken': {'calories': 238, 'protein': 27.0, 'carbs': 3.0, 'fats': 14.0},
    'idli': {'calories': 112, 'protein': 4.0, 'carbs': 18.0, 'fats': 3.0},
    'tea': {'calories': 2, 'protein': 0.0, 'carbs': 0.5, 'fats': 0.0},
    'coffee': {'calories': 1, 'protein': 0.1, 'carbs': 0.0, 'fats': 0.0}
}

# Set timezone to Indian Standard Time
IST = pytz.timezone('Asia/Kolkata')

def get_ist_time():
    """Get current time in Indian Standard Time"""
    return datetime.now(IST)

app = Flask(__name__)
CORS(app)

# Secret key for JWT
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# In-memory user storage (in production, use a database)
users = {}
user_profiles = {}  # Store detailed user information
user_daily_tasks = {}  # Store tasks per user
user_logs = {}  # Store logs per user

# Helper functions for authentication
def generate_token(user_id):
    """Generate JWT token for user"""
    payload = {
        'user_id': str(user_id),  # Ensure user_id is string
        'exp': get_ist_time() + timedelta(days=7)  # Token expires in 7 days
    }
    try:
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        print(f"DEBUG: JWT encode successful, payload: {payload}")
        return token
    except Exception as e:
        print(f"DEBUG: JWT encode error: {str(e)}")
        raise e

def verify_token(token):
    """Verify JWT token and return user_id"""
    try:
        print(f"DEBUG: Verifying token: {token}")
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        print(f"DEBUG: Token payload: {payload}")
        return payload['user_id']
    except Exception as e:
        print(f"DEBUG: Token verification failed: {str(e)}")
        return None

def hash_password(password):
    """Hash password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'age', 'gender']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        if data['email'] in users:
            return jsonify({'error': 'User with this email already exists'}), 400
        
        # Create user
        user_id = str(len(users) + 1)
        hashed_password = hash_password(data['password'])
        
        # Store user basic info
        users[data['email']] = {
            'id': user_id,
            'email': data['email'],
            'password': hashed_password,
            'name': data['name']
        }
        
        # Store detailed user profile
        user_profiles[user_id] = {
            'id': user_id,
            'name': data['name'],
            'email': data['email'],
            'age': data['age'],
            'gender': data['gender'],
            'phone': data.get('phone', ''),
            'weight': data.get('weight'),  # Optional - will be set in diet plan
            'height': data.get('height'),  # Optional - will be set in diet plan
            'activity_level': data.get('activity_level', 'moderate'),
            'goal': data.get('goal', 'maintenance'),
            'diet_plan': {},
            'created_at': get_ist_time().isoformat(),
            'updated_at': get_ist_time().isoformat(),
            'allergies': data.get('allergies', ''),
            'dietary_preferences': data.get('dietary_preferences', ''),
            'diseases': data.get('diseases', ''),
            'medical_conditions': data.get('medical_conditions', ''),
            'role': 'admin' if data.get('email', '').endswith('@admin.com') else 'user'  # Admin role for debug users
        }
        
        # Initialize user data storage
        user_daily_tasks[user_id] = {}
        user_logs[user_id] = {
            'diet_logs': [],
            'water_logs': [],
            'exercise_logs': [],
            'daily_compliance_calendar': {}
        }
        
        # Generate token
        token = generate_token(user_id)
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': user_id,
                'name': data['name'],
                'email': data['email']
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Check if user exists (case-insensitive)
        user_email_key = None
        for stored_email in users.keys():
            if stored_email.strip().lower() == email:
                user_email_key = stored_email
                break
        
        if not user_email_key:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        user = users.get(user_email_key)
        hashed_password = hash_password(password)
        
        # Verify password
        if not isinstance(user, dict):
            return jsonify({'error': 'Invalid user data structure'}), 401
        
        stored_password = user.get('password')
        
        # Compare passwords
        if hashed_password != stored_password:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate token
        # Get user profile to get user_id
        user_profile = None
        for profile_id, profile in user_profiles.items():
            if profile.get('email') == email:
                user_profile = profile
                break
        
        if not user_profile:
            return jsonify({'error': 'User profile not found'}), 404
        
        user_id = user_profile.get('id')
        if not user_id:
            return jsonify({'error': 'User ID not found'}), 404
        
        token = generate_token(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user_profile.get('id'),
                'name': user_profile.get('name'),
                'email': user_profile.get('email'),
                'age': user_profile.get('age'),
                'gender': user_profile.get('gender'),
                'phone': user_profile.get('phone'),
                'weight': user_profile.get('weight'),
                'height': user_profile.get('height'),
                'activity_level': user_profile.get('activity_level'),
                'goal': user_profile.get('goal'),
                'dietary_notes': user_profile.get('dietary_notes'),
                'diet_plan': user_profile.get('diet_plan'),
                'profile_completed': user_profile.get('weight') and user_profile.get('height')
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/auth/profile', methods=['GET'])
def get_profile():
    """Get user profile and dashboard data (protected)"""
    try:
        # Get token from header
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Authorization token required'}), 401
        
        token = token.replace('Bearer ', '')
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get user profile
        if user_id not in user_profiles:
            return jsonify({'error': 'User profile not found'}), 404
        
        profile = user_profiles[user_id]
        
        # Get today's date in IST
        today = get_ist_time().date().isoformat()
        
        # Calculate water data only if user has diet plan
        water_today_ml = 0
        water_goal_ml = 0
        
        # Only generate tasks if user has diet plan
        if user_id in user_profiles and user_profiles[user_id].get('weight') and user_profiles[user_id].get('height'):
            # Get or create user-specific daily tasks
            if user_id not in user_daily_tasks:
                user_daily_tasks[user_id] = {}
            if today not in user_daily_tasks[user_id]:
                user_daily_tasks[user_id][today] = generate_daily_predefined_tasks(get_ist_time().date(), user_id)
            
            # Calculate water data
            water_tasks = user_daily_tasks[user_id][today]['water_tasks']
            water_completed = sum(1 for task in water_tasks if task['completed'])
            water_total = len(water_tasks)
            water_today_ml = water_completed * 250  # 250ml per glass
            water_goal_ml = water_total * 250
        
        # Get recent exercise from user daily tasks
        recent_exercise = []
        if user_id in user_daily_tasks:
            # Get completed exercises from today and recent days
            today = get_ist_time().date()
            recent_exercise_data = []
            
            # Check last 7 days
            for i in range(7):
                check_date = (today - timedelta(days=i)).isoformat()
                if check_date in user_daily_tasks[user_id]:
                    exercise_tasks = user_daily_tasks[user_id][check_date].get('exercise_tasks', [])
                    for task in exercise_tasks:
                        if task.get('completed'):
                            recent_exercise_data.append({
                                'id': task.get('id', f"ex_{i}_{len(recent_exercise_data)}"),
                                'activity_type': task.get('name', 'Exercise'),
                                'duration_minutes': int(str(task.get('duration', '30')).split()[0]),
                                'calories_burned': task.get('calories', 200),
                                'date': check_date,
                                'completed_at': task.get('completed_at')
                            })
            
            # Sort by most recent and take top 5
            recent_exercise_data.sort(key=lambda x: x.get('completed_at', ''), reverse=True)
            recent_exercise = recent_exercise_data[:5]
        
        # Get diet plan if available
        diet_plan = profile.get('diet_plan', {})
        
        # Only return profile data if user has filled out diet plan (has weight and height)
        has_diet_plan = profile.get('weight') and profile.get('height')
        
        if not has_diet_plan:
            # User hasn't filled diet plan yet - return minimal data
            return jsonify({
                'success': True,
                'user': {
                    'id': user_id,
                    'name': profile['name'],
                    'email': profile['email']
                },
                'profile': {
                    'weight': None,
                    'height': None,
                    'bmi': None,
                    'bmi_category': None,
                    'activity_level': None,
                    'goal': None,
                    'daily_calories_needed': None,
                    'dietary_notes': None
                },
                'water_today_ml': 0,
                'water_goal_ml': 0,
                'recent_exercise': []
            })
        
        # User has diet plan - calculate and return actual data
        # Calculate BMI
        bmi = None
        if profile.get('height') and profile.get('weight'):
            height_m = profile['height'] / 100  # Convert cm to m
            bmi = round(profile['weight'] / (height_m * height_m), 1)
        
        # Calculate daily calories needed from diet plan
        daily_calories = None
        if diet_plan and 'diet_plan_info' in diet_plan:
            daily_calories = diet_plan['diet_plan_info'].get('daily_calorie_needs')
        
        return jsonify({
            'success': True,
            'user': {
                'id': user_id,
                'name': profile['name'],
                'email': profile['email']
            },
            'profile': {
                'weight': profile.get('weight'),
                'height': profile.get('height'),
                'bmi': bmi,
                'bmi_category': diet_plan.get('diet_plan_info', {}).get('user_metrics', {}).get('bmi_category') if bmi else None,
                'activity_level': profile.get('activity_level'),
                'goal': profile.get('goal'),
                'daily_calories_needed': daily_calories,
                'dietary_notes': diet_plan.get('diet_plan_info', {}).get('recommendations', {}).get('dietary_notes', '')
            },
            'water_today_ml': water_today_ml,
            'water_goal_ml': water_goal_ml,
            'recent_exercise': recent_exercise
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

# Authentication decorator
def require_auth(f):
    """Decorator to require authentication for endpoints"""
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Authorization token required'}), 401
        
        token = token.replace('Bearer ', '')
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user_id to request context
        request.user_id = user_id
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

class SimpleDietRecommender:
    """Optimized diet recommendation system"""
    
    def __init__(self):
        # Pre-computed diet plans for faster access
        self.diet_plans = {
            'underweight': {
                'goal': 'Healthy weight gain',
                'calories': '2500-3000 per day',
                'breakfast': [
                    'Oatmeal with banana, nuts, and honey (600 cal)',
                    'Whole wheat toast with avocado and eggs (550 cal)',
                    'Protein smoothie with fruits and peanut butter (520 cal)',
                    'Greek yogurt parfait with granola and fruits (580 cal)'
                ],
                'lunch': [
                    'Chicken and rice bowl with avocado (750 cal)',
                    'Pasta with creamy sauce and vegetables (700 cal)',
                    'Beef stir-fry with noodles (680 cal)',
                    'Tuna sandwich with chips and fruit (650 cal)'
                ],
                'dinner': [
                    'Salmon with sweet potato and vegetables (800 cal)',
                    'Steak with mashed potatoes and gravy (850 cal)',
                    'Chicken curry with rice (750 cal)',
                    'Pork chops with quinoa and roasted vegetables (780 cal)'
                ],
                'snacks': [
                    'Protein shake with banana and peanut butter (400 cal)',
                    'Trail mix with dried fruits and nuts (350 cal)',
                    'Cheese and crackers with apple (300 cal)',
                    'Whole milk smoothie with fruits (380 cal)'
                ]
            },
            'normal': {
                'goal': 'Maintain healthy weight',
                'calories': '1800-2200 per day',
                'breakfast': [
                    'Oatmeal with berries and almonds (400 cal)',
                    'Greek yogurt with granola and honey (350 cal)',
                    'Whole grain toast with avocado and egg (380 cal)',
                    'Protein smoothie with spinach and fruits (360 cal)'
                ],
                'lunch': [
                    'Grilled chicken salad with mixed greens (450 cal)',
                    'Quinoa bowl with roasted vegetables (420 cal)',
                    'Turkey wrap with hummus and vegetables (400 cal)',
                    'Lentil soup with whole grain bread (380 cal)'
                ],
                'dinner': [
                    'Baked salmon with steamed vegetables (500 cal)',
                    'Grilled chicken with roasted sweet potato (480 cal)',
                    'Vegetable stir-fry with tofu (420 cal)',
                    'Lean beef with brown rice and green beans (520 cal)'
                ],
                'snacks': [
                    'Apple with almond butter (200 cal)',
                    'Mixed nuts and seeds (180 cal)',
                    'Greek yogurt with berries (150 cal)',
                    'Carrot and cucumber sticks with hummus (120 cal)'
                ]
            },
            'overweight': {
                'goal': 'Healthy weight loss',
                'calories': '1200-1500 per day',
                'breakfast': [
                    'Oatmeal with cinnamon and apple slices (250 cal)',
                    'Greek yogurt with fresh berries (180 cal)',
                    'Vegetable omelet with whole wheat toast (220 cal)',
                    'Green smoothie with protein powder (200 cal)'
                ],
                'lunch': [
                    'Large salad with grilled chicken (350 cal)',
                    'Vegetable soup with small bread roll (280 cal)',
                    'Quinoa salad with lemon dressing and vegetables (320 cal)',
                    'Turkey lettuce wraps with vegetables (300 cal)'
                ],
                'dinner': [
                    'Grilled fish with steamed vegetables (350 cal)',
                    'Chicken breast with roasted vegetables (380 cal)',
                    'Large vegetable curry with minimal oil (320 cal)',
                    'Lean protein with large salad (340 cal)'
                ],
                'snacks': [
                    'Fresh fruit salad (80 cal)',
                    'Vegetable sticks with salsa (50 cal)',
                    'Herbal tea with small handful of nuts (100 cal)',
                    'Greek yogurt with cucumber slices (90 cal)'
                ]
            }
        }
        
        # Activity multipliers for calorie calculation
        self.activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'veryActive': 1.9
        }
        
        # Health condition adjustments
        self.health_adjustments = {
            'diabetes': {
                'avoid': ['sugar', 'honey', 'maple syrup', 'white bread', 'white rice'],
                'prefer': ['whole grains', 'lean proteins', 'non-starchy vegetables'],
                'tips': ['Choose complex carbohydrates', 'Monitor blood sugar regularly', 'Eat small frequent meals']
            },
            'hypertension': {
                'avoid': ['salt', 'processed foods', 'canned soups', 'deli meats'],
                'prefer': ['fresh vegetables', 'fruits', 'low-sodium options', 'potassium-rich foods'],
                'tips': ['Reduce sodium intake', 'Eat more potassium-rich foods', 'Avoid processed foods']
            },
            'none': {
                'avoid': [], 'prefer': [], 'tips': ['Maintain balanced diet', 'Stay hydrated', 'Exercise regularly']
            }
        }

    def calculate_bmi(self, weight_kg, height_cm):
        """Fast BMI calculation"""
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        return round(bmi, 1)

    def get_bmi_category(self, bmi):
        """Fast BMI categorization"""
        if bmi < 18.5:
            return 'underweight'
        elif bmi < 25:
            return 'normal'
        else:
            return 'overweight'

    def calculate_daily_calories(self, weight_kg, height_cm, age, gender, activity_level):
        """Fast calorie calculation"""
        if gender.lower() == 'male':
            bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
        
        multiplier = self.activity_multipliers.get(activity_level, 1.2)
        return round(bmr * multiplier, 0)

    def get_diet_recommendation(self, weight_kg, height_cm, age, gender, activity_level, health_conditions='none'):
        """Fast diet recommendation generation"""
        # Calculate metrics
        bmi = self.calculate_bmi(weight_kg, height_cm)
        bmi_category = self.get_bmi_category(bmi)
        daily_calories = self.calculate_daily_calories(weight_kg, height_cm, age, gender, activity_level)
        
        # Get base plan
        base_plan = self.diet_plans.get(bmi_category, self.diet_plans['normal'])
        
        # Select random meals for variety
        recommended_meals = {}
        for meal_type in ['breakfast', 'lunch', 'dinner', 'snacks']:
            available_meals = base_plan.get(meal_type, [])
            if available_meals:
                recommended_meals[meal_type] = random.choice(available_meals)
        
        # Generate health tips
        general_tips = [
            'Drink at least 8 glasses of water per day',
            'Include a variety of colorful vegetables in your diet',
            'Choose whole grains over refined grains',
            'Practice portion control and mindful eating',
            'Get adequate sleep (7-9 hours per night)'
        ]
        
        # Health condition tips
        health_tips = []
        if health_conditions and health_conditions.lower() != 'none':
            conditions = [cond.strip().lower() for cond in health_conditions.split(',')]
            for condition in conditions:
                if condition in self.health_adjustments:
                    health_tips.extend(self.health_adjustments[condition]['tips'])
        
        return {
            'user_metrics': {
                'bmi': bmi,
                'bmi_category': bmi_category.title(),
                'daily_calorie_needs': daily_calories
            },
            'health_metrics': {
                'bmi': bmi,
                'bmi_category': bmi_category.title(),
                'daily_calorie_needs': daily_calories
            },
            'diet_plan_info': {
                'goal': base_plan['goal'],
                'target_calories': base_plan['calories']
            },
            'recommended_meals': recommended_meals,
            'health_tips': (general_tips + health_tips)[:8]
        }

    def _generate_comprehensive_plan(self, weight, height, age, gender, activity_level, health_conditions, diet_recommendation):
        """Generate comprehensive lifestyle plan"""
        bmi = diet_recommendation.get('user_metrics', {}).get('bmi', 0)
        bmi_category = diet_recommendation.get('user_metrics', {}).get('bmi_category', 'normal')
        daily_calories = diet_recommendation.get('user_metrics', {}).get('daily_calorie_needs', 2000)
        
        # Fast exercise plan generation
        exercise_plan = self._get_exercise_plan_fast(activity_level, bmi_category, health_conditions)
        
        # Fast water plan generation
        water_plan = self._get_water_plan_fast(weight, activity_level, health_conditions)
        
        # Fast weekly schedule
        weekly_schedule = self._get_weekly_schedule_fast(diet_recommendation)
        
        # Combine everything
        comprehensive_plan = diet_recommendation.copy()
        comprehensive_plan['exercise_plan'] = exercise_plan
        comprehensive_plan['water_plan'] = water_plan
        comprehensive_plan['weekly_schedule'] = weekly_schedule
        
        # Ensure both response structures are included
        if 'user_metrics' not in comprehensive_plan:
            comprehensive_plan['user_metrics'] = diet_recommendation.get('user_metrics', {})
        if 'health_metrics' not in comprehensive_plan:
            comprehensive_plan['health_metrics'] = diet_recommendation.get('health_metrics', {})
        
        return comprehensive_plan

    def _get_exercise_plan_fast(self, activity_level, bmi_category, health_conditions):
        """Fast exercise plan generation"""
        # Determine goal based on BMI
        goal = 'weight_gain' if bmi_category.lower() == 'underweight' else 'weight_loss' if bmi_category.lower() == 'overweight' else 'maintenance'
        
        base_exercises = {
            'weight_gain': {
                'cardio': [
                    {'name': 'Light Walking', 'minutes': 20, 'sessions_per_week': 5, 'calories_per_session': 80},
                    {'name': 'Swimming', 'minutes': 30, 'sessions_per_week': 3, 'calories_per_session': 200}
                ],
                'strength': [
                    {'name': 'Weight Training', 'minutes': 45, 'sessions_per_week': 4, 'calories_per_session': 250},
                    {'name': 'Deadlifts', 'minutes': 30, 'sessions_per_week': 3, 'calories_per_session': 200}
                ]
            },
            'weight_loss': {
                'cardio': [
                    {'name': 'Brisk Walking', 'minutes': 30, 'sessions_per_week': 5, 'calories_per_session': 150},
                    {'name': 'Jogging', 'minutes': 25, 'sessions_per_week': 3, 'calories_per_session': 250}
                ],
                'strength': [
                    {'name': 'Bodyweight Squats', 'minutes': 20, 'sessions_per_week': 3, 'calories_per_session': 100},
                    {'name': 'Push-ups', 'minutes': 15, 'sessions_per_week': 3, 'calories_per_session': 80}
                ]
            },
            'maintenance': {
                'cardio': [
                    {'name': 'Running', 'minutes': 30, 'sessions_per_week': 3, 'calories_per_session': 300},
                    {'name': 'Jumping Jacks', 'minutes': 15, 'sessions_per_week': 3, 'calories_per_session': 150}
                ],
                'strength': [
                    {'name': 'Planks', 'minutes': 20, 'sessions_per_week': 4, 'calories_per_session': 80},
                    {'name': 'Burpees', 'minutes': 15, 'sessions_per_week': 2, 'calories_per_session': 120}
                ]
            }
        }
        
        exercise_plan = base_exercises.get(goal, base_exercises['maintenance'])
        
        # Adjust for health conditions
        if health_conditions and 'diabetes' in health_conditions.lower():
            for exercise_type in exercise_plan:
                for exercise in exercise_plan[exercise_type]:
                    exercise['minutes'] = int(exercise['minutes'] * 1.2)
                    exercise['calories_per_session'] = int(exercise['calories_per_session'] * 0.8)
        
        return exercise_plan

    def _get_water_plan_fast(self, weight, activity_level, health_conditions):
        """Fast water plan generation"""
        base_water_ml = weight * 35  # 35ml per kg
        
        activity_multipliers = {
            'sedentary': 1.0,
            'light': 1.1,
            'moderate': 1.2,
            'active': 1.3,
            'veryActive': 1.4
        }
        
        multiplier = activity_multipliers.get(activity_level, 1.2)
        recommended_water_ml = int(base_water_ml * multiplier)
        
        # Adjust for health conditions
        if health_conditions and 'diabetes' in health_conditions.lower():
            recommended_water_ml = int(recommended_water_ml * 0.9)
        
        water_glasses = round(recommended_water_ml / 250)
        
        return {
            'recommended_ml': recommended_water_ml,
            'recommended_glasses': water_glasses,
            'schedule': [
                f'7:00 AM - {water_glasses//4} glasses ({(water_glasses//4)*250}ml)',
                f'11:00 AM - {water_glasses//4} glasses ({(water_glasses//4)*250}ml)',
                f'3:00 PM - {water_glasses//4} glasses ({(water_glasses//4)*250}ml)',
                f'7:00 PM - {max(1, water_glasses//4)} glasses ({max(1, water_glasses//4)*250}ml)'
            ]
        }

    def _get_weekly_schedule_fast(self, diet_recommendation):
        """Fast weekly schedule generation"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        schedule = []
        
        for day in days:
            day_plan = {
                'day': day,
                'meals': {
                    'breakfast': diet_recommendation.get('recommended_meals', {}).get('breakfast', 'Healthy breakfast'),
                    'lunch': diet_recommendation.get('recommended_meals', {}).get('lunch', 'Balanced lunch'),
                    'dinner': diet_recommendation.get('recommended_meals', {}).get('dinner', 'Nutritious dinner'),
                    'snacks': diet_recommendation.get('recommended_meals', {}).get('snacks', 'Healthy snacks')
                },
                'exercise': 'Rest day' if day in ['Saturday', 'Sunday'] else 'Exercise day',
                'water_intake': '8 glasses'
            }
            schedule.append(day_plan)
        
        return schedule

# Initialize the system
diet_system = SimpleDietRecommender()

class UserRegistration:
    """Fast user registration system"""
    
    def __init__(self, csv_file='users.csv'):
        self.csv_file = csv_file
        self.ensure_csv_file_exists()
    
    def ensure_csv_file_exists(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['id', 'name', 'email', 'password', 'registration_date'])
    
    def email_exists(self, email):
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    if len(row) >= 3 and row[2].lower() == email.lower():
                        return True
            return False
        except:
            return False
    
    def save_user(self, name, email, password):
        try:
            user_id = datetime.now().strftime('%Y%m%d%H%M%S')
            registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([user_id, name, email, password, registration_date])
            
            return True
        except:
            return False

user_reg = UserRegistration()

@app.route('/')
def home():
    """Home page with API information"""
    return jsonify({
        'message': 'Diet Recommendation System API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'auth': {
                'login': 'POST /api/auth/login',
                'register': 'POST /api/auth/register',
                'profile': 'GET /api/auth/profile'
            },
            'diet': {
                'foods_search': 'GET /api/foods/search',
                'foods_nutrition': 'GET /api/foods/nutrition',
                'diet_log': 'GET/POST /api/diet-log',
                'diet_plan': 'GET/POST /api/diet-plan'
            },
            'exercise': {
                'exercise': 'GET/POST /api/exercise',
                'exercise_tasks': 'GET /api/exercise/tasks'
            },
            'water': {
                'water': 'GET/POST /api/water',
                'water_tasks': 'GET /api/water/tasks'
            },
            'reports': {
                'reports': 'GET /api/reports',
                'analytics': 'GET /api/analytics'
            }
        },
        'frontend_url': 'http://localhost:3000',
        'health_check': '/api/health'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Optimized Diet API is running'})

@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    try:
        data = request.get_json()
        required_fields = ['firstName', 'lastName', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        name = f"{data['firstName'].strip()} {data['lastName'].strip()}"
        email = data['email'].strip()
        password = data['password'].strip()
        
        if not name or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        if user_reg.email_exists(email):
            return jsonify({'error': 'Email already registered'}), 409
        
        if user_reg.save_user(name, email, password):
            access_token = f"token_{datetime.now().strftime('%Y%m%d%H%M%S')}_{email}"
            
            return jsonify({
                'message': 'Registration successful',
                'access_token': access_token,
                'user': {'name': name, 'email': email}
            }), 201
        else:
            return jsonify({'error': 'Registration failed. Please try again.'}), 500
    
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    try:
        data = request.get_json()
        if 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].strip()
        password = data['password'].strip()
        
        if not user_reg.email_exists(email):
            return jsonify({'error': 'User not found'}), 404
        
        access_token = f"token_{datetime.now().strftime('%Y%m%d%H%M%S')}_{email}"
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {'email': email, 'name': 'Registered User'}
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/reports/summary', methods=['GET'])
def reports_summary():
    """Get reports summary endpoint"""
    try:
        # For demo purposes, return mock summary data (in real app, would calculate from database)
        return jsonify({
            'range': 'week',
            'days': 7,
            'water_by_day': {
                '2026-04-01': 1000,
                '2026-04-02': 1500,
                '2026-04-03': 2000,
                '2026-04-04': 1750,
                '2026-04-05': 2250,
                '2026-04-06': 2500,
                '2026-04-07': 500
            },
            'water_total_ml': 11500,
            'exercise_by_day': {
                '2026-04-01': 30,
                '2026-04-02': 45,
                '2026-04-03': 60,
                '2026-04-04': 0,
                '2026-04-05': 30,
                '2026-04-06': 90,
                '2026-04-07': 0
            },
            'exercise_total_minutes': 255,
            'exercise_sessions': 6,
            'exercise_total_calories_burned': 1275,
            'exercise_calories_by_day': {
                '2026-04-01': 150,
                '2026-04-02': 225,
                '2026-04-03': 300,
                '2026-04-04': 0,
                '2026-04-05': 150,
                '2026-04-06': 450,
                '2026-04-07': 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get reports summary: {str(e)}'}), 500

@app.route('/api/bmi-calculator', methods=['POST'])
def calculate_bmi():
    """BMI calculator endpoint"""
    try:
        data = request.get_json()
        
        if 'weight' not in data or 'height' not in data:
            return jsonify({'error': 'Weight and height are required'}), 400
        
        weight = float(data['weight'])
        height = float(data['height'])
        
        if weight <= 0 or height <= 0:
            return jsonify({'error': 'Weight and height must be positive numbers'}), 400
        
        bmi = diet_system.calculate_bmi(weight, height)
        category = diet_system.get_bmi_category(bmi)
        
        return jsonify({
            'bmi': bmi,
            'category': category.title(),
            'description': f'Your BMI is {bmi}, which falls in the {category} category'
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/personalized-plan', methods=['GET'])
def get_personalized_plan():
    """Get personalized plan based on user's diet recommendation"""
    try:
        if not user_diet_plan:
            return jsonify({'error': 'No diet plan found. Please get diet recommendations first.'}), 404
        
        user_metrics = user_diet_plan.get('user_metrics', {})
        bmi = user_metrics.get('bmi', 0)
        bmi_category = user_metrics.get('bmi_category', 'normal')
        daily_calories = user_metrics.get('daily_calorie_needs', 2000)
        
        # Generate personalized exercise plan based on user's metrics
        personalized_exercise = generate_personalized_exercise(bmi, bmi_category, daily_calories)
        
        # Generate personalized water plan based on user's weight
        weight = user_metrics.get('weight', 70)  # Default weight if not available
        personalized_water = generate_personalized_water(weight, bmi_category)
        
        # Generate personalized reports
        personalized_reports = generate_personalized_reports(bmi, bmi_category, daily_calories)
        
        return jsonify({
            'user_metrics': user_metrics,
            'personalized_exercise': personalized_exercise,
            'personalized_water': personalized_water,
            'personalized_reports': personalized_reports
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get personalized plan: {str(e)}'}), 500

def generate_personalized_exercise(bmi, bmi_category, daily_calories):
    """Generate exercise plan based on user's BMI and calorie needs"""
    
    # Determine exercise goals based on BMI category
    if bmi_category.lower() == 'underweight':
        goal = 'weight_gain'
        intensity = 'moderate'
        focus = 'strength_building'
    elif bmi_category.lower() == 'overweight':
        goal = 'weight_loss'
        intensity = 'moderate_to_high'
        focus = 'cardio_focused'
    else:
        goal = 'maintenance'
        intensity = 'moderate'
        focus = 'balanced'
    
    # Calculate exercise calories based on daily needs (aim for 15-20% of daily calories)
    target_exercise_calories = int(daily_calories * 0.15)
    
    exercise_plan = {
        'goal': goal,
        'intensity': intensity,
        'focus': focus,
        'target_weekly_calories': target_exercise_calories * 7,
        'weekly_schedule': []
    }
    
    # Generate specific exercises based on goal
    if goal == 'weight_gain':
        exercises = [
            {'name': 'Weight Training', 'minutes': 45, 'sessions_per_week': 4, 'calories_per_session': 250, 'type': 'strength'},
            {'name': 'Deadlifts', 'minutes': 30, 'sessions_per_week': 3, 'calories_per_session': 200, 'type': 'strength'},
            {'name': 'Pull-ups', 'minutes': 15, 'sessions_per_week': 3, 'calories_per_session': 100, 'type': 'strength'},
            {'name': 'Light Walking', 'minutes': 20, 'sessions_per_week': 5, 'calories_per_session': 80, 'type': 'cardio'}
        ]
    elif goal == 'weight_loss':
        exercises = [
            {'name': 'Brisk Walking', 'minutes': 30, 'sessions_per_week': 5, 'calories_per_session': 150, 'type': 'cardio'},
            {'name': 'Jogging', 'minutes': 25, 'sessions_per_week': 4, 'calories_per_session': 250, 'type': 'cardio'},
            {'name': 'Cycling', 'minutes': 45, 'sessions_per_week': 3, 'calories_per_session': 400, 'type': 'cardio'},
            {'name': 'Bodyweight Squats', 'minutes': 20, 'sessions_per_week': 3, 'calories_per_session': 100, 'type': 'strength'}
        ]
    else:  # maintenance
        exercises = [
            {'name': 'Running', 'minutes': 30, 'sessions_per_week': 3, 'calories_per_session': 300, 'type': 'cardio'},
            {'name': 'Planks', 'minutes': 20, 'sessions_per_week': 4, 'calories_per_session': 80, 'type': 'strength'},
            {'name': 'Jumping Jacks', 'minutes': 15, 'sessions_per_week': 3, 'calories_per_session': 150, 'type': 'cardio'},
            {'name': 'Push-ups', 'minutes': 15, 'sessions_per_week': 3, 'calories_per_session': 80, 'type': 'strength'}
        ]
    
    exercise_plan['recommended_exercises'] = exercises
    return exercise_plan

def generate_personalized_water(weight, bmi_category):
    """Generate water intake plan based on user's weight and BMI"""
    
    # Base water calculation: 35ml per kg of body weight
    base_water_ml = weight * 35
    
    # Adjust for BMI category
    if bmi_category.lower() == 'underweight':
        multiplier = 1.1  # Slightly more for weight gain
    elif bmi_category.lower() == 'overweight':
        multiplier = 1.3  # More for weight loss and metabolism
    else:
        multiplier = 1.2  # Normal maintenance
    
    recommended_water_ml = int(base_water_ml * multiplier)
    water_glasses = round(recommended_water_ml / 250)
    
    # Generate personalized schedule based on typical daily routine
    schedule = [
        {'time': '6:00 AM', 'glasses': 1, 'purpose': 'Morning hydration to kickstart metabolism'},
        {'time': '9:00 AM', 'glasses': 2, 'purpose': 'Pre-meal hydration'},
        {'time': '12:00 PM', 'glasses': 1, 'purpose': 'Lunch time hydration'},
        {'time': '3:00 PM', 'glasses': 1, 'purpose': 'Afternoon energy boost'},
        {'time': '6:00 PM', 'glasses': 1, 'purpose': 'Dinner time hydration'},
        {'time': '9:00 PM', 'glasses': 1, 'purpose': 'Evening hydration before bed'}
    ]
    
    # Adjust schedule to match total glasses
    total_scheduled = sum(s['glasses'] for s in schedule)
    if total_scheduled != water_glasses:
        difference = water_glasses - total_scheduled
        if difference > 0:
            schedule[2]['glasses'] += difference  # Add to lunch time
        elif difference < 0:
            schedule[-1]['glasses'] += difference  # Remove from evening
    
    water_plan = {
        'recommended_ml': recommended_water_ml,
        'recommended_glasses': water_glasses,
        'weight_based': True,
        'bmi_adjusted': True,
        'schedule': schedule,
        'tips': [
            f'Drink {water_glasses} glasses daily based on your {weight}kg weight',
            'Spread intake throughout the day for better absorption',
            'Increase intake during exercise',
            'Monitor urine color as hydration indicator'
        ]
    }
    
    return water_plan

def generate_personalized_reports(bmi, bmi_category, daily_calories):
    """Generate personalized reports based on user's metrics"""
    
    # Calculate personalized targets
    if bmi_category.lower() == 'underweight':
        weekly_weight_goal = '+0.5 kg'
        calorie_adjustment = '+300 cal/day'
        focus_area = 'Muscle Building'
    elif bmi_category.lower() == 'overweight':
        weekly_weight_goal = '-0.5 kg'
        calorie_adjustment = '-500 cal/day'
        focus_area = 'Fat Burning'
    else:
        weekly_weight_goal = 'Maintain'
        calorie_adjustment = '0 cal/day'
        focus_area = 'Fitness Maintenance'
    
    # Generate personalized report structure
    reports = {
        'personalized_targets': {
            'weekly_weight_goal': weekly_weight_goal,
            'daily_calorie_target': daily_calories,
            'calorie_adjustment': calorie_adjustment,
            'focus_area': focus_area
        },
        'tracking_metrics': {
            'weight_tracking': True,
            'calorie_tracking': True,
            'exercise_tracking': True,
            'water_tracking': True,
            'compliance_tracking': True
        },
        'report_frequency': {
            'daily_check_in': True,
            'weekly_summary': True,
            'monthly_analysis': True
        },
        'alerts': {
            'weight_change_alert': True,
            'calorie_deficit_alert': True,
            'hydration_reminder': True,
            'exercise_reminder': True
        }
    }
    
    return reports

# Update the exercise logging to use personalized plan

def check_exercise_compliance(activity_type, duration, calories, exercise_plan):
    """Check if exercise matches personalized plan"""
    
    # Find matching exercise in plan
    matching_exercise = None
    for exercise in exercise_plan.get('recommended_exercises', []):
        if exercise['name'].lower() in activity_type.lower() or activity_type.lower() in exercise['name'].lower():
            matching_exercise = exercise
            break
    
    if not matching_exercise:
        return {
            'matches_plan': False,
            'message': f'This exercise is not in your recommended plan. Consider: {exercise_plan["recommended_exercises"][0]["name"]}',
            'plan_type': exercise_plan.get('goal', 'maintenance')
        }
    
    # Check duration compliance
    recommended_duration = matching_exercise['minutes']
    duration_variance = abs(duration - recommended_duration) / recommended_duration
    
    # Check calorie compliance
    recommended_calories = matching_exercise['calories_per_session']
    calorie_variance = abs(calories - recommended_calories) / recommended_calories if recommended_calories > 0 else 0
    
    # Calculate overall compliance
    duration_score = max(0, 100 - (duration_variance * 100))
    calorie_score = max(0, 100 - (calorie_variance * 100))
    overall_score = (duration_score + calorie_score) / 2
    
    if overall_score >= 80:
        message = f'Perfect! You followed your {exercise_plan["goal"]} plan exactly!'
    elif overall_score >= 60:
        message = f'Good job! Close to your {exercise_plan["goal"]} plan.'
    else:
        message = f'Try to match your {exercise_plan["goal"]} plan better next time.'
    
    return {
        'matches_plan': True,
        'overall_score': round(overall_score, 1),
        'duration_score': round(duration_score, 1),
        'calorie_score': round(calorie_score, 1),
        'message': message,
        'plan_type': exercise_plan.get('goal', 'maintenance'),
        'recommended': matching_exercise
    }

@app.route('/api/water', methods=['POST'])
@require_auth
def log_water():
    """Log water intake - now tick-based from predefined tasks (protected)"""
    try:
        user_id = request.user_id
        data = request.get_json()
        task_id = data.get('task_id')  # ID of the predefined water task
        
        if not task_id:
            return jsonify({'error': 'task_id is required for tick-based water logging'}), 400
        
        # Handle date properly - use today's date if not provided
        date_param = data.get('date')
        if date_param:
            if isinstance(date_param, str):
                target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                date_str = date_param
            else:
                target_date = date_param
                date_str = target_date.isoformat()
        else:
            target_date = datetime.now().date()
            date_str = target_date.isoformat()
        
        # Get or create user-specific daily tasks
        if user_id not in user_daily_tasks:
            user_daily_tasks[user_id] = {}
        if date_str not in user_daily_tasks[user_id]:
            user_daily_tasks[user_id][date_str] = generate_daily_predefined_tasks(target_date, user_id)
        
        # Find and complete the water task
        task_completed = False
        for water_task in user_daily_tasks[user_id][date_str]['water_tasks']:
            if water_task['id'] == task_id and not water_task['completed']:
                water_task['completed'] = True
                water_task['completed_at'] = get_ist_time().isoformat()
                task_completed = True
                break
        
        if not task_completed:
            return jsonify({'error': 'Water task not found or already completed'}), 400
        
        # Calculate compliance
        water_score = calculate_water_compliance_score(date_str, user_id)
        total_score = get_day_compliance_data(date_str, user_id)['overall_score']
        
        # Generate encouragement
        if water_score >= 90:
            encouragement = get_random_encouragement('perfect_water')
            reward_image = get_goal_image('daily_complete', user_id)
        elif water_score >= 75:
            encouragement = get_random_encouragement('good_water')
            reward_image = get_goal_image('daily_complete', user_id)
        else:
            encouragement = f"💧 Keep going! {water_score}% of water tasks completed today!"
            reward_image = ""
        
        # Check for streak bonus
        streak_bonus = check_streak_bonus(target_date, user_id)
        if streak_bonus:
            encouragement += " " + get_random_encouragement('streak_bonus')
            reward_image = get_goal_image('streak_bonus', user_id)
        
        return jsonify({
            'success': True,
            'message': 'Water task completed successfully!',
            'task_id': task_id,
            'water_score': water_score,
            'overall_score': total_score,
            'encouragement': encouragement,
            'reward_image': reward_image,
            'streak_bonus': streak_bonus
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to log water: {str(e)}'}), 500
        data = request.get_json()
        task_id = data.get('task_id')  # ID of the predefined water task
        
        if not task_id:
            return jsonify({'error': 'task_id is required for tick-based water logging'}), 400
        
        # Handle date properly - use today's date if not provided
        date_param = data.get('date')
        if date_param:
            if isinstance(date_param, str):
                target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                date_str = date_param
            else:
                target_date = date_param
                date_str = target_date.isoformat()
        else:
            target_date = datetime.now().date()
            date_str = target_date.isoformat()
        
        # Get or create daily tasks
        if date_str not in daily_tasks:
            daily_tasks[date_str] = generate_daily_predefined_tasks(target_date, None)
        
        # Find and complete the water task
        task_completed = False
        for water_task in daily_tasks[date_str]['water_tasks']:
            if water_task['id'] == task_id and not water_task['completed']:
                water_task['completed'] = True
                water_task['completed_at'] = get_ist_time().isoformat()
                task_completed = True
                break
        
        if not task_completed:
            return jsonify({'error': 'Water task not found or already completed'}), 400
        
        # Calculate compliance
        water_score = calculate_water_compliance_score(date_str, user_id)
        total_score = get_day_compliance_data(date_str, user_id)['overall_score']
        
        # Generate encouragement
        if water_score >= 90:
            encouragement = get_random_encouragement('perfect_water')
            reward_image = get_goal_image('daily_complete')
        elif water_score >= 75:
            encouragement = get_random_encouragement('good_water')
            reward_image = get_goal_image('daily_complete')
        else:
            encouragement = f"💧 Keep going! {water_score}% of water tasks completed today!"
            reward_image = ""
        
        # Check for streak bonus
        streak_bonus = check_streak_bonus(target_date, user_id)
        if streak_bonus:
            encouragement += " " + get_random_encouragement('streak_bonus')
            reward_image = get_goal_image('streak_bonus')
        
        return jsonify({
            'success': True,
            'message': 'Water task completed successfully!',
            'task_id': task_id,
            'water_score': water_score,
            'overall_score': total_score,
            'encouragement': encouragement,
            'reward_image': reward_image,
            'streak_bonus': streak_bonus
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to log water: {str(e)}'}), 500

@app.route('/api/water', methods=['GET'])
@require_auth
def get_water():
    """Get water tasks for a specific date (protected)"""
    try:
        user_id = request.user_id
        date_str = request.args.get('date', datetime.now().date().isoformat())
        
        # Get or create user-specific daily tasks
        if user_id not in user_daily_tasks:
            user_daily_tasks[user_id] = {}
        if date_str not in user_daily_tasks[user_id]:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            user_daily_tasks[user_id][date_str] = generate_daily_predefined_tasks(target_date, user_id)
        
        # Return water tasks
        water_tasks = user_daily_tasks[user_id][date_str]['water_tasks']
        
        # Calculate compliance
        completed_tasks = sum(1 for task in water_tasks if task['completed'])
        total_tasks = len(water_tasks)
        compliance_score = round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0
        
        return jsonify({
            'water_tasks': water_tasks,
            'compliance_score': compliance_score,
            'total_tasks': total_tasks,
            'date': date_str
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get water tasks: {str(e)}'}), 500

@app.route('/api/exercise', methods=['POST'])
@require_auth
def log_exercise():
    """Log exercise - now tick-based from predefined tasks"""
    try:
        user_id = request.user_id
        data = request.get_json()
        task_id = data.get('task_id')  # ID of the predefined exercise task
        
        if not task_id:
            return jsonify({'error': 'task_id is required for tick-based exercise logging'}), 400
        
        # Handle date properly - use today's date if not provided
        date_param = data.get('date')
        if date_param:
            if isinstance(date_param, str):
                target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                date_str = date_param
            else:
                target_date = date_param
                date_str = target_date.isoformat()
        else:
            target_date = get_ist_time().date()
            date_str = target_date.isoformat()
        
        # Get or create user-specific daily tasks
        if user_id not in user_daily_tasks:
            user_daily_tasks[user_id] = {}
        if date_str not in user_daily_tasks[user_id]:
            user_daily_tasks[user_id][date_str] = generate_daily_predefined_tasks(target_date, user_id)
        
        # Find and complete the exercise task
        task_completed = False
        for exercise_task in user_daily_tasks[user_id][date_str]['exercise_tasks']:
            if exercise_task['id'] == task_id and not exercise_task['completed']:
                exercise_task['completed'] = True
                exercise_task['completed_at'] = get_ist_time().isoformat()
                task_completed = True
                break
        
        if not task_completed:
            return jsonify({'error': 'Exercise task not found or already completed'}), 400
        
        # Calculate compliance
        exercise_score = calculate_exercise_compliance_score(date_str, user_id)
        total_score = get_day_compliance_data(date_str, user_id)['overall_score']
        
        # Generate encouragement
        if exercise_score >= 90:
            encouragement = get_random_encouragement('perfect_exercise')
            reward_image = get_goal_image('daily_complete')
        elif exercise_score >= 75:
            encouragement = get_random_encouragement('good_exercise')
            reward_image = get_goal_image('daily_complete')
        else:
            encouragement = f"💪 Keep moving! {exercise_score}% of exercise tasks completed today!"
            reward_image = ""
        
        # Check for streak bonus
        streak_bonus = check_streak_bonus(target_date, user_id)
        if streak_bonus:
            encouragement += " " + get_random_encouragement('streak_bonus')
            reward_image = get_goal_image('streak_bonus')
        
        return jsonify({
            'success': True,
            'message': 'Exercise task completed successfully!',
            'task_id': task_id,
            'exercise_score': exercise_score,
            'overall_score': total_score,
            'encouragement': encouragement,
            'reward_image': reward_image,
            'streak_bonus': streak_bonus
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to log exercise: {str(e)}'}), 500

@app.route('/api/exercise', methods=['GET'])
@require_auth
def get_exercise():
    """Get exercise tasks for a specific date"""
    try:
        user_id = request.user_id
        date_str = request.args.get('date', datetime.now().date().isoformat())
        
        # Get or create user-specific daily tasks
        if user_id not in user_daily_tasks:
            user_daily_tasks[user_id] = {}
        if date_str not in user_daily_tasks[user_id]:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            user_daily_tasks[user_id][date_str] = generate_daily_predefined_tasks(target_date, user_id)
        
        # Return exercise tasks
        exercise_tasks = user_daily_tasks[user_id][date_str]['exercise_tasks']
        
        # Calculate compliance
        completed_tasks = sum(1 for task in exercise_tasks if task['completed'])
        total_tasks = len(exercise_tasks)
        compliance_score = round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0
        
        return jsonify({
            'date': date_str,
            'exercise_tasks': exercise_tasks,
            'completed_tasks': completed_tasks,
            'total_tasks': total_tasks,
            'compliance_score': compliance_score,
            'all_completed': completed_tasks == total_tasks
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get exercise tasks: {str(e)}'}), 500

# Simple in-memory storage for demo (in real app, would use database)
water_logs = []
exercise_logs = []
diet_logs = []
user_diet_plan = {}
daily_compliance_calendar = {}  # New: Calendar for tracking daily compliance
log_id_counter = 1

@app.route('/api/calendar', methods=['GET'])
def get_compliance_calendar():
    """Get monthly compliance calendar with encouragement based on ticked tasks"""
    try:
        # Get current month and year (or from query params)
        now = datetime.now()
        year = int(request.args.get('year', now.year))
        month = int(request.args.get('month', now.month))
        
        # Generate calendar data
        calendar_data = generate_monthly_calendar(year, month)
        
        # Get streak information
        streak_info = calculate_streak_info()
        
        # Generate monthly encouragement message
        summary = calendar_data['summary']
        if summary['perfect_days'] >= 20:
            monthly_encouragement = f" INCREDIBLE MONTH! {summary['perfect_days']} perfect days! You're legendary!"
        elif summary['perfect_days'] >= 15:
            monthly_encouragement = f" AMAZING MONTH! {summary['perfect_days']} perfect days! Outstanding work!"
        elif summary['perfect_days'] >= 10:
            monthly_encouragement = f" GREAT MONTH! {summary['perfect_days']} perfect days! Keep it up!"
        elif summary['perfect_days'] >= 5:
            monthly_encouragement = f" GOOD MONTH! {summary['perfect_days']} perfect days! Solid progress!"
        else:
            monthly_encouragement = f" ROOM TO GROW! Only {summary['perfect_days']} perfect days. Next month will be better!"
        
        return jsonify({
            'calendar': calendar_data,
            'streak_info': streak_info,
            'monthly_encouragement': monthly_encouragement,
            'achievement_level': get_achievement_level(summary['success_rate'])
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get calendar: {str(e)}'}), 500

@app.route('/api/calendar/day', methods=['GET'])
def get_day_compliance():
    """Get detailed compliance for a specific day based on ticked tasks"""
    try:
        date_str = request.args.get('date', datetime.now().date().isoformat())
        
        # Get comprehensive day data
        day_data = get_day_compliance_data(date_str)
        
        # Get improvement tips if needed
        if day_data['overall_score'] < 75:
            improvement_tips = generate_improvement_tips(day_data)
        else:
            improvement_tips = []
        
        # Get completed tasks details
        completed_details = get_completed_tasks_details(date_str)
        
        return jsonify({
            'day_data': day_data,
            'improvement_tips': improvement_tips,
            'completed_tasks': completed_details
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get day compliance: {str(e)}'}), 500

def get_completed_tasks_details(date_str):
    """Get details of completed tasks for a day"""
    if date_str not in daily_tasks:
        return {
            'diet': [],
            'exercise': [],
            'water': []
        }
    
    tasks = daily_tasks[date_str]
    
    return {
        'diet': [
            {
                'id': task['id'],
                'meal_type': task['meal_type'],
                'description': task['description'],
                'completed_at': task['completed_at'],
                'icon': task['icon']
            }
            for task in tasks.get('diet_tasks', []) if task['completed']
        ],
        'exercise': [
            {
                'id': task['id'],
                'name': task['name'],
                'duration': task['duration'],
                'completed_at': task['completed_at'],
                'icon': task['icon']
            }
            for task in tasks.get('exercise_tasks', []) if task['completed']
        ],
        'water': [
            {
                'id': task['id'],
                'time': task['time'],
                'glasses': task['glasses'],
                'description': task['description'],
                'completed_at': task['completed_at'],
                'icon': task['icon']
            }
            for task in tasks.get('water_tasks', []) if task['completed']
        ]
    }

def generate_monthly_calendar(year, month):
    """Generate calendar data for a specific month"""
    import calendar
    
    # Get calendar days for the month
    cal = calendar.monthcalendar(year, month)
    calendar_days = []
    
    for week in cal:
        week_days = []
        for day in week:
            if day == 0:
                week_days.append(None)  # Empty day (outside month)
            else:
                date_obj = datetime(year, month, day).date()
                day_data = get_day_compliance_data(date_obj)
                week_days.append(day_data)
        calendar_days.append(week_days)
    
    return calendar_days

def get_day_compliance_data(date, user_id=None):
    """Get compliance data for a specific date based on ticked tasks"""
    try:
        # Handle both string and date object inputs
        if isinstance(date, str):
            date_str = date
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date_str = date.isoformat()
            target_date = date
        
        # Get user-specific or global tasks
        if user_id and user_id in user_daily_tasks and date_str in user_daily_tasks[user_id]:
            tasks = user_daily_tasks[user_id][date_str]
        else:
            if date_str not in daily_tasks:
                return {
                    'date': date_str,
                    'overall_score': 0,
                    'diet_score': 0,
                    'exercise_score': 0,
                    'water_score': 0,
                    'total_tasks': 0,
                    'completed_tasks': 0
                }
            tasks = daily_tasks[date_str]
        
        # Calculate compliance scores based on ticked tasks
        diet_score = calculate_diet_compliance_score(date_str, user_id)
        water_score = calculate_water_compliance_score(date_str, user_id)
        exercise_score = calculate_exercise_compliance_score(date_str, user_id)
        
        # Calculate overall score
        overall_score = round((diet_score + water_score + exercise_score) / 3, 1)
        
        # Get achievement level
        achievement_level = get_achievement_level(overall_score)
        
        # Generate daily encouragement
        encouragement = generate_daily_encouragement(overall_score, achievement_level, diet_score, water_score, exercise_score)
        
        # Get specific area praise
        area_praise = []
        if diet_score >= 90:
            area_praise.append("🍽️ Perfect diet compliance!")
        elif diet_score >= 75:
            area_praise.append("🍽️ Great diet work!")
        elif diet_score >= 50:
            area_praise.append("🍽️ Good diet progress!")
        
        if water_score >= 90:
            area_praise.append("💧 Great hydration!")
        elif water_score >= 75:
            area_praise.append("💧 Good hydration!")
        elif water_score >= 50:
            area_praise.append("💧 Decent water intake!")
        
        if exercise_score >= 90:
            area_praise.append("🏃 Excellent workout!")
        elif exercise_score >= 75:
            area_praise.append("🏃 Great exercise!")
        elif exercise_score >= 50:
            area_praise.append("🏃 Good activity!")
        
        return {
            'date': date_str,
            'diet_score': diet_score,
            'water_score': water_score,
            'exercise_score': exercise_score,
            'overall_score': overall_score,
            'achievement_level': achievement_level,
            'encouragement': encouragement,
            'area_praise': area_praise,
            'completed_tasks': get_completed_tasks_count(date_str),
            'total_tasks': get_total_tasks_count(date_str),
            'is_perfect_day': overall_score >= 90
        }
        
    except Exception as e:
        # Return default data if there's an error
        date_str = date.isoformat() if hasattr(date, 'isoformat') else str(date)
        return {
            'date': date_str,
            'diet_score': 0,
            'water_score': 0,
            'exercise_score': 0,
            'overall_score': 0,
            'achievement_level': 'needs_work',
            'encouragement': '🎯 Tomorrow\'s a New Day! Every day is a fresh start!',
            'area_praise': [],
            'completed_tasks': 0,
            'total_tasks': 0,
            'is_perfect_day': False
        }
    # Store in calendar
    daily_compliance_calendar[date_str] = day_data
    
    return day_data

def calculate_diet_compliance_score(date_str, user_id=None):
    """Calculate diet compliance score based on ticked tasks"""
    if user_id and user_id in user_daily_tasks and date_str in user_daily_tasks[user_id]:
        tasks = user_daily_tasks[user_id][date_str].get('diet_tasks', [])
    else:
        if date_str not in daily_tasks:
            return 0
        tasks = daily_tasks[date_str].get('diet_tasks', [])
    
    if not tasks:
        return 0
    
    # Count completed diet tasks
    completed_tasks = sum(1 for task in tasks if task['completed'])
    total_tasks = len(tasks)
    
    return round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0

def calculate_water_compliance_score(date_str, user_id=None):
    """Calculate water compliance score based on ticked tasks"""
    if user_id and user_id in user_daily_tasks and date_str in user_daily_tasks[user_id]:
        tasks = user_daily_tasks[user_id][date_str].get('water_tasks', [])
    else:
        if date_str not in daily_tasks:
            return 0
        tasks = daily_tasks[date_str].get('water_tasks', [])
    
    if not tasks:
        return 0
    
    # Count completed water tasks
    completed_tasks = sum(1 for task in tasks if task['completed'])
    total_tasks = len(tasks)
    
    return round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0

def calculate_exercise_compliance_score(date_str, user_id=None):
    """Calculate exercise compliance score based on ticked tasks"""
    if user_id and user_id in user_daily_tasks and date_str in user_daily_tasks[user_id]:
        tasks = user_daily_tasks[user_id][date_str]
    else:
        if date_str not in daily_tasks:
            return 0
        tasks = daily_tasks[date_str]
    exercise_tasks = tasks.get('exercise_tasks', [])
    
    if not exercise_tasks:
        return 0
    
    # Count completed exercise tasks
    completed_tasks = sum(1 for task in exercise_tasks if task['completed'])
    total_tasks = len(exercise_tasks)
    
    return round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0

def get_completed_tasks_count(date_str):
    """Get total completed tasks for a day"""
    if date_str not in daily_tasks:
        return 0
    
    tasks = daily_tasks[date_str]
    completed = 0
    
    # Count completed diet tasks
    completed += sum(1 for task in tasks.get('diet_tasks', []) if task['completed'])
    
    # Count completed exercise tasks
    completed += sum(1 for task in tasks.get('exercise_tasks', []) if task['completed'])
    
    # Count completed water tasks
    completed += sum(1 for task in tasks.get('water_tasks', []) if task['completed'])
    
    return completed

def get_total_tasks_count(date_str):
    """Get total tasks for a day"""
    if date_str not in daily_tasks:
        return 0
    
    tasks = daily_tasks[date_str]
    total = 0
    
    total += len(tasks.get('diet_tasks', []))
    total += len(tasks.get('exercise_tasks', []))
    total += len(tasks.get('water_tasks', []))
    
    return total

def generate_monthly_calendar(year, month):
    """Generate monthly calendar with compliance data based on ticked tasks"""
    import calendar
    
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    calendar_data = {
        'year': year,
        'month': month,
        'month_name': month_name,
        'weeks': [],
        'summary': {}
    }
    
    total_days = 0
    perfect_days = 0
    excellent_days = 0
    good_days = 0
    
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)
            else:
                date_str = f"{year:04d}-{month:02d}-{day:02d}"
                day_data = get_day_compliance_data(date_str)
                week_data.append(day_data)
                
                total_days += 1
                if day_data['overall_score'] >= 90:
                    perfect_days += 1
                    excellent_days += 1
                    good_days += 1
                elif day_data['overall_score'] >= 75:
                    excellent_days += 1
                    good_days += 1
                elif day_data['overall_score'] >= 50:
                    good_days += 1
        
        calendar_data['weeks'].append(week_data)
    
    # Calculate monthly summary
    calendar_data['summary'] = {
        'total_days': total_days,
        'perfect_days': perfect_days,
        'excellent_days': excellent_days,
        'good_days': good_days,
        'success_rate': round((good_days / total_days) * 100, 1) if total_days > 0 else 0,
        'excellence_rate': round((excellent_days / total_days) * 100, 1) if total_days > 0 else 0,
        'perfection_rate': round((perfect_days / total_days) * 100, 1) if total_days > 0 else 0
    }
    
    return calendar_data

def calculate_streak_info():
    """Calculate current and longest streak based on ticked tasks"""
    if not daily_tasks:
        return {'current_streak': 0, 'longest_streak': 0}
    
    # Get all dates with tasks
    dates_with_tasks = sorted(daily_tasks.keys())
    
    if not dates_with_tasks:
        return {'current_streak': 0, 'longest_streak': 0}
    
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    
    # Check dates in order
    for i, date_str in enumerate(dates_with_tasks):
        day_data = get_day_compliance_data(date_str)
        
        if day_data['overall_score'] >= 75:  # Good day threshold
            temp_streak += 1
            if i == len(dates_with_tasks) - 1:  # Last date
                current_streak = temp_streak
        else:
            # Check if next day is consecutive
            next_date = datetime.strptime(dates_with_tasks[i + 1], '%Y-%m-%d').date()
            current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            if (next_date - current_date).days == 1:
                # Consecutive good day
                pass
            else:
                # Break in streak
                current_streak = temp_streak
                temp_streak = 0
        
        longest_streak = max(longest_streak, temp_streak)
    
    return {
        'current_streak': current_streak,
        'longest_streak': longest_streak
    }

def get_detailed_day_compliance(date):
    """Get detailed compliance data for a specific day"""
    day_data = get_day_compliance_data(date)
    
    # Add more detailed information
    detailed_data = day_data.copy()
    
    # Get specific logs for this day
    detailed_data['diet_logs'] = [log for log in diet_logs if log.get('date') == date.isoformat()]
    detailed_data['water_logs'] = [log for log in water_logs 
                                  if datetime.fromisoformat(log['logged_at'].replace('Z', '+00:00')).date() == date]
    detailed_data['exercise_logs'] = [log for log in exercise_logs 
                                    if datetime.fromisoformat(log['logged_at'].replace('Z', '+00:00')).date() == date]
    
    # Add recommendations for improvement
    if day_data['overall_compliance'] < 50:
        detailed_data['improvement_tips'] = generate_improvement_tips(day_data)
    
    return detailed_data

def generate_improvement_tips(day_data):
    """Generate personalized improvement tips"""
    tips = []
    
    if day_data['diet_compliance'] < 50:
        tips.append("🍽️ Try to follow your recommended meals more closely")
        tips.append("📝 Plan your meals in advance to stay on track")
    
    if day_data['water_compliance'] < 50:
        tips.append("💧 Set reminders to drink water throughout the day")
        tips.append("🚰 Keep a water bottle nearby as a visual reminder")
    
    if day_data['exercise_compliance'] < 50:
        tips.append("🏃 Start with just 10 minutes of activity")
        tips.append("⏰ Schedule exercise like an important appointment")
    
    if not tips:
        tips.append("🌟 You're doing great! Keep up the good work!")
    
    return tips

# Simple in-memory storage for demo (in real app, would use database)
water_logs = []
exercise_logs = []
diet_logs = []
user_diet_plan = {}
log_id_counter = 1

# Simple in-memory storage for demo (in real app, would use database)
water_logs = []
exercise_logs = []
diet_logs = []
user_diet_plan = {}
daily_compliance_calendar = {}  # New: Calendar for tracking daily compliance
daily_tasks = {}  # New: Daily predefined tasks
log_id_counter = 1

# Enhanced encouragement message pools with emojis and dynamic variety
ENCOURAGEMENT_MESSAGES = {
    'perfect_diet': [
        "🌟 Perfect! You're a nutrition champion today! 🥗💪",
        "🏆 Outstanding diet compliance! You're crushing it! 🍽️🔥",
        "⭐ Meal plan master! Your body thanks you! 🙏💚",
        "🎯 Perfect nutrition! You're unstoppable! 🚀💫",
        "👑 Diet royalty! You're ruling your health game! 👑🌟",
        "💚 Perfect fuel! Your cells are celebrating! 🎉🌈",
        "🥗 Nutrition perfection! You're absolutely glowing! ✨🌟"
    ],
    'good_diet': [
        "💪 Great job on your diet today! Keep it up! 🌈🍽️",
        "👏 Nice work with your food choices! You're building habits! 🌱🌿",
        "🌟 Good nutrition choices! Progress is happening! 📈📊",
        "💪 Solid diet work! Every healthy meal counts! 🍽️⭐",
        "🌈 Great food choices! You're on the right path! 🛤️🎯",
        "🥗 Keep it going! Your body appreciates it! 🙏💚",
        "🍽️ Awesome choices! You're making progress! 📈✨"
    ],
    'perfect_exercise': [
        "🔥 Workout warrior! You killed that exercise! 💪🏋️",
        "⚡ Fitness champion! Your energy is amazing! ⚡🌟",
        "🏃 Exercise master! You're unstoppable today! 🌟🔥",
        "💪 Perfect workout! Your strength is showing! 🏋️💪",
        "🎯 Fitness goal crusher! You're absolutely killing it! 🎯🚀",
        "🌟 Incredible workout! You're on fire! 🔥💫",
        "💥 Explosive performance! You're crushing goals! 🎆🏆"
    ],
    'good_exercise': [
        "👍 Great workout! Movement is medicine! 💊🏃",
        "🌱 Good exercise session! You're building strength! 💪🌿",
        "🚀 Nice workout! Consistency is key! 🔑🌟",
        "💪 Solid effort! Every rep counts! 📊⭐",
        "🌟 Good movement! Your body appreciates it! 🙏💪",
        "🏃 Keep pushing! You're getting stronger! 💪📈",
        "⚡ Great energy! Your dedication shows! 🌟💫"
    ],
    'perfect_water': [
        "💧 Hydration hero! Your body is thriving! 🌊💧",
        "🌊 Water champion! Perfect hydration achieved! 💧🌟",
        "💦 Perfect water intake! Your cells are happy! 😊💚",
        "🚰 Hydration master! You're crushing your goals! 🎯💧",
        "💧 Water wizard! Perfect fluid balance! ✨🌊",
        "💎 Hydration perfection! Your body is glowing! ✨🌟",
        "🌊 Perfect balance! You're absolutely crushing it! 💧🏆"
    ],
    'good_water': [
        "💪 Good hydration! Keep sipping! 💧🌱",
        "🌱 Nice water work! Your body thanks you! 🙏💚",
        "💦 Good hydration! You're on track! 🎯💧",
        "🌊 Solid water intake! Keep it flowing! 💧🌊",
        "💧 Good hydration! Every sip helps! 💦⭐",
        "🌟 Keep it up! Your cells appreciate it! 🙏💧",
        "💚 Great start! You're building the habit! 🌱💧"
    ],
    'streak_bonus': [
        "🔥🔥 STREAK FIRE! You're on a roll! Keep it going! 🔥🔥",
        "⚡⚡ CONSISTENCY KING! Your dedication is inspiring! ⚡⚡",
        "🌟🌟 STREAK STAR! You're building amazing habits! 🌟🌟",
        "💪💪 HABIT HERO! Your consistency is your superpower! 💪💪",
        "🏆🏆 STREAK CHAMPION! Unstoppable momentum! 🏆🏆",
        "🎆🎆 STREAK LEGEND! You're absolutely on fire! 🔥🌟",
        "⭐⭐ STREAK MASTER! Your dedication is incredible! ⭐⭐"
    ],
    'daily_complete': [
        "🎉 PERFECT DAY! You nailed everything! 🌟🎊",
        "🏆 DAY CHAMPION! Complete success in all areas! 💪🏋️",
        "⭐ ALL-STAR DAY! You're absolutely crushing it! 🚀⭐",
        "👑 MASTER DAY! Total wellness achievement! 👑🌟",
        "🎯 GOAL CRUSHER! Perfect day completed! 🎯🚀",
        "🌈 PERFECT EXECUTION! You're unstoppable today! 🌈🔥",
        "💫 LEGENDARY DAY! You're absolutely on fire! 💫🏆"
    ]
}

# Enhanced goal-based image pools with more variety
GOAL_IMAGES = {
    'weight_gain': {
        'daily_complete': [
            'https://picsum.photos/seed/muscle-growth-progress/400/300.jpg',
            'https://picsum.photos/seed/strength-building-journey/400/300.jpg',
            'https://picsum.photos/seed/weight-gain-success/400/300.jpg',
            'https://picsum.photos/seed/mass-building-results/400/300.jpg',
            'https://picsum.photos/seed/muscle-transformation/400/300.jpg',
            'https://picsum.photos/seed/strength-gains-visible/400/300.jpg',
            'https://picsum.photos/seed/workout-progress/400/300.jpg'
        ],
        'streak_bonus': [
            'https://picsum.photos/seed/muscle-streak-fire/400/300.jpg',
            'https://picsum.photos/seed/consistency-gains-momentum/400/300.jpg',
            'https://picsum.photos/seed/weight-gain-streak-champion/400/300.jpg',
            'https://picsum.photos/seed/strength-consistency-legend/400/300.jpg',
            'https://picsum.photos/seed/mass-building-streak-master/400/300.jpg',
            'https://picsum.photos/seed/gym-consistency-hero/400/300.jpg'
        ],
        'weekly_achievement': [
            'https://picsum.photos/seed/weekly-muscle-growth/400/300.jpg',
            'https://picsum.photos/seed/weekly-strength-results/400/300.jpg',
            'https://picsum.photos/seed/weekly-gains-transformation/400/300.jpg',
            'https://picsum.photos/seed/weekly-progress-visible/400/300.jpg',
            'https://picsum.photos/seed/weekly-mass-building/400/300.jpg'
        ]
    },
    'weight_loss': {
        'daily_complete': [
            'https://picsum.photos/seed/fat-burning-results/400/300.jpg',
            'https://picsum.photos/seed/weight-loss-transformation/400/300.jpg',
            'https://picsum.photos/seed/slimming-down-progress/400/300.jpg',
            'https://picsum.photos/seed/getting-fit-success/400/300.jpg',
            'https://picsum.photos/seed/fitness-transformation-visible/400/300.jpg',
            'https://picsum.photos/seed/calorie-burn-results/400/300.jpg',
            'https://picsum.photos/seed/weight-loss-journey/400/300.jpg'
        ],
        'streak_bonus': [
            'https://picsum.photos/seed/fat-loss-streak-fire/400/300.jpg',
            'https://picsum.photos/seed/weight-loss-consistency-hero/400/300.jpg',
            'https://picsum.photos/seed/slimming-streak-champion/400/300.jpg',
            'https://picsum.photos/seed/fitness-streak-legend/400/300.jpg',
            'https://picsum.photos/seed/transformation-streak-master/400/300.jpg'
        ],
        'weekly_achievement': [
            'https://picsum.photos/seed/weekly-fat-loss-results/400/300.jpg',
            'https://picsum.photos/seed/weekly-transformation-visible/400/300.jpg',
            'https://picsum.photos/seed/weekly-slimming-progress/400/300.jpg',
            'https://picsum.photos/seed/weekly-fitness-achievement/400/300.jpg',
            'https://picsum.photos/seed/weekly-weight-loss-success/400/300.jpg'
        ]
    },
    'maintenance': {
        'daily_complete': [
            'https://picsum.photos/seed/fitness-balance-perfect/400/300.jpg',
            'https://picsum.photos/seed/health-maintenance-success/400/300.jpg',
            'https://picsum.photos/seed/wellness-lifestyle-achievement/400/300.jpg',
            'https://picsum.photos/seed/active-living-balance/400/300.jpg',
            'https://picsum.photos/seed/healthy-balance-mastery/400/300.jpg',
            'https://picsum.photos/seed/wellness-routine-success/400/300.jpg'
        ],
        'streak_bonus': [
            'https://picsum.photos/seed/consistency-fitness-hero/400/300.jpg',
            'https://picsum.photos/seed/wellness-streak-champion/400/300.jpg',
            'https://picsum.photos/seed/health-consistency-master/400/300.jpg',
            'https://picsum.photos/seed/balance-streak-legend/400/300.jpg',
            'https://picsum.photos/seed/lifestyle-consistency-king/400/300.jpg'
        ],
        'weekly_achievement': [
            'https://picsum.photos/seed/weekly-wellness-achievement/400/300.jpg',
            'https://picsum.photos/seed/weekly-balance-success/400/300.jpg',
            'https://picsum.photos/seed/weekly-health-mastery/400/300.jpg',
            'https://picsum.photos/seed/weekly-fitness-balance/400/300.jpg',
            'https://picsum.photos/seed/weekly-lifestyle-perfection/400/300.jpg'
        ]
    }
}

@app.route('/api/daily-tasks', methods=['GET'])
def get_daily_tasks():
    """Get predefined daily tasks based on user's diet plan"""
    try:
        date_str = request.args.get('date', datetime.now().date().isoformat())
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        if not user_diet_plan:
            return jsonify({'error': 'No diet plan found. Please get diet recommendations first.'}), 404
        
        # Generate predefined tasks for the day
        daily_tasks_data = generate_daily_predefined_tasks(target_date, None)
        
        return jsonify(daily_tasks_data)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get daily tasks: {str(e)}'}), 500

@app.route('/api/complete-task', methods=['POST'])
def complete_task():
    """Complete a predefined task with encouragement and image reward"""
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        task_type = data.get('task_type')  # 'diet', 'exercise', 'water'
        
        if not task_id or not task_type:
            return jsonify({'error': 'task_id and task_type are required'}), 400
        
        # Handle date properly - use today's date if not provided
        date_param = data.get('date')
        if date_param:
            if isinstance(date_param, str):
                target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                date_str = date_param
            else:
                target_date = date_param
                date_str = target_date.isoformat()
        else:
            target_date = datetime.now().date()
            date_str = target_date.isoformat()
        
        # Get or create daily tasks
        if date_str not in daily_tasks:
            daily_tasks[date_str] = generate_daily_predefined_tasks(target_date, None)
        
        # Mark task as completed
        task_completed = False
        encouragement = ""
        reward_image = ""
        
        if task_type == 'diet':
            for meal in daily_tasks[date_str]['diet_tasks']:
                if meal['id'] == task_id and not meal['completed']:
                    meal['completed'] = True
                    meal['completed_at'] = get_ist_time().isoformat()
                    task_completed = True
                    encouragement = get_random_encouragement('perfect_diet')
                    reward_image = get_goal_image('daily_complete')
                    break
        
        elif task_type == 'exercise':
            for exercise in daily_tasks[date_str]['exercise_tasks']:
                if exercise['id'] == task_id and not exercise['completed']:
                    exercise['completed'] = True
                    exercise['completed_at'] = get_ist_time().isoformat()
                    task_completed = True
                    encouragement = get_random_encouragement('perfect_exercise')
                    reward_image = get_goal_image('daily_complete')
                    break
        
        elif task_type == 'water':
            for water_task in daily_tasks[date_str]['water_tasks']:
                if water_task['id'] == task_id and not water_task['completed']:
                    water_task['completed'] = True
                    water_task['completed_at'] = get_ist_time().isoformat()
                    task_completed = True
                    encouragement = get_random_encouragement('perfect_water')
                    reward_image = get_goal_image('daily_complete')
                    break
        
        if not task_completed:
            return jsonify({'error': 'Task not found or already completed'}), 400
        
        # Check if all tasks are completed for bonus encouragement and image
        all_completed = check_all_tasks_completed(date_str)
        if all_completed:
            encouragement = get_random_encouragement('daily_complete')
            reward_image = get_goal_image('daily_complete')
        
        # Check for streak bonus with special image
        streak_bonus = check_streak_bonus(target_date)
        if streak_bonus:
            encouragement += " " + get_random_encouragement('streak_bonus')
            reward_image = get_goal_image('streak_bonus')
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'encouragement': encouragement,
            'reward_image': reward_image,
            'all_completed': all_completed,
            'streak_bonus': streak_bonus
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to complete task: {str(e)}'}), 500

def get_goal_image(achievement_type):
    """Get appropriate image based on user's goal and achievement"""
    import random
    
    # Determine user's goal
    user_goal = 'maintenance'  # default
    if user_diet_plan:
        diet_info = user_diet_plan.get('diet_plan_info', {})
        goal = diet_info.get('goal', '').lower()
        
        if 'gain' in goal:
            user_goal = 'weight_gain'
        elif 'loss' in goal:
            user_goal = 'weight_loss'
    
    # Get appropriate image pool
    if user_goal in GOAL_IMAGES and achievement_type in GOAL_IMAGES[user_goal]:
        return random.choice(GOAL_IMAGES[user_goal][achievement_type])
    
    # Fallback to maintenance images
    return random.choice(GOAL_IMAGES['maintenance'][achievement_type])

def generate_daily_predefined_tasks(date, user_id=None):
    """Generate predefined tasks based on user's diet plan - DYNAMIC for each day"""
    import random
    
    # Get user-specific diet plan if user_id is provided
    if user_id and user_id in user_profiles:
        user_profile = user_profiles[user_id]
        diet_plan = user_profile.get('diet_plan', {})
        user_metrics = diet_plan.get('diet_plan_info', {}).get('user_metrics', {})
        bmi_category = user_metrics.get('bmi_category', 'normal')
        weight = user_profile.get('weight', 70)
        daily_calories = diet_plan.get('diet_plan_info', {}).get('daily_calorie_needs', 2000)
        recommended_meals = diet_plan.get('recommended_meals', {})
        diet_info = diet_plan.get('diet_plan_info', {})
        user_goal = diet_info.get('goal', '').lower()
    else:
        # Fallback to global data
        user_metrics = user_diet_plan.get('user_metrics', {})
        bmi_category = user_metrics.get('bmi_category', 'normal')
        weight = user_metrics.get('weight', 70)
        daily_calories = user_metrics.get('daily_calorie_needs', 2000)
        recommended_meals = user_diet_plan.get('recommended_meals', {})
        diet_info = user_diet_plan.get('diet_plan_info', {})
        user_goal = diet_info.get('goal', '').lower()
    
    # Use date as seed for variety but consistent for the same day
    if isinstance(date, str):
        date_str = date
    else:
        date_str = date.isoformat()
    day_seed = hash(date_str) % 1000
    random.seed(day_seed)
    
    # Generate diet tasks (same meals but different order/presentation)
    diet_tasks = []
    meal_types = ['breakfast', 'lunch', 'dinner', 'snacks']
    
    # Shuffle meal order for variety
    shuffled_meals = meal_types.copy()
    random.shuffle(shuffled_meals)
    
    for i, meal_type in enumerate(shuffled_meals):
        if meal_type in recommended_meals:
            diet_tasks.append({
                'id': f'diet_{i}',
                'type': 'diet',
                'meal_type': meal_type,
                'description': recommended_meals[meal_type],
                'completed': False,
                'completed_at': None,
                'icon': random.choice(['🍽️', '🥗', '🍳', '🥪', '🍱', '🍲'])
            })
    
    # Generate DYNAMIC exercise tasks based on user's specific requirements
    exercise_tasks = []
    
    if 'gain' in user_goal:
        # Weight gain specific exercises
        exercise_pools = {
            'strength': [
                {'name': 'Heavy Weight Training', 'duration': '45 min', 'icon': '🏋️', 'focus': 'muscle building'},
                {'name': 'Deadlifts', 'duration': '30 min', 'icon': '💪', 'focus': 'strength'},
                {'name': 'Pull-ups', 'duration': '15 min', 'icon': '🔗', 'focus': 'back strength'},
                {'name': 'Bench Press', 'duration': '35 min', 'icon': '🏋️', 'focus': 'chest strength'},
                {'name': 'Squats', 'duration': '40 min', 'icon': '🦵', 'focus': 'leg strength'},
                {'name': 'Overhead Press', 'duration': '25 min', 'icon': '💪', 'focus': 'shoulder strength'},
                {'name': 'Barbell Rows', 'duration': '30 min', 'icon': '🏋️', 'focus': 'back thickness'},
                {'name': 'Dumbbell Curls', 'duration': '20 min', 'icon': '💪', 'focus': 'arm growth'}
            ],
            'cardio': [
                {'name': 'Light Walking', 'duration': '20 min', 'icon': '🚶', 'focus': 'active recovery'},
                {'name': 'Leisure Cycling', 'duration': '30 min', 'icon': '🚴', 'focus': 'cardio health'},
                {'name': 'Swimming', 'duration': '25 min', 'icon': '🏊', 'focus': 'full body'},
                {'name': 'Elliptical', 'duration': '20 min', 'icon': '🏃', 'focus': 'low impact cardio'}
            ]
        }
        # Select 3 strength + 1 cardio (varied each day)
        selected_strength = random.sample(exercise_pools['strength'], min(3, len(exercise_pools['strength'])))
        selected_cardio = random.sample(exercise_pools['cardio'], 1)
        selected_exercises = selected_strength + selected_cardio
        
    elif 'loss' in user_goal:
        # Weight loss specific exercises
        exercise_pools = {
            'cardio': [
                {'name': 'High-Intensity Running', 'duration': '30 min', 'icon': '🏃', 'focus': 'fat burning'},
                {'name': 'HIIT Workout', 'duration': '25 min', 'icon': '⚡', 'focus': 'calorie torch'},
                {'name': 'Jump Rope', 'duration': '20 min', 'icon': '🪢', 'focus': 'cardio blast'},
                {'name': 'Burpees', 'duration': '15 min', 'icon': '🔥', 'focus': 'full body burn'},
                {'name': 'Mountain Climbers', 'duration': '20 min', 'icon': '🏔️', 'focus': 'core burn'},
                {'name': 'Box Jumps', 'duration': '15 min', 'icon': '📦', 'focus': 'explosive power'},
                {'name': 'Battle Ropes', 'duration': '20 min', 'icon': '🪢', 'focus': 'intensity'}
            ],
            'strength': [
                {'name': 'Bodyweight Squats', 'duration': '20 min', 'icon': '🦵', 'focus': 'leg toning'},
                {'name': 'Push-ups', 'duration': '15 min', 'icon': '💪', 'focus': 'upper body'},
                {'name': 'Planks', 'duration': '20 min', 'icon': '🧘', 'focus': 'core strength'},
                {'name': 'Lunges', 'duration': '15 min', 'icon': '🦵', 'focus': 'leg endurance'},
                {'name': 'Mountain Climbers', 'duration': '15 min', 'icon': '🏔️', 'focus': 'core stability'}
            ]
        }
        # Select 3 cardio + 1 strength (varied each day)
        selected_cardio = random.sample(exercise_pools['cardio'], min(3, len(exercise_pools['cardio'])))
        selected_strength = random.sample(exercise_pools['strength'], 1)
        selected_exercises = selected_cardio + selected_strength
        
    else:  # maintenance
        # Balanced fitness exercises
        exercise_pools = {
            'cardio': [
                {'name': 'Moderate Running', 'duration': '30 min', 'icon': '🏃', 'focus': 'cardio health'},
                {'name': 'Swimming', 'duration': '25 min', 'icon': '🏊', 'focus': 'full body'},
                {'name': 'Cycling', 'duration': '40 min', 'icon': '🚴', 'focus': 'endurance'},
                {'name': 'Dancing', 'duration': '30 min', 'icon': '💃', 'focus': 'fun fitness'},
                {'name': 'Rowing Machine', 'duration': '30 min', 'icon': '🚣', 'focus': 'full body'},
                {'name': 'Elliptical', 'duration': '25 min', 'icon': '🏃', 'focus': 'low impact'}
            ],
            'strength': [
                {'name': 'Push-ups', 'duration': '15 min', 'icon': '💪', 'focus': 'upper body'},
                {'name': 'Planks', 'duration': '20 min', 'icon': '🧘', 'focus': 'core stability'},
                {'name': 'Squats', 'duration': '25 min', 'icon': '🦵', 'focus': 'leg strength'},
                {'name': 'Lunges', 'duration': '15 min', 'icon': '🦵', 'focus': 'balance'},
                {'name': 'Pull-ups', 'duration': '15 min', 'icon': '🔗', 'focus': 'back strength'}
            ],
            'flexibility': [
                {'name': 'Yoga Flow', 'duration': '30 min', 'icon': '🧘', 'focus': 'flexibility'},
                {'name': 'Dynamic Stretching', 'duration': '15 min', 'icon': '🤸', 'focus': 'mobility'},
                {'name': 'Pilates', 'duration': '25 min', 'icon': '🤸‍♀️', 'focus': 'core control'},
                {'name': 'Tai Chi', 'duration': '20 min', 'icon': '☯️', 'focus': 'balance'}
            ]
        }
        # Select 2 cardio + 1 strength + 1 flexibility (varied each day)
        selected_cardio = random.sample(exercise_pools['cardio'], 2)
        selected_strength = random.sample(exercise_pools['strength'], 1)
        selected_flexibility = random.sample(exercise_pools['flexibility'], 1)
        selected_exercises = selected_cardio + selected_strength + selected_flexibility
    
    # Randomize exercise order
    random.shuffle(selected_exercises)
    
    for i, exercise in enumerate(selected_exercises):
        exercise_tasks.append({
            'id': f'exercise_{i}',
            'type': 'exercise',
            'name': exercise['name'],
            'duration': exercise['duration'],
            'focus': exercise['focus'],
            'completed': False,
            'completed_at': None,
            'icon': exercise['icon']
        })
    
    # Generate DYNAMIC water tasks based on user's specific requirements
    water_plan = generate_personalized_water(weight, bmi_category)
    total_glasses = water_plan.get('recommended_glasses', 8)
    
    # Different water schedules based on user goal
    if 'gain' in user_goal:
        # Weight gain needs more water for muscle building
        water_schedule_templates = [
            [
                {'time': 'Wake-up Hydration', 'glasses': 2, 'icon': '💧', 'purpose': 'muscle prep'},
                {'time': 'Pre-workout', 'glasses': 2, 'icon': '🏋️', 'purpose': 'performance'},
                {'time': 'Post-workout', 'glasses': 2, 'icon': '💪', 'purpose': 'recovery'},
                {'time': 'With Meals', 'glasses': 2, 'icon': '🍽️', 'purpose': 'digestion'},
                {'time': 'Before Bed', 'glasses': 1, 'icon': '🌙', 'purpose': 'overnight recovery'}
            ],
            [
                {'time': '6 AM Rise', 'glasses': 2, 'icon': '🌅', 'purpose': 'kickstart metabolism'},
                {'time': '9 AM Boost', 'glasses': 2, 'icon': '⚡', 'purpose': 'energy'},
                {'time': '12 PM Lunch', 'glasses': 1, 'icon': '☀️', 'purpose': 'meal hydration'},
                {'time': '3 PM Refuel', 'glasses': 2, 'icon': '🔋', 'purpose': 'afternoon energy'},
                {'time': '6 PM Dinner', 'glasses': 1, 'icon': '🍽️', 'purpose': 'digestion'},
                {'time': '9 PM Wind-down', 'glasses': 1, 'icon': '🌙', 'purpose': 'recovery'}
            ]
        ]
    elif 'loss' in user_goal:
        # Weight loss needs water for metabolism and fullness
        water_schedule_templates = [
            [
                {'time': 'Morning Detox', 'glasses': 2, 'icon': '💧', 'purpose': 'metabolism boost'},
                {'time': 'Before Meals', 'glasses': 1, 'icon': '🥗', 'purpose': 'fullness'},
                {'time': 'Mid-morning', 'glasses': 1, 'icon': '🌤️', 'purpose': 'hunger control'},
                {'time': 'Pre-lunch', 'glasses': 1, 'icon': '☀️', 'purpose': 'portion control'},
                {'time': 'Afternoon', 'glasses': 2, 'icon': '🌆', 'purpose': 'energy boost'},
                {'time': 'Evening', 'glasses': 1, 'icon': '🌙', 'purpose': 'nighttime metabolism'}
            ],
            [
                {'time': 'Fat Burn Start', 'glasses': 2, 'icon': '🔥', 'purpose': 'metabolism'},
                {'time': 'Crush Hunger', 'glasses': 1, 'icon': '🚫', 'purpose': 'appetite control'},
                {'time': 'Energy Boost', 'glasses': 2, 'icon': '⚡', 'purpose': 'calorie burn'},
                {'time': 'Hydration Break', 'glasses': 1, 'icon': '💧', 'purpose': 'focus'},
                {'time': 'Evening Cleanse', 'glasses': 1, 'icon': '🌙', 'purpose': 'detox'}
            ]
        ]
    else:  # maintenance
        water_schedule_templates = [
            [
                {'time': 'Morning Routine', 'glasses': 2, 'icon': '🌅', 'purpose': 'daily start'},
                {'time': 'Work Break', 'glasses': 1, 'icon': '☕', 'purpose': 'focus'},
                {'time': 'Lunch Time', 'glasses': 2, 'icon': '🥗', 'purpose': 'digestion'},
                {'time': 'Afternoon Boost', 'glasses': 2, 'icon': '⚡', 'purpose': 'energy'},
                {'time': 'Evening Wind-down', 'glasses': 1, 'icon': '🌙', 'purpose': 'relaxation'}
            ],
            [
                {'time': 'Hydration Kickstart', 'glasses': 2, 'icon': '💧', 'purpose': 'morning'},
                {'time': 'Midday Refill', 'glasses': 2, 'icon': '🌤️', 'purpose': 'afternoon'},
                {'time': 'Pre-workout', 'glasses': 1, 'icon': '🏋️', 'purpose': 'performance'},
                {'time': 'Post-workout', 'glasses': 1, 'icon': '💪', 'purpose': 'recovery'},
                {'time': 'Evening Hydration', 'glasses': 2, 'icon': '🌙', 'purpose': 'nighttime'}
            ]
        ]
    
    # Select a random water schedule template
    selected_schedule = random.choice(water_schedule_templates)
    
    # Adjust glasses to match total target
    scheduled_total = sum(item['glasses'] for item in selected_schedule)
    if scheduled_total != total_glasses:
        # Adjust last item
        selected_schedule[-1]['glasses'] += (total_glasses - scheduled_total)
    
    water_tasks = []
    for i, schedule in enumerate(selected_schedule):
        water_tasks.append({
            'id': f'water_{i}',
            'type': 'water',
            'time': schedule['time'],
            'glasses': schedule['glasses'],
            'purpose': schedule['purpose'],
            'description': f'Drink {schedule["glasses"]} glasses of water for {schedule["purpose"]}',
            'completed': False,
            'completed_at': None,
            'icon': schedule['icon']
        })
    
    return {
        'date': date_str,
        'diet_tasks': diet_tasks,
        'exercise_tasks': exercise_tasks,
        'water_tasks': water_tasks,
        'total_tasks': len(diet_tasks) + len(exercise_tasks) + len(water_tasks),
        'day_variety': f"Today's mix: {len(exercise_tasks)} exercises, {len(water_tasks)} water sessions",
        'user_goal': user_goal,
        'personalization_note': f"Tasks personalized for {user_goal} goal"
    }

def get_random_encouragement(category):
    """Get random encouragement message with emojis"""
    import random
    return random.choice(ENCOURAGEMENT_MESSAGES.get(category, ['👍 Great job!']))

def check_all_tasks_completed(date_str, user_id=None):
    """Check if all tasks for the day are completed"""
    if user_id and user_id in user_daily_tasks and date_str in user_daily_tasks[user_id]:
        tasks = user_daily_tasks[user_id][date_str]
    else:
        if date_str not in daily_tasks:
            return False
        tasks = daily_tasks[date_str]
    
    # Check all diet tasks
    for meal in tasks['diet_tasks']:
        if not meal['completed']:
            return False
    
    # Check all exercise tasks
    for exercise in tasks['exercise_tasks']:
        if not exercise['completed']:
            return False
    
    # Check all water tasks
    for water in tasks['water_tasks']:
        if not water['completed']:
            return False
    
    return True

def check_streak_bonus(current_date, user_id=None):
    """Check if user deserves streak bonus encouragement"""
    try:
        # Handle both string and date object inputs
        if isinstance(current_date, str):
            current_date = datetime.strptime(current_date, '%Y-%m-%d').date()
        
        # Simple streak check (can be made more sophisticated)
        yesterday = current_date - timedelta(days=1)
        yesterday_str = yesterday.isoformat()
        
        # Check user-specific or global tasks
        if user_id and user_id in user_daily_tasks and yesterday_str in user_daily_tasks[user_id]:
            return check_all_tasks_completed(yesterday_str, user_id)
        elif yesterday_str in daily_tasks:
            return check_all_tasks_completed(yesterday_str)
        
        return False
    except Exception as e:
        # If there's any error, don't give streak bonus
        return False

@app.route('/api/diet-log', methods=['POST'])
@require_auth
def log_meal():
    """Log meal intake"""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['meal_type', 'food_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate nutrition fields (allow 0 values)
        nutrition_fields = ['calories', 'protein', 'carbs', 'fats']
        for field in nutrition_fields:
            if data.get(field) is None or data.get(field) == '':
                return jsonify({'error': f'{field} is required'}), 400
        
        # Initialize user_logs if not exists
        if user_id not in user_logs:
            user_logs[user_id] = {'diet_logs': [], 'exercise_logs': [], 'water_logs': []}
        
        # Initialize diet_logs if not exists
        if 'diet_logs' not in user_logs[user_id]:
            user_logs[user_id]['diet_logs'] = []
        
        # Create meal entry
        meal_entry = {
            'id': str(len(user_logs[user_id]['diet_logs']) + 1),
            'meal_type': data['meal_type'],
            'food_name': data['food_name'],
            'calories': int(data['calories']) or 0,
            'protein': float(data['protein']) or 0.0,
            'carbs': float(data['carbs']) or 0.0,
            'fats': float(data['fats']) or 0.0,
            'serving_size': int(data.get('serving_size', 100)),
            'date': data.get('date', get_ist_time().date().isoformat()),
            'logged_at': get_ist_time().isoformat()
        }
        
        # Add to user logs
        user_logs[user_id]['diet_logs'].append(meal_entry)
        
        return jsonify({
            'success': True,
            'message': 'Meal logged successfully',
            'meal': meal_entry
        })
    except Exception as e:
        return jsonify({'error': f'Failed to log meal: {str(e)}'}), 500

@app.route('/api/diet-log', methods=['GET'])
@require_auth
def get_meal_logs():
    """Get meal logs for a specific date"""
    try:
        user_id = request.user_id
        date_param = request.args.get('date')
        
        if not date_param:
            date_param = get_ist_time().date().isoformat()
        
        # Initialize user_logs if not exists
        if user_id not in user_logs:
            user_logs[user_id] = {'diet_logs': [], 'exercise_logs': [], 'water_logs': []}
        
        # Initialize diet_logs if not exists
        if 'diet_logs' not in user_logs[user_id]:
            user_logs[user_id]['diet_logs'] = []
        
        # Filter logs by date
        logs = []
        for log in user_logs[user_id]['diet_logs']:
            if log['date'] == date_param:
                logs.append(log)
        
        return jsonify({
            'success': True,
            'date': date_param,
            'meals': logs
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get meal logs: {str(e)}'}), 500

def search_foods(query):
    """Search for foods in the food database"""
    query = query.lower()
    matches = []
    
    for food_name, nutrition in FOOD_DATABASE.items():
        if query in food_name.lower():
            matches.append({
                'name': food_name,
                'calories': nutrition['calories'],
                'protein': nutrition['protein'],
                'carbs': nutrition['carbs'],
                'fats': nutrition['fats']
            })
    
    return matches

@app.route('/api/foods/search', methods=['GET'])
@require_auth
def search_foods_endpoint():
    """Search for foods in database"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'success': True, 'foods': []})
        
        matches = search_foods(query)
        return jsonify({'success': True, 'foods': matches})
        
    except Exception as e:
        return jsonify({'error': f'Failed to search foods: {str(e)}'}), 500

def get_food_nutrition(food_name, serving_size=100):
    """Get nutrition information for a specific food"""
    food_name = food_name.lower()
    
    if food_name in FOOD_DATABASE:
        base_nutrition = FOOD_DATABASE[food_name]
        # Scale nutrition based on serving size
        scale_factor = serving_size / 100
        return {
            'calories': round(base_nutrition['calories'] * scale_factor, 1),
            'protein': round(base_nutrition['protein'] * scale_factor, 1),
            'carbs': round(base_nutrition['carbs'] * scale_factor, 1),
            'fats': round(base_nutrition['fats'] * scale_factor, 1)
        }
    else:
        # Default nutrition for unknown foods
        return {
            'calories': 100,
            'protein': 10,
            'carbs': 15,
            'fats': 5
        }

@app.route('/api/foods/nutrition', methods=['GET'])
@require_auth
def get_food_nutrition_endpoint():
    """Get nutrition info for a specific food"""
    try:
        food_name = request.args.get('food', '')
        serving_size = int(request.args.get('serving', 100))
        
        if not food_name:
            return jsonify({'error': 'Food name is required'}), 400
        
        nutrition = get_food_nutrition(food_name, serving_size)
        return jsonify({'success': True, 'nutrition': nutrition})
        
    except Exception as e:
        return jsonify({'error': f'Failed to get nutrition: {str(e)}'}), 500

def admin_required(f):
    """Decorator to require admin role"""
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Admin authorization required'}), 401
        
        token = token.replace('Bearer ', '')
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Check if user has admin role
        if user_id not in user_profiles or user_profiles[user_id].get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/debug/exercise-status', methods=['GET'])
@require_auth
def debug_exercise_status():
    """Debug endpoint to check exercise task generation"""
    try:
        user_id = request.user_id
        date_str = request.args.get('date', datetime.now().date().isoformat())
        
        # Check user profile
        user_profile = user_profiles.get(user_id, {})
        diet_plan = user_profile.get('diet_plan', {})
        has_diet_plan = bool(diet_plan.get('diet_plan_info'))
        
        # Check daily tasks
        if user_id not in user_daily_tasks:
            user_daily_tasks[user_id] = {}
        if date_str not in user_daily_tasks[user_id]:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            user_daily_tasks[user_id][date_str] = generate_daily_predefined_tasks(target_date, user_id)
        
        daily_tasks = user_daily_tasks[user_id][date_str]
        
        return jsonify({
            'user_id': user_id,
            'date': date_str,
            'has_diet_plan': has_diet_plan,
            'diet_plan_info': diet_plan.get('diet_plan_info', {}),
            'daily_tasks': {
                'exercise_tasks_count': len(daily_tasks.get('exercise_tasks', [])),
                'exercise_tasks': daily_tasks.get('exercise_tasks', []),
                'water_tasks_count': len(daily_tasks.get('water_tasks', [])),
                'diet_tasks_count': len(daily_tasks.get('diet_tasks', []))
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Debug error: {str(e)}'}), 500

        date_str = request.args.get('date', datetime.now().date().isoformat())
        
        if date_str not in daily_tasks:
            return jsonify({
                'date': date_str,
                'completed_diet': [],
                'completed_exercise': [],
                'completed_water': [],
                'total_completed': 0
            })
        
        tasks = daily_tasks[date_str]
        
        # Get completed tasks
        completed_diet = [meal for meal in tasks['diet_tasks'] if meal['completed']]
        completed_exercise = [ex for ex in tasks['exercise_tasks'] if ex['completed']]
        completed_water = [water for water in tasks['water_tasks'] if water['completed']]
        
        total_completed = len(completed_diet) + len(completed_exercise) + len(completed_water)
        
        return jsonify({
            'date': date_str,
            'completed_diet': completed_diet,
            'completed_exercise': completed_exercise,
            'completed_water': completed_water,
            'total_completed': total_completed,
            'total_tasks': tasks['total_tasks'],
            'completion_rate': round((total_completed / tasks['total_tasks']) * 100, 1) if tasks['total_tasks'] > 0 else 0
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get user activities: {str(e)}'}), 500

@app.route('/api/progress-report', methods=['GET'])
def get_progress_report():
    """Get detailed report of what user actually did"""
    try:
        # Get date range (default to last 7 days)
        days = int(request.args.get('days', 7))
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        report_data = {
            'period': f'{days} days',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'daily_summary': [],
            'total_completed_tasks': 0,
            'total_tasks': 0,
            'completion_rate': 0,
            'achievements': []
        }
        
        total_completed = 0
        total_possible = 0
        
        # Generate report for each day
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            
            if date_str in daily_tasks:
                tasks = daily_tasks[date_str]
                
                completed_diet = len([meal for meal in tasks['diet_tasks'] if meal['completed']])
                completed_exercise = len([ex for ex in tasks['exercise_tasks'] if ex['completed']])
                completed_water = len([water for water in tasks['water_tasks'] if water['completed']])
                
                day_total = completed_diet + completed_exercise + completed_water
                day_possible = tasks['total_tasks']
                
                total_completed += day_total
                total_possible += day_possible
                
                daily_summary = {
                    'date': date_str,
                    'completed_diet': completed_diet,
                    'completed_exercise': completed_exercise,
                    'completed_water': completed_water,
                    'total_completed': day_total,
                    'total_tasks': day_possible,
                    'completion_rate': round((day_total / day_possible) * 100, 1) if day_possible > 0 else 0,
                    'perfect_day': day_total == day_possible
                }
                
                report_data['daily_summary'].append(daily_summary)
            else:
                # Day with no tasks
                report_data['daily_summary'].append({
                    'date': date_str,
                    'completed_diet': 0,
                    'completed_exercise': 0,
                    'completed_water': 0,
                    'total_completed': 0,
                    'total_tasks': 0,
                    'completion_rate': 0,
                    'perfect_day': False
                })
            
            current_date += timedelta(days=1)
        
        report_data['total_completed_tasks'] = total_completed
        report_data['total_tasks'] = total_possible
        report_data['completion_rate'] = round((total_completed / total_possible) * 100, 1) if total_possible > 0 else 0
        
        # Generate achievements
        perfect_days = len([day for day in report_data['daily_summary'] if day['perfect_day']])
        if perfect_days >= 5:
            report_data['achievements'].append('🏆 Perfect Week Champion')
        elif perfect_days >= 3:
            report_data['achievements'].append('⭐ Consistency Master')
        elif perfect_days >= 1:
            report_data['achievements'].append('💪 Goal Getter')
        
        if report_data['completion_rate'] >= 80:
            report_data['achievements'].append('🌟 Excellence Achiever')
        elif report_data['completion_rate'] >= 60:
            report_data['achievements'].append('👍 Solid Performer')
        
        return jsonify(report_data)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get progress report: {str(e)}'}), 500

@app.route('/api/diet-log', methods=['POST'])
def log_diet():
    """Log diet intake endpoint"""
    global log_id_counter
    try:
        data = request.get_json()
        meal_type = data.get('meal_type', '').strip()  # breakfast, lunch, dinner, snacks
        food_description = data.get('food_description', '').strip()
        calories = data.get('calories')
        
        if not meal_type or not food_description:
            return jsonify({'error': 'meal_type and food_description are required'}), 400
        
        if calories is not None:
            try:
                calories = int(calories)
            except (ValueError, TypeError):
                calories = None
        
        # Create new diet log entry
        new_log = {
            'id': log_id_counter,
            'meal_type': meal_type,
            'food_description': food_description,
            'calories': calories,
            'logged_at': datetime.now().isoformat() + 'Z',
            'date': datetime.now().date().isoformat()
        }
        
        # Add to in-memory storage
        diet_logs.append(new_log)
        log_id_counter += 1
        
        # Check if this matches recommendation
        match_result = check_diet_compliance(meal_type, food_description, calories)
        new_log['match_result'] = match_result
        
        return jsonify(new_log), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to log diet: {str(e)}'}), 500

@app.route('/api/diet-log', methods=['GET'])
def get_diet_logs():
    """Get diet logs endpoint"""
    try:
        date_str = request.args.get('date')
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'date must be YYYY-MM-DD'}), 400
        else:
            target_date = datetime.now().date()
        
        # Filter logs for the target date
        today_logs = [log for log in diet_logs if log.get('date') == target_date.isoformat()]
        
        return jsonify({
            'date': target_date.isoformat(),
            'logs': today_logs
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get diet logs: {str(e)}'}), 500

@app.route('/api/compliance-report', methods=['GET'])
def get_compliance_report():
    """Get diet compliance report with encouragement"""
    try:
        date_str = request.args.get('date')
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'date must be YYYY-MM-DD'}), 400
        else:
            target_date = datetime.now().date()
        
        # Get today's diet logs
        today_logs = [log for log in diet_logs if log.get('date') == target_date.isoformat()]
        
        # Get user's recommended plan (would be stored per user in real app)
        recommended_plan = user_diet_plan.get('recommended_meals', {})
        
        # Analyze compliance
        compliance_analysis = analyze_daily_compliance(today_logs, recommended_plan)
        
        # Generate encouragement message
        encouragement = generate_encouragement_message(compliance_analysis)
        
        return jsonify({
            'date': target_date.isoformat(),
            'compliance_analysis': compliance_analysis,
            'encouragement': encouragement,
            'recommended_plan': recommended_plan,
            'actual_logs': today_logs
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get compliance report: {str(e)}'}), 500

def check_diet_compliance(meal_type, food_description, calories):
    """Check if logged food matches recommendation"""
    recommended_plan = user_diet_plan.get('recommended_meals', {})
    recommended_food = recommended_plan.get(meal_type, '')
    
    if not recommended_food:
        return {'match': False, 'reason': 'No recommendation for this meal type'}
    
    # Simple matching logic (in real app, would be more sophisticated)
    food_lower = food_description.lower()
    recommended_lower = recommended_food.lower()
    
    # Check for key ingredients
    match_score = 0
    if 'oatmeal' in food_lower and 'oatmeal' in recommended_lower:
        match_score += 50
    if 'chicken' in food_lower and 'chicken' in recommended_lower:
        match_score += 50
    if 'salmon' in food_lower and 'salmon' in recommended_lower:
        match_score += 50
    if 'salad' in food_lower and 'salad' in recommended_lower:
        match_score += 30
    if 'vegetables' in food_lower and 'vegetables' in recommended_lower:
        match_score += 30
    
    # Check calorie range (±100 calories)
    if calories:
        try:
            # Extract calories from recommendation
            import re
            rec_cal_match = re.search(r'\((\d+)\s*cal\)', recommended_lower)
            if rec_cal_match:
                rec_calories = int(rec_cal_match.group(1))
                if abs(calories - rec_calories) <= 100:
                    match_score += 20
        except:
            pass
    
    is_match = match_score >= 50
    return {
        'match': is_match,
        'score': match_score,
        'recommended': recommended_food,
        'actual': food_description
    }

def analyze_daily_compliance(logs, recommended_plan):
    """Analyze daily diet compliance"""
    meal_types = ['breakfast', 'lunch', 'dinner', 'snacks']
    completed_meals = []
    missed_meals = []
    partial_meals = []
    
    for meal_type in meal_types:
        meal_logs = [log for log in logs if log['meal_type'] == meal_type]
        recommended_food = recommended_plan.get(meal_type, '')
        
        if not meal_logs:
            if recommended_food:
                missed_meals.append({
                    'meal_type': meal_type,
                    'recommended': recommended_food,
                    'status': 'missed'
                })
        else:
            # Check if any meal matches well
            best_match = max(meal_logs, key=lambda x: x.get('match_result', {}).get('score', 0))
            match_result = best_match.get('match_result', {})
            
            if match_result.get('match', False):
                completed_meals.append({
                    'meal_type': meal_type,
                    'recommended': recommended_food,
                    'actual': best_match['food_description'],
                    'score': match_result.get('score', 0),
                    'status': 'completed'
                })
            else:
                partial_meals.append({
                    'meal_type': meal_type,
                    'recommended': recommended_food,
                    'actual': best_match['food_description'],
                    'score': match_result.get('score', 0),
                    'status': 'partial'
                })
    
    total_meals = len([meal for meal in meal_types if recommended_plan.get(meal)])
    compliance_rate = (len(completed_meals) / total_meals * 100) if total_meals > 0 else 0
    
    return {
        'completed_meals': completed_meals,
        'missed_meals': missed_meals,
        'partial_meals': partial_meals,
        'compliance_rate': round(compliance_rate, 1),
        'total_meals': total_meals,
        'meals_tracked': len(completed_meals) + len(partial_meals)
    }

def generate_encouragement_message(analysis):
    """Generate personalized encouragement message"""
    compliance_rate = analysis['compliance_rate']
    completed_count = len(analysis['completed_meals'])
    total_meals = analysis['total_meals']
    
    if compliance_rate >= 80:
        return {
            'level': 'excellent',
            'title': '🌟 Excellent Job!',
            'message': f"You're following your diet plan perfectly! {completed_count}/{total_meals} meals completed. Keep up the amazing work!",
            'color': 'success',
            'achievements': ['Diet Champion', 'Consistency Master', 'Goal Crusher']
        }
    elif compliance_rate >= 60:
        return {
            'level': 'good',
            'title': '💪 Great Progress!',
            'message': f"You're doing well! {completed_count}/{total_meals} meals completed. You're building healthy habits!",
            'color': 'info',
            'achievements': ['Health Enthusiast', 'Consistent Eater']
        }
    elif compliance_rate >= 40:
        return {
            'level': 'fair',
            'title': '👍 Keep Going!',
            'message': f"You're making progress! {completed_count}/{total_meals} meals completed. Every healthy choice counts!",
            'color': 'warning',
            'achievements': ['Health Conscious']
        }
    else:
        return {
            'level': 'needs_improvement',
            'title': '🎯 Let\'s Try Again!',
            'message': f"Today was challenging ({completed_count}/{total_meals} meals). Tomorrow is a new opportunity to reach your goals!",
            'color': 'danger',
            'achievements': ['Health Explorer']
        }

@app.route('/api/save-profile', methods=['POST'])
@require_auth
def save_profile():
    """Save user profile and generate diet recommendations (protected)"""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        # Update user profile with new data
        if user_id in user_profiles:
            profile = user_profiles[user_id]
            profile.update({
                'age': data.get('age', profile.get('age')),
                'gender': data.get('gender', profile.get('gender')),
                'weight': data.get('weight', profile.get('weight')),
                'height': data.get('height', profile.get('height')),
                'activity_level': data.get('activity_level', profile.get('activity_level')),
                'goal': data.get('goal', profile.get('goal')),
                'medical_conditions': data.get('medical_conditions', profile.get('medical_conditions', '')),
                'allergies': data.get('allergies', profile.get('allergies', '')),
                'dietary_preferences': data.get('dietary_preferences', profile.get('dietary_preferences', '')),
                'diseases': data.get('diseases', profile.get('diseases', '')),
                'updated_at': get_ist_time().isoformat()
            })
        else:
            # Create new profile if it doesn't exist
            user_profiles[user_id] = {
                'id': user_id,
                'name': data.get('name', 'User'),
                'email': data.get('email', ''),
                'age': data.get('age'),
                'gender': data.get('gender'),
                'weight': data.get('weight'),
                'height': data.get('height'),
                'activity_level': data.get('activity_level', 'moderate'),
                'goal': data.get('goal', 'maintenance'),
                'medical_conditions': data.get('medical_conditions', ''),
                'allergies': data.get('allergies', ''),
                'dietary_preferences': data.get('dietary_preferences', ''),
                'diseases': data.get('diseases', ''),
                'created_at': get_ist_time().isoformat(),
                'updated_at': get_ist_time().isoformat()
            }
        
        # Generate diet recommendation using the existing system
        weight = float(data.get('weight'))
        height = float(data.get('height'))
        age = int(data.get('age'))
        gender = data.get('gender')
        activity_level = data.get('activity_level')
        health_conditions = data.get('medical_conditions', '').lower().split(', ') if data.get('medical_conditions') else []
        
        recommendation = diet_system.get_diet_recommendation(weight, height, age, gender, activity_level, health_conditions)
        comprehensive_plan = diet_system._generate_comprehensive_plan(weight, height, age, gender, activity_level, health_conditions, recommendation)
        
        # Store the diet plan for this user
        user_profiles[user_id]['diet_plan'] = comprehensive_plan
        
        return jsonify({
            'success': True,
            'message': 'Profile saved successfully',
            'recommendation': comprehensive_plan
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to save profile: {str(e)}'}), 500

# Initialize the diet system
diet_system = SimpleDietRecommender()

# Global variables for task management (will be replaced with user-specific storage)
user_diet_plan = {}
daily_tasks = {}
daily_compliance_calendar = {}
log_id_counter = 1

# Create default admin user on startup
def create_default_admin():
    """Create default admin user on startup"""
    admin_email = 'admin@diet-system.com'
    admin_password = 'admin123'
    
    if admin_email not in users:
        user_id = str(len(users) + 1)
        hashed_password = hash_password(admin_password)
        
        # Store user authentication info
        users[admin_email] = {
            'id': user_id,
            'email': admin_email,
            'password': hashed_password,
            'name': 'Debug Admin'
        }
        
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
            'diet_plan': {
                'diet_plan_info': {
                    'user_metrics': {
                        'weight': 70,
                        'height': 170,
                        'bmi': 24.2,
                        'bmi_category': 'normal'
                    },
                    'daily_calorie_needs': 2000,
                    'goal': 'maintenance'
                },
                'recommended_meals': {
                    'breakfast': 'Oatmeal with fruits',
                    'lunch': 'Grilled chicken salad',
                    'dinner': 'Vegetable curry with rice',
                    'snacks': 'Mixed nuts and seeds'
                }
            },
            'created_at': get_ist_time().isoformat(),
            'updated_at': get_ist_time().isoformat(),
            'allergies': '',
            'dietary_preferences': '',
            'diseases': '',
            'medical_conditions': '',
            'role': 'admin'
        }
        
        print(f"Default admin user created:")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        print(f"   Role: admin")
        print(f"   User ID: {user_id}")
        return user_id
    else:
        print(f"Admin user {admin_email} already exists")
        return None

if __name__ == '__main__':
    # Create default admin user before starting server
    create_default_admin()
    
    print("\n" + "="*60)
    print("Starting OPTIMIZED Diet Recommendation System...")
    print("  FAST - Optimized for speed")
    print("  COMPLETE - Diet + Exercise + Water + Weekly Schedule + Reports + Compliance Tracking")
    print("\nAvailable endpoints:")
    print("  GET  /api/health - Health check")
    print("  POST /api/auth/register - User registration")
    print("  POST /api/auth/login - User login")
    print("  GET  /api/profile - Get user profile")
    print("  POST /api/save-profile - Save profile & get recommendations")
    print("  POST /api/bmi-calculator - Calculate BMI")
    print("  POST /api/water - Complete predefined water task (tick-based)")
    print("  GET  /api/water - Get water tasks for date")
    print("  POST /api/exercise - Complete predefined exercise task (tick-based)")
    print("  GET  /api/exercise - Get exercise tasks for date")
    print("  POST /api/diet-log - Log diet intake")
    print("  GET  /api/diet-log - Get diet logs")
    print("  GET  /api/personalized-plan - Get personalized exercise, water & reports")
    print("  GET  /api/daily-tasks - Get predefined daily tasks to complete")
    print("  POST /api/complete-task - Complete task with random encouragement + IMAGE")
    print("  GET  /api/achievement-reward - Get visual reward for achievement level")
    print("  GET  /api/weekly-reward - Get weekly visual reward based on progress")
    print("  GET  /api/user-activities - Get what user actually completed")
    print("  GET  /api/progress-report - Get detailed report of user activities")
    print("  GET  /api/calendar - Get monthly compliance calendar with encouragement")
    print("  GET  /api/calendar/day - Get detailed compliance for specific day")
    print("  GET  /api/compliance-report - Get compliance report with encouragement")
    print("  GET  /api/reports/summary - Get reports summary")
    print("\nFeatures:")
    print("  [OK] Personalized diet recommendations")
    print("  [OK] Predefined daily tasks with tick-to-complete system")
    print("  [OK] TICK-BASED water and exercise logging (no manual input)")
    print("  [OK] Random encouragement messages with emojis (never the same)")
    print("  [OK] GOAL-BASED IMAGE REWARDS (muscle growth, fat burning, balance)")
    print("  [OK] Visual motivation images that change based on user's goals")
    print("  [OK] Calendar tracking based on ticked tasks (not manual logs)")
    print("  [OK] Diet compliance checking")
    print("  [OK] Achievement and encouragement System")
    print("  [OK] Monthly compliance calendar with daily encouragement")
    print("  [OK] Streak tracking and progress visualization")
    print("  [OK] Progress reports showing what user actually completed")
    print("  [OK] Weekly reports and analytics")
    print("\nServer running on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
