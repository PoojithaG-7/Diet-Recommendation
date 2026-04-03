import random


class DietRecommendationSystem:
    """
    Rule-based diet recommendations by BMI category and personal metrics.
    """

    def __init__(self):
        self.bmi_diet_plans = {
            'underweight': {
                'description': 'High-calorie nutrient-dense foods for healthy weight gain',
                'target_calories': '2500-3000 calories per day',
                'breakfast': [
                    'Protein pancakes with banana and nuts (600 cal)',
                    'Avocado toast with eggs and cheese (550 cal)',
                    'Oatmeal with peanut butter, banana, and honey (580 cal)',
                    'Greek yogurt parfait with granola and fruits (520 cal)',
                ],
                'lunch': [
                    'Chicken and rice bowl with avocado (750 cal)',
                    'Pasta with creamy sauce and vegetables (700 cal)',
                    'Beef stir-fry with noodles (680 cal)',
                    'Tuna sandwich with chips and fruit (650 cal)',
                ],
                'dinner': [
                    'Salmon with sweet potato and vegetables (800 cal)',
                    'Steak with mashed potatoes and gravy (850 cal)',
                    'Chicken curry with rice (750 cal)',
                    'Pork chops with quinoa and roasted vegetables (780 cal)',
                ],
                'snacks': [
                    'Protein shake with banana and peanut butter (400 cal)',
                    'Trail mix with dried fruits and nuts (350 cal)',
                    'Cheese and crackers with apple (300 cal)',
                    'Whole milk smoothie with fruits (380 cal)',
                ],
            },
            'normal': {
                'description': 'Balanced nutrition for maintaining healthy weight',
                'target_calories': '1800-2200 calories per day',
                'breakfast': [
                    'Oatmeal with berries and almonds (400 cal)',
                    'Greek yogurt with granola and honey (350 cal)',
                    'Whole grain toast with avocado and egg (380 cal)',
                    'Protein smoothie with spinach and fruits (360 cal)',
                ],
                'lunch': [
                    'Grilled chicken salad with mixed greens (450 cal)',
                    'Quinoa bowl with roasted vegetables (420 cal)',
                    'Turkey wrap with hummus and vegetables (400 cal)',
                    'Lentil soup with whole grain bread (380 cal)',
                ],
                'dinner': [
                    'Baked salmon with steamed vegetables (500 cal)',
                    'Grilled chicken with roasted sweet potato (480 cal)',
                    'Vegetable stir-fry with tofu (420 cal)',
                    'Lean beef with brown rice and green beans (520 cal)',
                ],
                'snacks': [
                    'Apple with almond butter (200 cal)',
                    'Mixed nuts and seeds (180 cal)',
                    'Greek yogurt with berries (150 cal)',
                    'Carrot sticks with hummus (120 cal)',
                ],
            },
            'overweight': {
                'description': 'Lower-calorie nutrient-dense foods for healthy weight loss',
                'target_calories': '1200-1500 calories per day',
                'breakfast': [
                    'Oatmeal with cinnamon and apple slices (250 cal)',
                    'Greek yogurt with berries (180 cal)',
                    'Vegetable omelet with whole wheat toast (220 cal)',
                    'Green smoothie with protein powder (200 cal)',
                ],
                'lunch': [
                    'Large salad with grilled chicken (350 cal)',
                    'Vegetable soup with small bread roll (280 cal)',
                    'Quinoa salad with lemon dressing (320 cal)',
                    'Turkey lettuce wraps with vegetables (300 cal)',
                ],
                'dinner': [
                    'Grilled fish with steamed vegetables (350 cal)',
                    'Chicken breast with roasted vegetables (380 cal)',
                    'Large vegetable curry with minimal oil (320 cal)',
                    'Lean protein with large salad (340 cal)',
                ],
                'snacks': [
                    'Fresh fruit salad (80 cal)',
                    'Vegetable sticks with salsa (50 cal)',
                    'Herbal tea with small handful of nuts (100 cal)',
                    'Greek yogurt with cucumber (90 cal)',
                ],
            },
        }

        self.activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'veryActive': 1.9,
        }

    def calculate_bmi(self, weight, height):
        height_m = height / 100
        bmi = weight / (height_m ** 2)
        return round(bmi, 1)

    def categorize_bmi(self, bmi):
        if bmi < 18.5:
            return 'underweight'
        if bmi < 25:
            return 'normal'
        return 'overweight'

    def calculate_bmr(self, weight, height, age, gender):
        if gender.lower() == 'male':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        return round(bmr, 0)

    def calculate_daily_calories(self, weight, height, age, gender, activity_level):
        bmr = self.calculate_bmr(weight, height, age, gender)
        multiplier = self.activity_multipliers.get(activity_level, 1.2)
        return round(bmr * multiplier, 0)

    def get_dynamic_diet_plan(self, weight, height, age, gender, activity_level, goal=None):
        bmi = self.calculate_bmi(weight, height)
        bmi_category = self.categorize_bmi(bmi)
        daily_calories = self.calculate_daily_calories(weight, height, age, gender, activity_level)
        diet_plan = self.bmi_diet_plans[bmi_category].copy()
        personalized_meals = {}
        for meal_type in ['breakfast', 'lunch', 'dinner', 'snacks']:
            available_meals = diet_plan.get(meal_type, [])
            if available_meals:
                personalized_meals[meal_type] = random.choice(available_meals)

        # Exercise suggestions are generated alongside the diet so the app can
        # both recommend and track burned calories.
        exercise_recommendations, weekly_ex_cal = self._get_exercise_recommendations(
            weight_kg=weight,
            bmi_category=bmi_category,
            activity_level=activity_level,
            goal=goal,
        )

        return {
            'user_metrics': {
                'weight': weight,
                'height': height,
                'age': age,
                'gender': gender,
                'activity_level': activity_level,
                'bmi': bmi,
                'bmi_category': bmi_category.title(),
                'daily_calories_needed': daily_calories,
            },
            'diet_plan_info': {
                'category': bmi_category.title(),
                'description': diet_plan['description'],
                'target_calories': diet_plan['target_calories'],
            },
            'recommended_meals': personalized_meals,
            'health_tips': self._get_health_tips(bmi_category),
            'exercise_recommendations': exercise_recommendations,
            'estimated_weekly_calories_burned': weekly_ex_cal,
        }

    def _get_health_tips(self, bmi_category):
        tips = {
            'underweight': [
                'Eat frequent small meals throughout the day',
                'Include protein-rich foods in every meal',
                'Choose healthy calorie-dense foods like nuts and avocados',
                'Add strength training exercises to build muscle mass',
                'Stay hydrated but do not fill up on water before meals',
            ],
            'normal': [
                'Maintain a balanced diet with all food groups',
                'Exercise regularly for at least 30 minutes most days',
                'Get adequate sleep (7-9 hours per night)',
                'Practice portion control and mindful eating',
                'Include a variety of colorful fruits and vegetables',
            ],
            'overweight': [
                'Focus on portion control and mindful eating',
                'Include more vegetables and fiber in your diet',
                'Choose lean proteins and reduce processed foods',
                'Engage in regular cardiovascular exercise',
                'Set realistic weight loss goals (1-2 pounds per week)',
            ],
        }
        return tips.get(bmi_category, tips['normal'])

    def _estimate_calories_burned(self, *, met, weight_kg, duration_minutes):
        # Standard MET formula: kcal/min = MET * weight(kg) * 3.5 / 200
        # kcal for duration = kcal/min * minutes
        kcal = met * weight_kg * 3.5 / 200 * duration_minutes
        return int(round(kcal))

    def _distribute_sessions(self, total_sessions, n_items):
        # Evenly distribute sessions across n exercise entries.
        base = total_sessions // n_items
        extra = total_sessions % n_items
        sessions = []
        for i in range(n_items):
            sessions.append(base + (1 if i < extra else 0))
        return sessions

    def _get_exercise_recommendations(self, *, weight_kg, bmi_category, activity_level, goal=None):
        # MET values are approximate (general fitness ranges). This keeps estimates
        # consistent between recommendations and tracking when calories are missing.
        cardio_pool = [
            {'exercise_type': 'Brisk Walking', 'met': 3.5},
            {'exercise_type': 'Cycling', 'met': 6.8},
            {'exercise_type': 'Running', 'met': 9.8},
            {'exercise_type': 'Jump Rope', 'met': 10.0},
        ]
        strength_pool = [
            {'exercise_type': 'Squats', 'met': 5.0},
            {'exercise_type': 'Push-ups', 'met': 5.5},
            {'exercise_type': 'Lunges', 'met': 5.0},
            {'exercise_type': 'Resistance Band Rows', 'met': 4.8},
        ]
        flex_pool = [
            {'exercise_type': 'Yoga / Mobility', 'met': 2.5},
            {'exercise_type': 'Stretching', 'met': 1.8},
        ]

        # Choose base weekly targets from activity level.
        base_by_activity = {
            'sedentary': {'cardio_sessions': 2, 'strength_sessions': 2, 'flex_sessions': 3, 'cardio_minutes': 25, 'strength_minutes': 25, 'flex_minutes': 20},
            'light': {'cardio_sessions': 3, 'strength_sessions': 2, 'flex_sessions': 3, 'cardio_minutes': 30, 'strength_minutes': 30, 'flex_minutes': 20},
            'moderate': {'cardio_sessions': 4, 'strength_sessions': 3, 'flex_sessions': 3, 'cardio_minutes': 35, 'strength_minutes': 35, 'flex_minutes': 20},
            'active': {'cardio_sessions': 5, 'strength_sessions': 3, 'flex_sessions': 4, 'cardio_minutes': 40, 'strength_minutes': 40, 'flex_minutes': 25},
            'veryActive': {'cardio_sessions': 5, 'strength_sessions': 4, 'flex_sessions': 4, 'cardio_minutes': 45, 'strength_minutes': 45, 'flex_minutes': 25},
        }
        base = base_by_activity.get(activity_level, base_by_activity['sedentary'])

        cardio_sessions = base['cardio_sessions']
        strength_sessions = base['strength_sessions']
        flex_sessions = base['flex_sessions']

        # Goal adjustments (simple but effective).
        if goal == 'weightLoss':
            cardio_sessions += 1
            strength_sessions = max(1, strength_sessions - 1)
        elif goal == 'weightGain':
            strength_sessions += 1
            cardio_sessions = max(1, cardio_sessions - 1)
        elif goal == 'muscleGain':
            strength_sessions = max(strength_sessions, 3) + 1
            cardio_sessions = max(1, cardio_sessions - 1)
        # maintenance => no changes

        # BMI adjustments.
        if bmi_category == 'overweight':
            # Prefer lower-impact cardio.
            cardio_pool = [p for p in cardio_pool if p['exercise_type'] in ['Brisk Walking', 'Cycling']]
            flex_sessions = max(flex_sessions, 3)
        elif bmi_category == 'underweight':
            # Ensure strength emphasis for weight gain.
            strength_sessions = max(strength_sessions, 3)

        # Build category recommendations (2 cardio items, 2 strength items, 1 flex item).
        cardio_pick = random.sample(cardio_pool, k=min(2, len(cardio_pool)))
        strength_pick = random.sample(strength_pool, k=min(2, len(strength_pool)))
        flex_pick = [random.choice(flex_pool)]

        cardio_minutes = base['cardio_minutes']
        strength_minutes = base['strength_minutes']
        flex_minutes = base['flex_minutes']

        cardio_sessions_split = self._distribute_sessions(cardio_sessions, len(cardio_pick))
        strength_sessions_split = self._distribute_sessions(strength_sessions, len(strength_pick))
        flex_sessions_split = self._distribute_sessions(flex_sessions, len(flex_pick))

        cardio_recs = []
        weekly_total = 0
        for idx, item in enumerate(cardio_pick):
            est_per_session = self._estimate_calories_burned(
                met=item['met'], weight_kg=weight_kg, duration_minutes=cardio_minutes
            )
            est_week = est_per_session * cardio_sessions_split[idx]
            weekly_total += est_week
            cardio_recs.append(
                {
                    'exercise_type': item['exercise_type'],
                    'minutes_per_session': cardio_minutes,
                    'sessions_per_week': cardio_sessions_split[idx],
                    'estimated_calories_per_session': est_per_session,
                    'estimated_weekly_calories': est_week,
                }
            )

        strength_recs = []
        for idx, item in enumerate(strength_pick):
            est_per_session = self._estimate_calories_burned(
                met=item['met'], weight_kg=weight_kg, duration_minutes=strength_minutes
            )
            est_week = est_per_session * strength_sessions_split[idx]
            weekly_total += est_week
            strength_recs.append(
                {
                    'exercise_type': item['exercise_type'],
                    'minutes_per_session': strength_minutes,
                    'sessions_per_week': strength_sessions_split[idx],
                    'estimated_calories_per_session': est_per_session,
                    'estimated_weekly_calories': est_week,
                }
            )

        flexibility_recs = []
        for idx, item in enumerate(flex_pick):
            est_per_session = self._estimate_calories_burned(
                met=item['met'], weight_kg=weight_kg, duration_minutes=flex_minutes
            )
            est_week = est_per_session * flex_sessions_split[idx]
            weekly_total += est_week
            flexibility_recs.append(
                {
                    'exercise_type': item['exercise_type'],
                    'minutes_per_session': flex_minutes,
                    'sessions_per_week': flex_sessions_split[idx],
                    'estimated_calories_per_session': est_per_session,
                    'estimated_weekly_calories': est_week,
                }
            )

        return (
            {
                'cardio': cardio_recs,
                'strength': strength_recs,
                'flexibility': flexibility_recs,
            },
            weekly_total,
        )
