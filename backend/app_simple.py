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
    """
    Simple diet recommendation system based on BMI and health conditions.
    Perfect for B.Tech final year project - clean, readable, and effective.
    """
    
    def __init__(self):
        """Initialize with simple diet plans for different BMI categories"""
        
        # Diet plans based on BMI categories
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
                    'Carrot sticks with hummus (120 cal)'
                ]
            },
            'overweight': {
                'goal': 'Healthy weight loss',
                'calories': '1200-1500 per day',
                'breakfast': [
                    'Oatmeal with cinnamon and apple slices (250 cal)',
                    'Greek yogurt with berries (180 cal)',
                    'Vegetable omelet with whole wheat toast (220 cal)',
                    'Green smoothie with protein powder (200 cal)'
                ],
                'lunch': [
                    'Large salad with grilled chicken (350 cal)',
                    'Vegetable soup with small bread roll (280 cal)',
                    'Quinoa salad with lemon dressing (320 cal)',
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
                    'Greek yogurt with cucumber (90 cal)'
                ]
            }
        }
        
        # Activity level multipliers for calorie calculation
        self.activity_multipliers = {
            'sedentary': 1.2,      # Little or no exercise
            'light': 1.375,        # Light exercise 1-3 days/week
            'moderate': 1.55,      # Moderate exercise 3-5 days/week
            'active': 1.725,       # Hard exercise 6-7 days/week
            'veryActive': 1.9      # Very hard exercise & physical job
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
            'heart_disease': {
                'avoid': ['saturated fats', 'fried foods', 'red meat', 'butter'],
                'prefer': ['omega-3 rich foods', 'lean proteins', 'whole grains', 'nuts'],
                'tips': ['Choose heart-healthy fats', 'Limit saturated fats', 'Eat more fish']
            },
            'none': {
                'avoid': [],
                'prefer': [],
                'tips': ['Maintain balanced diet', 'Stay hydrated', 'Exercise regularly']
            }
        }
    
    def calculate_bmi(self, weight_kg, height_cm):
        """Calculate BMI using standard formula"""
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        return round(bmi, 1)
    
    def get_bmi_category(self, bmi):
        """Categorize BMI into underweight, normal, or overweight"""
        if bmi < 18.5:
            return 'underweight'
        elif bmi < 25:
            return 'normal'
        else:
            return 'overweight'
    
    def calculate_daily_calories(self, weight_kg, height_cm, age, gender, activity_level):
        """Calculate daily calorie needs using Harris-Benedict equation"""
        # Calculate BMR (Basal Metabolic Rate)
        if gender.lower() == 'male':
            bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
        
        # Activity multipliers
        multiplier = self.activity_multipliers.get(activity_level, 1.2)
        daily_calories = bmr * multiplier
        
        return round(daily_calories, 0)
    
    def adjust_for_health_conditions(self, meal_plan, health_conditions):
        """Adjust meal plan based on health conditions"""
        if not health_conditions or health_conditions.lower() == 'none':
            return meal_plan, []
        
        conditions = [cond.strip().lower() for cond in health_conditions.split(',')]
        adjusted_plan = meal_plan.copy()
        health_tips = []
        
        for condition in conditions:
            if condition in self.health_adjustments:
                adjustment = self.health_adjustments[condition]
                
                # Add health tips
                health_tips.extend(adjustment['tips'])
                
                # Apply food preferences (simplified logic)
                for meal_type in adjusted_plan:
                    meals = adjusted_plan[meal_type]
                    adjusted_meals = []
                    
                    for meal in meals:
                        meal_lower = meal.lower()
                        should_avoid = any(avoid in meal_lower for avoid in adjustment['avoid'])
                        
                        if not should_avoid:
                            adjusted_meals.append(meal)
                        else:
                            # Replace with healthier alternative
                            if 'sugar' in meal_lower or 'honey' in meal_lower:
                                adjusted_meals.append(meal.replace('honey', 'stevia').replace('sugar', 'natural sweetener'))
                            elif 'salt' in meal_lower:
                                adjusted_meals.append(meal.replace('salt', 'herbs and spices'))
                            else:
                                adjusted_meals.append('Grilled vegetables with herbs (250 cal)')
                    
                    adjusted_plan[meal_type] = adjusted_meals if adjusted_meals else ['Fresh vegetable salad (200 cal)']
        
        return adjusted_plan, list(set(health_tips))  # Remove duplicate tips
    
    def get_diet_recommendation(self, weight_kg, height_cm, age, gender, activity_level, health_conditions='none'):
        """
        Main method to get diet recommendations
        
        Args:
            weight_kg (float): Weight in kilograms
            height_cm (float): Height in centimeters
            age (int): Age in years
            gender (str): 'male' or 'female'
            activity_level (str): Activity level
            health_conditions (str): Health conditions (comma separated)
            
        Returns:
            dict: Complete diet recommendation
        """
        # Calculate basic metrics
        bmi = self.calculate_bmi(weight_kg, height_cm)
        bmi_category = self.get_bmi_category(bmi)
        daily_calories = self.calculate_daily_calories(weight_kg, height_cm, age, gender, activity_level)
        
        # Get base diet plan for BMI category
        base_plan = self.diet_plans[bmi_category].copy()
        
        # Adjust for health conditions
        adjusted_plan, health_tips = self.adjust_for_health_conditions(base_plan, health_conditions)
        
        # Select random meals for variety
        recommended_meals = {}
        for meal_type in ['breakfast', 'lunch', 'dinner', 'snacks']:
            available_meals = adjusted_plan.get(meal_type, [])
            if available_meals:
                recommended_meals[meal_type] = random.choice(available_meals)
        
        # Generate general health tips
        general_tips = [
            'Drink at least 8 glasses of water per day',
            'Include a variety of colorful vegetables in your diet',
            'Choose whole grains over refined grains',
            'Practice portion control and mindful eating',
            'Get adequate sleep (7-9 hours per night)'
        ]
        
        # Combine all tips
        all_tips = general_tips + health_tips
        
        return {
            'user_profile': {
                'weight': weight_kg,
                'height': height_cm,
                'age': age,
                'gender': gender,
                'activity_level': activity_level,
                'health_conditions': health_conditions
            },
            'health_metrics': {
                'bmi': bmi,
                'bmi_category': bmi_category.title(),
                'daily_calorie_needs': daily_calories
            },
            'diet_plan': {
                'goal': base_plan['goal'],
                'target_calories': base_plan['calories'],
                'recommended_meals': recommended_meals
            },
            'health_tips': all_tips[:8],  # Limit to 8 tips for cleaner output
            'disclaimer': 'This is a general recommendation. Please consult with a healthcare professional for personalized advice.'
        }
    
    def _generate_comprehensive_plan(self, weight, height, age, gender, activity_level, health_conditions, diet_recommendation):
        """
        Generate comprehensive lifestyle plan including diet, exercise, and water intake
        """
        bmi = diet_recommendation.get('health_metrics', {}).get('bmi', 0)
        bmi_category = diet_recommendation.get('health_metrics', {}).get('bmi_category', 'normal')
        daily_calories = diet_recommendation.get('health_metrics', {}).get('daily_calorie_needs', 2000)
        
        # Exercise recommendations based on goals and activity level
        exercise_plan = self._get_exercise_plan(activity_level, bmi_category, health_conditions)
        
        # Water intake recommendations
        water_plan = self._get_water_plan(weight, activity_level, health_conditions)
        
        # Combine everything into comprehensive plan
        comprehensive_plan = diet_recommendation.copy()
        comprehensive_plan['exercise_plan'] = exercise_plan
        comprehensive_plan['water_plan'] = water_plan
        comprehensive_plan['weekly_schedule'] = self._get_weekly_schedule(diet_recommendation, exercise_plan)
        
        return comprehensive_plan
    
    def _get_exercise_plan(self, activity_level, bmi_category, health_conditions):
        """
        Generate personalized exercise recommendations
        """
        base_exercises = {
            'weight_loss': {
                'cardio': [
                    {'name': 'Brisk Walking', 'minutes': 30, 'sessions_per_week': 5, 'calories_per_session': 150},
                    {'name': 'Jogging', 'minutes': 25, 'sessions_per_week': 3, 'calories_per_session': 250},
                    {'name': 'Cycling', 'minutes': 45, 'sessions_per_week': 3, 'calories_per_session': 400}
                ],
                'strength': [
                    {'name': 'Bodyweight Squats', 'minutes': 20, 'sessions_per_week': 3, 'calories_per_session': 100},
                    {'name': 'Push-ups', 'minutes': 15, 'sessions_per_week': 3, 'calories_per_session': 80},
                    {'name': 'Lunges', 'minutes': 25, 'sessions_per_week': 2, 'calories_per_session': 120}
                ]
            },
            'weight_gain': {
                'cardio': [
                    {'name': 'Light Walking', 'minutes': 20, 'sessions_per_week': 5, 'calories_per_session': 80},
                    {'name': 'Swimming', 'minutes': 30, 'sessions_per_week': 3, 'calories_per_session': 200}
                ],
                'strength': [
                    {'name': 'Weight Training', 'minutes': 45, 'sessions_per_week': 4, 'calories_per_session': 250},
                    {'name': 'Deadlifts', 'minutes': 30, 'sessions_per_week': 3, 'calories_per_session': 200},
                    {'name': 'Pull-ups', 'minutes': 15, 'sessions_per_week': 3, 'calories_per_session': 100}
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
        
        # Adjust for health conditions
        if 'diabetes' in health_conditions.lower():
            # Lower intensity, longer duration
            for exercise_type in base_exercises.get('maintenance', {}):
                for exercise in base_exercises['maintenance'][exercise_type]:
                    exercise['minutes'] = int(exercise['minutes'] * 1.2)
                    exercise['calories_per_session'] = int(exercise['calories_per_session'] * 0.8)
        
        if 'hypertension' in health_conditions.lower():
            # Focus on low-impact exercises
            for exercise_type in base_exercises.get('maintenance', {}):
                for exercise in base_exercises['maintenance'][exercise_type]:
                    if 'Jumping' in exercise['name']:
                        exercise['minutes'] = int(exercise['minutes'] * 1.5)  # Reduce jumping time
                        exercise['calories_per_session'] = int(exercise['calories_per_session'] * 0.7)
        
        return base_exercises.get('weight_gain', base_exercises['maintenance'])
    
    def _get_water_plan(self, weight, activity_level, health_conditions):
        """
        Generate water intake recommendations
        """
        base_water_ml = weight * 35  # 35ml per kg
        
        # Adjust for activity level
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
        if 'diabetes' in health_conditions.lower():
            recommended_water_ml = int(recommended_water_ml * 0.9)  # Slightly less for diabetes
        
        water_glasses = round(recommended_water_ml / 250)  # 250ml per glass
        
        return {
            'recommended_ml': recommended_water_ml,
            'recommended_glasses': water_glasses,
            'schedule': [
                f'7:00 AM - {water_glasses//3} glasses ({(water_glasses//3)*250}ml)',
                f'11:00 AM - {water_glasses//3} glasses ({(water_glasses//3)*250}ml)',
                f'3:00 PM - {water_glasses//3} glasses ({(water_glasses//3)*250}ml)',
                f'7:00 PM - {max(1, water_glasses//3)} glasses ({max(1, water_glasses//3)*250}ml)'
            ]
        }
    
    def _get_weekly_schedule(self, diet_plan, exercise_plan):
        """
        Generate a weekly schedule combining diet and exercise
        """
        schedule = []
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day in days:
            day_plan = {
                'day': day,
                'meals': {
                    'breakfast': diet_plan.get('recommended_meals', {}).get('breakfast', 'Healthy breakfast'),
                    'lunch': diet_plan.get('recommended_meals', {}).get('lunch', 'Balanced lunch'),
                    'dinner': diet_plan.get('recommended_meals', {}).get('dinner', 'Nutritious dinner'),
                    'snacks': diet_plan.get('recommended_meals', {}).get('snacks', 'Healthy snacks')
                },
                'exercise': 'Rest day' if day in ['Saturday', 'Sunday'] else 'Exercise day',
                'water_intake': '8 glasses'
            }
            schedule.append(day_plan)
        
        return schedule

# Initialize the recommendation system
diet_system = SimpleDietRecommender()

class UserRegistration:
    """
    Simple user registration system using CSV file storage.
    Perfect for B.Tech project - no database required.
    """
    
    def __init__(self, csv_file='users.csv'):
        """Initialize with CSV file path"""
        self.csv_file = csv_file
        self.ensure_csv_file_exists()
    
    def ensure_csv_file_exists(self):
        """Create CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['id', 'name', 'email', 'password', 'registration_date'])
    
    def email_exists(self, email):
        """Check if email already exists in CSV file"""
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header row
                for row in reader:
                    if len(row) >= 3 and row[2].lower() == email.lower():
                        return True
            return False
        except Exception as e:
            print(f"Error checking email existence: {e}")
            return False
    
    def save_user(self, name, email, password):
        """Save new user to CSV file"""
        try:
            # Generate unique ID (timestamp based)
            user_id = datetime.now().strftime('%Y%m%d%H%M%S')
            registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([user_id, name, email, password, registration_date])
            
            return True
        except Exception as e:
            print(f"Error saving user: {e}")
            return False
    
    def get_all_users(self):
        """Get all users (for debugging purposes)"""
        try:
            users = []
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 5:
                        users.append({
                            'id': row[0],
                            'name': row[1],
                            'email': row[2],
                            'password': row[3],
                            'registration_date': row[4]
                        })
            return users
        except Exception as e:
            print(f"Error getting users: {e}")
            return []

# Initialize user registration system
user_reg = UserRegistration()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Simple Diet Recommendation API is running',
        'version': '1.0.0'
    })

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """
    Main endpoint for diet recommendations
    Expected JSON input:
    {
        "weight": 70,
        "height": 170,
        "age": 25,
        "gender": "male",
        "activityLevel": "moderate",
        "healthConditions": "none"  // optional, can be "diabetes", "hypertension", "heart_disease", or comma-separated
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['weight', 'height', 'age', 'gender', 'activityLevel']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Extract and validate data
        weight = float(data['weight'])
        height = float(data['height'])
        age = int(data['age'])
        gender = data['gender']
        activity_level = data['activityLevel']
        health_conditions = data.get('healthConditions', 'none')
        
        # Basic validation
        if weight <= 0 or height <= 0 or age <= 0:
            return jsonify({'error': 'Weight, height, and age must be positive numbers'}), 400
        
        if gender.lower() not in ['male', 'female']:
            return jsonify({'error': 'Gender must be either "male" or "female"'}), 400
        
        valid_activities = ['sedentary', 'light', 'moderate', 'active', 'veryActive']
        if activity_level not in valid_activities:
            return jsonify({'error': f'Invalid activity level. Choose from: {", ".join(valid_activities)}'}), 400
        
        # Get diet recommendation
        recommendation = diet_system.get_diet_recommendation(
            weight, height, age, gender, activity_level, health_conditions
        )
        
        # Log diet request to admin dashboard
        try:
            requests.post('http://localhost:5001/api/admin/log-activity', json={
                'email': f'user_{weight}_{height}',  # Anonymous user identification
                'activity_type': 'diet_request',
                'details': f'BMI: {recommendation["health_metrics"]["bmi"]}, Category: {recommendation["health_metrics"]["bmi_category"]}, Conditions: {health_conditions}'
            }, timeout=2)
            
            # Also log detailed diet request data
            requests.post('http://localhost:5001/api/admin/log-diet-request', json={
                'email': f'user_{weight}_{height}',
                'user_data': {
                    'weight': weight,
                    'height': height,
                    'age': age,
                    'gender': gender,
                    'activity_level': activity_level,
                    'health_conditions': health_conditions
                },
                'recommendation': recommendation
            }, timeout=2)
        except:
            pass  # Admin dashboard might not be running
        
        return jsonify(recommendation)
        
    except ValueError as e:
        return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/api/bmi-calculator', methods=['POST'])
def calculate_bmi():
    """Simple BMI calculator endpoint"""
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
            'interpretation': f'Your BMI of {bmi} indicates you are {category}'
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register_user():
    """
    User registration endpoint
    Expected JSON input:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Combine first and last name
        name = data['name'].strip()
        email = data['email'].strip()
        password = data['password'].strip()
        
        # Basic validation
        if not name or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        # Email format validation
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if email already exists
        if user_reg.email_exists(email):
            return jsonify({'error': 'Email already registered'}), 409
        
        # Save new user
        if user_reg.save_user(name, email, password):
            # Log registration to admin dashboard
            try:
                requests.post('http://localhost:5001/api/admin/log-activity', json={
                    'email': email,
                    'activity_type': 'registration',
                    'details': f'User {name} registered successfully'
                }, timeout=2)
            except:
                pass  # Admin dashboard might not be running
            
            return jsonify({
                'message': 'Registration successful',
                'user': {
                    'name': name,
                    'email': email
                }
            }), 201
        else:
            return jsonify({'error': 'Registration failed. Please try again.'}), 500
    
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    """
    Auth registration endpoint (compatible with React frontend)
    Expected JSON input:
    {
        "firstName": "Mounika",
        "lastName": "Choppa", 
        "email": "mounika@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Combine first and last name
        name = f"{data['firstName'].strip()} {data['lastName'].strip()}"
        email = data['email'].strip()
        password = data['password'].strip()
        
        # Basic validation
        if not name or not email or not password:
            return jsonify({
                'error': 'All fields are required'
            }), 400
        
        # Email format validation
        if '@' not in email or '.' not in email:
            return jsonify({
                'error': 'Invalid email format'
            }), 400
        
        # Check if email already exists
        if user_reg.email_exists(email):
            return jsonify({
                'error': 'Email already registered'
            }), 409
        
        # Save new user
        if user_reg.save_user(name, email, password):
            # Generate simple token (for demo purposes)
            access_token = f"token_{datetime.now().strftime('%Y%m%d%H%M%S')}_{email}"
            
            # Log registration to admin dashboard
            try:
                requests.post('http://localhost:5001/api/admin/log-activity', json={
                    'email': email,
                    'activity_type': 'registration',
                    'details': f'User {name} registered successfully'
                }, timeout=2)
            except:
                pass  # Admin dashboard might not be running
            
            return jsonify({
                'message': 'Registration successful',
                'access_token': access_token,
                'user': {
                    'name': name,
                    'email': email
                }
            }), 201
        else:
            return jsonify({
                'error': 'Registration failed. Please try again.'
            }), 500
    
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    """
    Simple login endpoint (for demo purposes - no real authentication)
    Expected JSON input:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.get_json()
        
        if 'email' not in data or 'password' not in data:
            return jsonify({
                'error': 'Email and password are required'
            }), 400
        
        email = data['email'].strip()
        password = data['password'].strip()
        
        # Check if user exists (simple validation)
        if not user_reg.email_exists(email):
            return jsonify({
                'error': 'User not found'
            }), 404
        
        # Generate simple token (for demo purposes)
        access_token = f"token_{datetime.now().strftime('%Y%m%d%H%M%S')}_{email}"
        
        # Log login attempt to admin dashboard
        try:
            requests.post('http://localhost:5001/api/admin/log-activity', json={
                'email': email,
                'activity_type': 'login',
                'details': 'User logged in successfully'
            }, timeout=2)
        except:
            pass  # Admin dashboard might not be running
        
        # Return success (in real app, you'd validate password)
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'email': email,
                'name': 'Registered User'  # You could fetch actual name
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Login failed: {str(e)}'
        }), 500

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """
    Get user profile endpoint (for React frontend)
    Returns mock user profile data
    """
    try:
        # For demo purposes, return a mock profile
        # In real app, you'd get this from token/session
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
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Profile fetch failed: {str(e)}'
        }), 500

@app.route('/api/save-profile', methods=['POST'])
def save_profile():
    """
    Save user profile endpoint (for React frontend)
    Saves user health data and returns diet recommendations
    """
    try:
        data = request.get_json()
        
        # Extract user data with multiple field name support
        weight = float(data.get('weight', 0))
        height = float(data.get('height', 0))
        age = int(data.get('age', 0))
        gender = data.get('gender', 'male')
        activity_level = data.get('activityLevel', data.get('activity_level', 'moderate'))
        goal = data.get('goal', 'maintenance')
        health_conditions = data.get('health_conditions', data.get('medicalConditions', 'none'))
        
        # Handle dietary restrictions
        dietary_restrictions = data.get('dietaryRestrictions', [])
        if isinstance(dietary_restrictions, str):
            dietary_restrictions = [dietary_restrictions] if dietary_restrictions else []
        
        # Get allergies
        allergies = data.get('allergies', '')
        
        # Validate data
        if weight <= 0 or height <= 0 or age <= 0:
            return jsonify({
                'success': False,
                'error': 'Invalid data provided. Height should be in cm (e.g., 170)'
            }), 400
        
        # Get diet recommendation
        recommendation = diet_system.get_diet_recommendation(
            weight, height, age, gender, activity_level, health_conditions
        )
        
        # Generate comprehensive lifestyle plan
        comprehensive_plan = diet_system._generate_comprehensive_plan(
            weight, height, age, gender, activity_level, health_conditions, recommendation
        )
        
        # Log diet request to admin dashboard
        try:
            requests.post('http://localhost:5001/api/admin/log-activity', json={
                'email': data.get('email', 'user_profile'),
                'activity_type': 'diet_request',
                'details': f'BMI: {recommendation["health_metrics"]["bmi"]}, Category: {recommendation["health_metrics"]["bmi_category"]}, Conditions: {health_conditions}'
            }, timeout=2)
            
            # Also log detailed diet request data
            requests.post('http://localhost:5001/api/admin/log-diet-request', json={
                'email': data.get('email', 'user_profile'),
                'user_data': {
                    'weight': weight,
                    'height': height,
                    'age': age,
                    'gender': gender,
                    'activity_level': activity_level,
                    'health_conditions': health_conditions
                },
                'recommendation': recommendation
            }, timeout=2)
        except:
            pass  # Admin dashboard might not be running
        
        return jsonify({
            'success': True,
            'recommendation': comprehensive_plan
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid data format: {str(e)}. Please check your height (should be in cm, e.g., 170)'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An unexpected error occurred: {str(e)}'
        }), 500

@app.route('/api/users', methods=['GET'])
def get_all_users():
    """Get all registered users (for debugging purposes)"""
    try:
        users = user_reg.get_all_users()
        return jsonify({
            'success': True,
            'users': users,
            'total_users': len(users)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving users: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("Starting Simple Diet Recommendation System...")
    print("Available endpoints:")
    print("  GET  /api/health - Health check")
    print("  POST /api/recommendations - Get diet recommendations")
    print("  POST /api/bmi-calculator - Calculate BMI")
    print("  POST /api/register - User registration")
    print("  POST /api/auth/register - Auth registration (React compatible)")
    print("  POST /api/auth/login - User login")
    print("  GET  /api/profile - Get user profile")
    print("  POST /api/save-profile - Save profile & get recommendations")
    print("  GET  /api/users - View all users (debug)")
    print("\nServer running on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
