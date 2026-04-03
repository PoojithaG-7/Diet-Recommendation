from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import random
import csv
import os
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)

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

@app.route('/api/profile', methods=['GET'])
def get_profile():
    return jsonify({
        'success': True,
        'user': {
            'name': 'Demo User',
            'email': 'demo@example.com',
            'age': 25,
            'weight': 70,
            'height': 170,
            'gender': 'male',
            'activity_level': 'moderate',
            'health_conditions': 'none'
        }
    })

@app.route('/api/save-profile', methods=['POST'])
def save_profile():
    """OPTIMIZED: Fast comprehensive plan generation"""
    try:
        data = request.get_json()
        
        # Fast data extraction
        weight = float(data.get('weight', 0))
        height = float(data.get('height', 0))
        age = int(data.get('age', 0))
        gender = data.get('gender', 'male')
        activity_level = data.get('activityLevel', data.get('activity_level', 'moderate'))
        health_conditions = data.get('health_conditions', data.get('medicalConditions', 'none'))
        
        # Fast validation
        if weight <= 0 or height <= 0 or age <= 0:
            return jsonify({'success': False, 'error': 'Invalid data. Height should be in cm (e.g., 170)'}), 400
        
        # FAST PATH: Get base recommendation
        base_recommendation = diet_system.get_diet_recommendation(
            weight, height, age, gender, activity_level, health_conditions
        )
        
        # FAST PATH: Generate comprehensive plan
        comprehensive_plan = diet_system._generate_comprehensive_plan(
            weight, height, age, gender, activity_level, health_conditions, base_recommendation
        )
        
        # ASYNC LOGGING (don't wait for admin dashboard)
        try:
            requests.post('http://localhost:5001/api/admin/log-activity', json={
                'email': data.get('email', 'user_profile'),
                'activity_type': 'diet_request',
                'details': f'BMI: {base_recommendation["user_metrics"]["bmi"]}, Category: {base_recommendation["user_metrics"]["bmi_category"]}, Conditions: {health_conditions}'
            }, timeout=0.5)
        except:
            pass
        
        return jsonify({'success': True, 'recommendation': comprehensive_plan})
        
    except ValueError as e:
        return jsonify({'success': False, 'error': f'Invalid data format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting OPTIMIZED Diet Recommendation System...")
    print("  FAST - Optimized for speed")
    print("  COMPLETE - Diet + Exercise + Water + Weekly Schedule")
    print("\nServer running on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
