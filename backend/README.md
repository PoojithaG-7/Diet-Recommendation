# Diet Recommendation System - Backend API

A Flask-based REST API that provides personalized diet and exercise recommendations using rule-based logic.

## Features

- **BMI Calculator**: Calculate Body Mass Index and health status
- **Calorie Calculator**: Calculate daily calorie needs using Harris-Benedict equation
- **Diet Recommendations**: Personalized meal plans based on goals and dietary restrictions
- **Exercise Recommendations**: Customized workout plans based on fitness level and goals
- **Health Tips**: Goal-specific nutrition and fitness advice

## API Endpoints

### Health Check
```
GET /api/health
```
Returns API status

### Get Full Recommendations
```
POST /api/recommendations
```
Accepts user health data and returns comprehensive diet and exercise recommendations.

**Request Body:**
```json
{
  "weight": 70,
  "height": 170,
  "age": 25,
  "gender": "male",
  "activityLevel": "moderate",
  "goal": "weightLoss",
  "dietaryRestrictions": ["vegetarian"],
  "allergies": "nuts",
  "medicalConditions": ""
}
```

**Response:**
```json
{
  "user_metrics": {
    "bmi": 24.2,
    "bmi_category": "Normal",
    "bmi_status": "Maintain healthy weight",
    "daily_calories": 2000,
    "macronutrients": {
      "protein": 150,
      "carbs": 200,
      "fats": 67
    }
  },
  "diet_recommendations": {
    "breakfast": [...],
    "lunch": [...],
    "dinner": [...],
    "snacks": [...]
  },
  "exercise_recommendations": {
    "cardio": [...],
    "strength": [...],
    "flexibility": [...]
  },
  "health_tips": [...],
  "water_intake": "8.0 glasses per day",
  "sleep_recommendation": "7-9 hours per night"
}
```

### BMI Calculator
```
POST /api/bmi-calculator
```
Calculate BMI from weight and height.

### Calorie Calculator
```
POST /api/calorie-calculator
```
Calculate daily calorie needs.

## Rule-Based Logic

### BMI Categories
- Underweight: BMI < 18.5
- Normal: 18.5 ≤ BMI < 25
- Overweight: 25 ≤ BMI < 30
- Obese: BMI ≥ 30

### Activity Level Multipliers
- Sedentary: 1.2
- Lightly active: 1.375
- Moderately active: 1.55
- Very active: 1.725
- Extra active: 1.9

### Goal Adjustments
- Weight Loss: -500 calories from TDEE
- Weight Gain: +500 calories from TDEE
- Maintenance: TDEE (no adjustment)

### Macronutrient Distribution
- Protein: 30% of daily calories
- Carbohydrates: 40% of daily calories
- Fats: 30% of daily calories

### Dietary Restrictions Support
- Vegetarian: Replaces meat with plant-based alternatives
- Vegan: Removes all animal products
- Gluten-Free: Replaces gluten-containing foods
- Allergies: Removes common allergens (nuts, dairy, eggs, shellfish)

### Exercise Plan Adjustments
- Beginners: Reduced intensity and duration
- Advanced: Increased intensity and duration
- Goal-specific: Different focus for weight loss vs weight gain

## Authentication and database

The API uses **SQLite** (file `backend/instance/diet_app.db` by default) and **JWT** bearer tokens.

Set these environment variables for production:

- `SECRET_KEY` — Flask session signing (required for `/admin` login).
- `JWT_SECRET_KEY` — signing user access tokens (use a long random string).
- `ADMIN_SECRET` — shared key for the developer dashboard and `GET /api/admin/overview`.
- `ADMIN_ACTIVE_WINDOW_MINUTES` — optional; defaults to `15` (used to count “active” users by `last_activity`).

User access tokens are returned as `access_token` from `POST /api/auth/register` and `POST /api/auth/login`. Send `Authorization: Bearer <token>` on protected routes.

### Auth endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Body: `email`, `password`, optional `firstName`, `lastName`, `age`, `gender`, `phone` |
| POST | `/api/auth/login` | Body: `email`, `password` |

### Tracking (requires JWT)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/profile` | User, saved diet profile, today’s water total, recent exercise |
| POST | `/api/water` | Body: `amount_ml` **or** `glasses` (250 ml per glass) |
| GET | `/api/water` | Query `date=YYYY-MM-DD` (optional; default today UTC) |
| POST | `/api/exercise` | Body: `activity_type`, `duration_minutes`, optional `calories_burned` |
| GET | `/api/exercise` | Query optional `from`, `to` (`YYYY-MM-DD`) |
| GET | `/api/reports/summary` | Query `range=week` or `month` |

`POST /api/recommendations` works without a token; with `Authorization: Bearer …` it updates the user’s `UserProfile` (BMI category, calories, goal, notes).

## Developer admin (Flask-only)

1. Set `ADMIN_SECRET` in the environment.
2. Start the backend: `python app.py`
3. Open **http://localhost:5000/admin**
4. Enter the admin key once; the session unlocks the HTML dashboard (registered users, users active in the last N minutes, per-user diet category and needs).

JSON consumers can call:

`GET /api/admin/overview` with header `X-Admin-Key: <ADMIN_SECRET>`.

## Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Testing

Use curl or Postman to test the endpoints:

```bash
# Health check
curl http://localhost:5000/api/health

# Get recommendations
curl -X POST http://localhost:5000/api/recommendations \
  -H "Content-Type: application/json" \
  -d '{"weight":70,"height":170,"age":25,"gender":"male","activityLevel":"moderate","goal":"weightLoss"}'
```

## Integration with Frontend

The React frontend is configured to proxy requests to `http://localhost:5000`. Make sure both servers are running:

1. Start the Flask backend: `python app.py`
2. Start the React frontend: `npm start`

## Error Handling

The API includes comprehensive error handling:
- Validation for required fields
- Data type validation
- Graceful error responses with appropriate HTTP status codes

## Future Enhancements

- Machine learning-based recommendations
- User profile persistence
- Meal logging and tracking
- Progress analytics
- Integration with fitness trackers
- Recipe database integration
