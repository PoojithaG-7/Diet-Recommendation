import React, { useState } from 'react';
import { Container, Card, Form, Button, Row, Col, Alert, Table } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import { useAuth } from '../context/AuthContext';

const DietForm = () => {
  const { token } = useAuth();
  const [formData, setFormData] = useState({
    weight: '',
    height: '',
    age: '',
    gender: '',
    activityLevel: '',
    goal: '',
    dietaryRestrictions: [],
    allergies: '',
    mealsPerDay: '3',
    waterIntake: '8',
    sleepHours: '',
    medicalConditions: ''
  });
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (type === 'checkbox') {
      setFormData(prev => ({
        ...prev,
        dietaryRestrictions: checked 
          ? [...prev.dietaryRestrictions, value]
          : prev.dietaryRestrictions.filter(item => item !== value)
      }));
    } else {
      setFormData({
        ...formData,
        [name]: value
      });
    }
  };

  const buildNotes = () => {
    const parts = [];
    if (formData.dietaryRestrictions.length) {
      parts.push(`Restrictions: ${formData.dietaryRestrictions.join(', ')}`);
    }
    if (formData.allergies) {
      parts.push(`Allergies: ${formData.allergies}`);
    }
    if (formData.medicalConditions) {
      parts.push(`Medical: ${formData.medicalConditions}`);
    }
    if (formData.waterIntake) {
      parts.push(`Water goal (glasses/day): ${formData.waterIntake}`);
    }
    if (formData.sleepHours) {
      parts.push(`Sleep (h): ${formData.sleepHours}`);
    }
    return parts.join('\n');
  };

  const generateRecommendation = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!token) {
      setError('Please login to generate diet recommendations');
      setLoading(false);
      return;
    }

    try {
      const headers = { 'Content-Type': 'application/json' };
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
      const body = {
        weight: parseFloat(formData.weight),
        height: parseFloat(formData.height),
        age: parseInt(formData.age, 10),
        gender: formData.gender,
        activityLevel: formData.activityLevel,
        goal: formData.goal,
        dietaryNotes: buildNotes(),
        allergies: formData.allergies || undefined,
        medicalConditions: formData.medicalConditions || undefined,
        health_conditions: formData.medicalConditions || 'none', // Add this field
      };
      const res = await fetch('/api/save-profile', {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || 'Failed to generate recommendation.');
        return;
      }
      setRecommendation(data.recommendation || data); // Handle both response formats
    } catch {
      setError('Failed to generate recommendation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const macrosFromCalories = (cals) => {
    const dailyCalories = Math.round(cals);
    return {
      dailyCalories,
      protein: Math.round(dailyCalories * 0.3 / 4),
      carbs: Math.round(dailyCalories * 0.4 / 4),
      fats: Math.round(dailyCalories * 0.3 / 9),
    };
  };

  return (
    <Container className="diet-form-container">
      <h2 className="text-center mb-4">Complete Your Diet Plan</h2>
      
      <Alert variant="info" className="mb-4">
        <h5 className="alert-heading">Welcome! Let's get started 🎯</h5>
        <p className="mb-2">
          <strong>Step 1:</strong> Fill out your health information below<br/>
          <strong>Step 2:</strong> Get your personalized diet recommendations<br/>
          <strong>Step 3:</strong> View your updated Dashboard with real data
        </p>
        <hr />
        <p className="mb-0 text-muted">
          Your BMI, calorie targets, and water goals will be calculated based on your input.
        </p>
      </Alert>
      
      <Card className="mb-4">
        <Card.Body>
          <Form onSubmit={generateRecommendation}>
            <Row>
              <Col md={3}>
                <Form.Group className="mb-3">
                  <Form.Label>Weight (kg)</Form.Label>
                  <Form.Control
                    type="number"
                    name="weight"
                    value={formData.weight}
                    onChange={handleChange}
                    placeholder="Enter weight"
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group className="mb-3">
                  <Form.Label>Height (cm)</Form.Label>
                  <Form.Control
                    type="number"
                    name="height"
                    value={formData.height}
                    onChange={handleChange}
                    placeholder="Enter height"
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group className="mb-3">
                  <Form.Label>Age</Form.Label>
                  <Form.Control
                    type="number"
                    name="age"
                    value={formData.age}
                    onChange={handleChange}
                    placeholder="Enter age"
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group className="mb-3">
                  <Form.Label>Gender</Form.Label>
                  <Form.Select
                    name="gender"
                    value={formData.gender}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Activity Level</Form.Label>
                  <Form.Select
                    name="activityLevel"
                    value={formData.activityLevel}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select activity level</option>
                    <option value="sedentary">Sedentary (little or no exercise)</option>
                    <option value="light">Lightly active (1-3 days/week)</option>
                    <option value="moderate">Moderately active (3-5 days/week)</option>
                    <option value="active">Very active (6-7 days/week)</option>
                    <option value="veryActive">Extra active (very hard exercise)</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Health Goal</Form.Label>
                  <Form.Select
                    name="goal"
                    value={formData.goal}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select your goal</option>
                    <option value="weightLoss">Weight Loss</option>
                    <option value="maintenance">Maintain Weight</option>
                    <option value="weightGain">Weight Gain</option>
                    <option value="muscleGain">Muscle Gain</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Dietary Restrictions</Form.Label>
              <div>
                {['vegetarian', 'vegan', 'glutenFree', 'dairyFree', 'keto', 'paleo'].map(restriction => (
                  <Form.Check
                    key={restriction}
                    type="checkbox"
                    label={restriction.charAt(0).toUpperCase() + restriction.slice(1).replace(/([A-Z])/g, ' $1')}
                    name="dietaryRestrictions"
                    value={restriction}
                    checked={formData.dietaryRestrictions.includes(restriction)}
                    onChange={handleChange}
                    inline
                  />
                ))}
              </div>
            </Form.Group>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Allergies (if any)</Form.Label>
                  <Form.Control
                    type="text"
                    name="allergies"
                    value={formData.allergies}
                    onChange={handleChange}
                    placeholder="e.g., nuts, shellfish, etc."
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Medical Conditions</Form.Label>
                  <Form.Control
                    type="text"
                    name="medicalConditions"
                    value={formData.medicalConditions}
                    onChange={handleChange}
                    placeholder="e.g., diabetes, hypertension, etc."
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Meals Per Day</Form.Label>
                  <Form.Select
                    name="mealsPerDay"
                    value={formData.mealsPerDay}
                    onChange={handleChange}
                  >
                    <option value="3">3 meals</option>
                    <option value="4">4 meals</option>
                    <option value="5">5 meals</option>
                    <option value="6">6 meals</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Water Intake (glasses/day)</Form.Label>
                  <Form.Control
                    type="number"
                    name="waterIntake"
                    value={formData.waterIntake}
                    onChange={handleChange}
                    min="1"
                    max="20"
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Sleep Hours</Form.Label>
                  <Form.Control
                    type="number"
                    name="sleepHours"
                    value={formData.sleepHours}
                    onChange={handleChange}
                    placeholder="Hours per night"
                    min="1"
                    max="24"
                  />
                </Form.Group>
              </Col>
            </Row>

            {error && <Alert variant="danger">{error}</Alert>}

            <Button
              variant="primary"
              type="submit"
              className="w-100"
              disabled={loading}
            >
              {loading ? 'Generating Recommendation...' : 'Get Diet Recommendation'}
            </Button>
          </Form>
        </Card.Body>
      </Card>

      {recommendation && (recommendation.user_metrics || recommendation.health_metrics) && (
        <Card className="recommendation-card">
          <Card.Body>
            <h3 className="mb-4">Your Personalized Diet Recommendation</h3>
            {!token && (
              <Alert variant="warning">
                Sign in to save this plan to your profile and use the dashboard.
              </Alert>
            )}
            <Row className="mb-4">
              <Col md={3}>
                <div className="text-center">
                  <h5>BMI</h5>
                  <h2>{recommendation.user_metrics?.bmi || recommendation.health_metrics?.bmi}</h2>
                  <small>{recommendation.user_metrics?.bmi_category || recommendation.health_metrics?.bmi_category}</small>
                </div>
              </Col>
              <Col md={3}>
                <div className="text-center">
                  <h5>Daily Calories</h5>
                  <h2>{Math.round(recommendation.user_metrics?.daily_calorie_needs || recommendation.health_metrics?.daily_calorie_needs)}</h2>
                </div>
              </Col>
              {(() => {
                const calories = recommendation.user_metrics?.daily_calorie_needs || recommendation.health_metrics?.daily_calorie_needs;
                const m = macrosFromCalories(calories);
                return (
                  <>
                    <Col md={2}>
                      <div className="text-center">
                        <h5>Protein (g)</h5>
                        <h2>{m.protein}</h2>
                      </div>
                    </Col>
                    <Col md={2}>
                      <div className="text-center">
                        <h5>Carbs (g)</h5>
                        <h2>{m.carbs}</h2>
                      </div>
                    </Col>
                    <Col md={2}>
                      <div className="text-center">
                        <h5>Fats (g)</h5>
                        <h2>{m.fats}</h2>
                      </div>
                    </Col>
                  </>
                );
              })()}
            </Row>

            {recommendation.diet_plan_info && (
              <p className="text-muted">
                Goal: {recommendation.diet_plan_info.goal} — {recommendation.diet_plan_info.target_calories}
              </p>
            )}

            <h4 className="mb-3">Today&apos;s suggested meals</h4>
            <Row>
              {recommendation.recommended_meals &&
                Object.entries(recommendation.recommended_meals).map(([meal, text]) => (
                  <Col md={6} key={meal} className="mb-3">
                    <h6 className="text-capitalize">{meal}</h6>
                    <p className="mb-0">{text}</p>
                  </Col>
                ))}
            </Row>

            <h4 className="mb-3 mt-4">Health Tips</h4>
            <ul>
              {(recommendation.health_tips || []).map((tip, index) => (
                <li key={index}>{tip}</li>
              ))}
            </ul>

            {/* Exercise Plan */}
            {recommendation.exercise_plan && (
              <>
                <h4 className="mb-3 mt-4">Exercise Plan</h4>
                <Row>
                  {Object.entries(recommendation.exercise_plan).map(([category, exercises]) => (
                    <Col md={6} key={category} className="mb-4">
                      <h6 className="text-capitalize">{category} Exercises</h6>
                      {exercises.map((exercise, idx) => (
                        <div key={idx} className="mb-2">
                          <strong>{exercise.name}</strong> - {exercise.minutes} min, {exercise.sessions_per_week} sessions/week, {exercise.calories_per_session} cal/session
                        </div>
                      ))}
                    </Col>
                  ))}
                </Row>
              </>
            )}

            {/* Water Plan */}
            {recommendation.water_plan && (
              <>
                <h4 className="mb-3 mt-4">Water Intake Plan</h4>
                <p><strong>Recommended:</strong> {recommendation.water_plan.recommended_glasses} glasses ({recommendation.water_plan.recommended_ml}ml) per day</p>
                <h6>Daily Schedule:</h6>
                <ul>
                  {recommendation.water_plan.schedule.map((schedule, index) => (
                    <li key={index}>{schedule}</li>
                  ))}
                </ul>
              </>
            )}

            {recommendation.exercise_recommendations && (
              <>
                <h4 className="mb-3 mt-4">Exercise Recommendations</h4>
                {recommendation.estimated_weekly_calories_burned != null && (
                  <p className="text-muted mb-3">
                    Estimated weekly calories burned: {recommendation.estimated_weekly_calories_burned} kcal
                  </p>
                )}

                {['cardio', 'strength', 'flexibility'].map((category) => {
                  const rows = recommendation.exercise_recommendations?.[category] || [];
                  if (!rows.length) return null;
                  const label = category.charAt(0).toUpperCase() + category.slice(1);
                  return (
                    <Card className="mb-3" key={category}>
                      <Card.Header>{label}</Card.Header>
                      <Card.Body style={{ padding: 0 }}>
                        <Table size="sm" responsive className="mb-0">
                          <thead>
                            <tr>
                              <th>Exercise</th>
                              <th>Minutes / session</th>
                              <th>Sessions / week</th>
                              <th>Est. kcal / session</th>
                              <th>Est. kcal / week</th>
                            </tr>
                          </thead>
                          <tbody>
                            {rows.map((r, idx) => (
                              <tr key={idx}>
                                <td>{r.exercise_type}</td>
                                <td>{r.minutes_per_session}</td>
                                <td>{r.sessions_per_week}</td>
                                <td>{r.estimated_calories_per_session}</td>
                                <td>{r.estimated_weekly_calories}</td>
                              </tr>
                            ))}
                          </tbody>
                        </Table>
                      </Card.Body>
                    </Card>
                  );
                })}
              </>
            )}

            {recommendation && (
              <Alert variant="success" className="mt-4">
                <h5 className="alert-heading">🎉 Diet Plan Created Successfully!</h5>
                <p className="mb-2">
                  Your personalized diet plan is ready! Your BMI and calorie targets have been calculated.
                </p>
                <p className="mb-0">
                  <strong>Next step:</strong> Click "View Dashboard" below to see your updated health metrics and start tracking your progress.
                </p>
              </Alert>
            )}

            <div className="text-center mt-4">
              {recommendation ? (
                <LinkContainer to="/dashboard">
                  <Button variant="success" size="lg">
                    📊 View Your Dashboard
                  </Button>
                </LinkContainer>
              ) : (
                <Button variant="primary" type="submit" disabled={loading}>
                  {loading ? 'Generating...' : 'Generate Diet Plan'}
                </Button>
              )}
            </div>
          </Card.Body>
        </Card>
      )}
    </Container>
  );
};

export default DietForm;
