# Food Database with Common Indian Foods and Their Nutritional Values
# Values are per 100g serving

FOOD_DATABASE = {
    # Indian Foods
    'rice': {
        'calories': 130,
        'protein': 2.7,
        'carbs': 28,
        'fats': 0.3
    },
    'chapati': {
        'calories': 104,
        'protein': 3.0,
        'carbs': 18.0,
        'fats': 1.5
    },
    'dal': {
        'calories': 116,
        'protein': 8.0,
        'carbs': 20.0,
        'fats': 0.5
    },
    'samosa': {
        'calories': 262,
        'protein': 4.0,
        'carbs': 24.0,
        'fats': 16.0
    },
    'paneer tikka': {
        'calories': 265,
        'protein': 18.0,
        'carbs': 8.0,
        'fats': 20.0
    },
    'butter chicken': {
        'calories': 238,
        'protein': 27.0,
        'carbs': 3.0,
        'fats': 14.0
    },
    'idli': {
        'calories': 112,
        'protein': 4.0,
        'carbs': 18.0,
        'fats': 3.0
    },
    'dosa': {
        'calories': 133,
        'protein': 2.6,
        'carbs': 25.0,
        'fats': 2.7
    },
    'sambhar': {
        'calories': 87,
        'protein': 2.5,
        'carbs': 13.0,
        'fats': 3.0
    },
    
    # Common Foods
    'chicken breast': {
        'calories': 165,
        'protein': 31.0,
        'carbs': 0.0,
        'fats': 3.6
    },
    'egg': {
        'calories': 155,
        'protein': 13.0,
        'carbs': 1.1,
        'fats': 11.0
    },
    'banana': {
        'calories': 89,
        'protein': 1.1,
        'carbs': 23.0,
        'fats': 0.3
    },
    'apple': {
        'calories': 52,
        'protein': 0.3,
        'carbs': 14.0,
        'fats': 0.2
    },
    'milk': {
        'calories': 42,
        'protein': 3.4,
        'carbs': 5.0,
        'fats': 1.0
    },
    'bread': {
        'calories': 265,
        'protein': 9.0,
        'carbs': 49.0,
        'fats': 3.2
    },
    'yogurt': {
        'calories': 59,
        'protein': 10.0,
        'carbs': 3.6,
        'fats': 0.4
    },
    'aloo paratha': {
        'calories': 208,
        'protein': 3.0,
        'carbs': 32.0,
        'fats': 8.0
    },
    'rajma': {
        'calories': 140,
        'protein': 9.0,
        'carbs': 20.0,
        'fats': 4.0
    },
    'vegetable curry': {
        'calories': 95,
        'protein': 3.0,
        'carbs': 12.0,
        'fats': 4.0
    },
    'salad': {
        'calories': 17,
        'protein': 1.4,
        'carbs': 3.0,
        'fats': 0.2
    },
    'orange': {
        'calories': 47,
        'protein': 0.9,
        'carbs': 12.0,
        'fats': 0.1
    },
    'tea': {
        'calories': 2,
        'protein': 0.0,
        'carbs': 0.5,
        'fats': 0.0
    },
    'coffee': {
        'calories': 1,
        'protein': 0.1,
        'carbs': 0.0,
        'fats': 0.0
    }
}

def get_food_nutrition(food_name, serving_size_grams=100):
    """Get nutritional information for a food item"""
    food_name_lower = food_name.lower().strip()
    
    # Try exact match first
    if food_name_lower in FOOD_DATABASE:
        food_data = FOOD_DATABASE[food_name_lower]
        multiplier = serving_size_grams / 100
        return {
            'calories': round(food_data['calories'] * multiplier),
            'protein': round(food_data['protein'] * multiplier, 1),
            'carbs': round(food_data['carbs'] * multiplier, 1),
            'fats': round(food_data['fats'] * multiplier, 1)
        }
    
    # Try partial match
    for food_key, food_data in FOOD_DATABASE.items():
        if food_name_lower in food_key or food_key in food_name_lower:
            multiplier = serving_size_grams / 100
            return {
                'calories': round(food_data['calories'] * multiplier),
                'protein': round(food_data['protein'] * multiplier, 1),
                'carbs': round(food_data['carbs'] * multiplier, 1),
                'fats': round(food_data['fats'] * multiplier, 1)
            }
    
    # Default if not found
    return {
        'calories': 0,
        'protein': 0.0,
        'carbs': 0.0,
        'fats': 0.0
    }

def search_foods(query):
    """Search for foods in database"""
    query_lower = query.lower().strip()
    matches = []
    
    for food_key in FOOD_DATABASE.keys():
        if query_lower in food_key or food_key in query_lower:
            matches.append(food_key)
    
    return matches[:5]  # Return top 5 matches
