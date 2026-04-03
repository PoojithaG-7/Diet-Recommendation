import React, { useState, useEffect, useCallback } from 'react';
import { Container, Row, Col, Card, Button, ProgressBar, Table, Alert, Badge } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ML_PER_GLASS = 250;

const Dashboard = () => {
  const { token, authFetch } = useAuth();
  const navigate = useNavigate();
  const [payload, setPayload] = useState(null);
  const [error, setError] = useState('');
  const [mealTotals, setMealTotals] = useState({ calories: 0, protein: 0, carbs: 0, fats: 0 });

  const load = useCallback(async () => {
    const res = await authFetch('/api/auth/profile');
    if (res.status === 401) {
      navigate('/login', { state: { from: { pathname: '/dashboard' } } });
      return;
    }
    const data = await res.json();
    if (!res.ok) {
      setError(data.error || 'Could not load dashboard');
      return;
    }
    
    // Simplified dashboard loading - remove diet plan gating
    setError('');
    setPayload(data);
    
    // Load today's meal totals
    loadMealTotals();
  }, [authFetch, navigate]);

  const loadMealTotals = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const res = await authFetch(`/api/diet-log?date=${today}`);
      if (res.ok) {
        const data = await res.json();
        const totals = (data.logs || []).reduce((acc, meal) => ({
          calories: acc.calories + (meal.calories || 0),
          protein: acc.protein + (meal.protein || 0),
          carbs: acc.carbs + (meal.carbs || 0),
          fats: acc.fats + (meal.fats || 0)
        }), { calories: 0, protein: 0, carbs: 0, fats: 0 });
        setMealTotals(totals);
      }
    } catch (err) {
      console.error('Failed to load meal totals:', err);
    }
  };

  useEffect(() => {
    if (!token) {
      navigate('/login', { state: { from: { pathname: '/dashboard' } } });
      return;
    }
    load();
  }, [token, navigate, load]);

  if (!payload) {
    return (
      <Container className="mt-4 py-5">
        {error ? <Alert variant="danger">{error}</Alert> : <p className="text-muted">Loading…</p>}
      </Container>
    );
  }

  const { user, profile, water_today_ml, water_goal_ml, recent_exercise } = payload;
  const displayName = user?.name || user?.email || 'User';
  
  // Check if user has filled diet plan
  const hasDietPlan = profile && profile.weight && profile.height;
  
  // Only show values if user has diet plan
  const bmi = hasDietPlan ? profile.bmi : null;
  const dailyCal = hasDietPlan ? profile.daily_calories_needed : null;
  
  // Only show water data if goals exist
  const waterGoalGlasses = water_goal_ml ? Math.round(water_goal_ml / ML_PER_GLASS) : null;
  const caloriesConsumed = mealTotals.calories;
  const proteinGoal = dailyCal ? Math.round((dailyCal * 0.3) / 4) : null;
  const carbsGoal = dailyCal ? Math.round((dailyCal * 0.4) / 4) : null;
  const fatsGoal = dailyCal ? Math.round((dailyCal * 0.3) / 9) : null;

  const getBMICategory = (val) => {
    if (val == null) return { category: '—', color: 'secondary' };
    if (val < 18.5) return { category: 'Underweight', color: 'info' };
    if (val < 25) return { category: 'Normal', color: 'success' };
    if (val < 30) return { category: 'Overweight', color: 'warning' };
    return { category: 'Obese', color: 'danger' };
  };

  const bmiInfo = getBMICategory(bmi);

  return (
    <div>
      <div className="dashboard-header">
        <Container>
          <h1 className="mb-0">Your Health Dashboard</h1>
          <p className="lead mb-0">Hi {displayName} — track nutrition and fitness</p>
        </Container>
      </div>

      <Container className="mt-4">
        {error && <Alert variant="danger">{error}</Alert>}

        <Alert variant="info" className="mb-4">
          <p className="mb-0">
            <strong>Welcome! To get started:</strong><br/>
            1. First, fill out your <strong>Diet Plan</strong> to set your weight, height, and goals<br/>
            2. Then you can track <strong>Water</strong> and <strong>Exercise</strong> with personalized targets<br/>
            3. Your <strong>BMI</strong> and <strong>Calorie targets</strong> will appear after completing your diet plan
          </p>
        </Alert>

        <Row className="mb-4">
          <Col md={3}>
            <Card className="stat-card">
              <Card.Body className="text-center">
                <h5 className="text-muted">Weight (profile)</h5>
                <h2>{hasDietPlan && profile?.weight ? `${profile.weight} kg` : '—'}</h2>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="stat-card">
              <Card.Body className="text-center">
                <h5 className="text-muted">BMI</h5>
                <h2>{bmi ?? '—'}</h2>
                {bmi && <Badge bg={bmiInfo.color}>{bmiInfo.category}</Badge>}
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="stat-card">
              <Card.Body className="text-center">
                <h5 className="text-muted">Calorie target</h5>
                <h2>{dailyCal ? Math.round(dailyCal) : '—'}</h2>
                {dailyCal && <small>kcal / day (from plan)</small>}
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="stat-card">
              <Card.Body className="text-center">
                <h5 className="text-muted">Water today</h5>
                <h2>{waterGoalGlasses ? (water_today_ml / ML_PER_GLASS).toFixed(1) : '—'}</h2>
                {waterGoalGlasses && <small>of {waterGoalGlasses} glasses</small>}
              </Card.Body>
            </Card>
          </Col>
        </Row>

        <Row className="mb-4">
          <Col md={6}>
            <Card>
              <Card.Header>
                <h5 className="mb-0">Daily goals (macros)</h5>
              </Card.Header>
              <Card.Body>
                {hasDietPlan ? (
                  <>
                    <div className="mb-3">
                      <div className="d-flex justify-content-between mb-1">
                        <span>Calories (logged meals)</span>
                        <span>
                          {caloriesConsumed} / {Math.round(dailyCal)}
                        </span>
                      </div>
                      <ProgressBar
                        now={dailyCal ? (caloriesConsumed / dailyCal) * 100 : 0}
                        variant="success"
                      />
                    </div>
                    <div className="mb-3">
                      <div className="d-flex justify-content-between mb-1">
                        <span>Protein</span>
                        <span>{mealTotals.protein.toFixed(1)}g / {proteinGoal}g</span>
                      </div>
                      <ProgressBar now={proteinGoal ? (mealTotals.protein / proteinGoal) * 100 : 0} variant="info" />
                    </div>
                    <div className="mb-3">
                      <div className="d-flex justify-content-between mb-1">
                        <span>Carbohydrates</span>
                        <span>{mealTotals.carbs.toFixed(1)}g / {carbsGoal}g</span>
                      </div>
                      <ProgressBar now={carbsGoal ? (mealTotals.carbs / carbsGoal) * 100 : 0} variant="warning" />
                    </div>
                    <div className="mb-3">
                      <div className="d-flex justify-content-between mb-1">
                        <span>Fats</span>
                        <span>{mealTotals.fats.toFixed(1)}g / {fatsGoal}g</span>
                      </div>
                      <ProgressBar now={fatsGoal ? (mealTotals.fats / fatsGoal) * 100 : 0} variant="danger" />
                    </div>
                    <div className="mb-1">
                      <div className="d-flex justify-content-between mb-1">
                        <span>Water</span>
                        <span>
                          {water_today_ml} ml / {water_goal_ml} ml
                        </span>
                      </div>
                      <ProgressBar
                        now={water_goal_ml ? Math.min(100, (water_today_ml / water_goal_ml) * 100) : 0}
                        variant="primary"
                      />
                    </div>
                  </>
                ) : (
                  <p className="text-muted mb-0">Please fill out your diet plan to see your personalized goals.</p>
                )}
              </Card.Body>
            </Card>
          </Col>
          <Col md={6}>
            <Card>
              <Card.Header>
                <h5 className="mb-0">Diet plan snapshot</h5>
              </Card.Header>
              <Card.Body>
                {hasDietPlan ? (
                  <>
                    <p>
                      <strong>Category:</strong> {profile.bmi_category ?? '—'}
                    </p>
                    <p>
                      <strong>Activity:</strong> {profile.activity_level ?? '—'}
                    </p>
                    <p>
                      <strong>Goal:</strong> {profile.goal ?? '—'}
                    </p>
                    {profile.dietary_notes ? (
                      <p className="small text-muted mb-0">
                        <strong>Needs / notes:</strong> {profile.dietary_notes}
                      </p>
                    ) : null}
                  </>
                ) : (
                  <p className="text-muted mb-0">No saved plan yet. Use Diet Plan while logged in.</p>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>

        <Row className="mb-4">
          <Col md={12}>
            <Card>
              <Card.Header>
                <h5 className="mb-0">Recent exercise</h5>
              </Card.Header>
              <Card.Body>
                {recent_exercise && recent_exercise.length > 0 ? (
                  <Table hover size="sm" className="mb-0">
                    <thead>
                      <tr>
                        <th>Activity</th>
                        <th>Minutes</th>
                        <th>Calories</th>
                        <th>When</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recent_exercise.map((row) => (
                        <tr key={row.id}>
                          <td>{row.activity_type}</td>
                          <td>{row.duration_minutes}</td>
                          <td>{row.calories_burned != null ? row.calories_burned : '—'}</td>
                          <td>{row.completed_at && row.completed_at !== 'Invalid Date' ? 
                            new Date(row.completed_at).toLocaleString('en-US', { 
                              hour: '2-digit', 
                              minute: '2-digit',
                              hour12: true 
                            }) : 'Just now'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                ) : (
                  <p className="text-muted mb-0">No sessions yet.</p>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>

        <Card className="mb-4">
          <Card.Header>
            <h5 className="mb-0">Quick actions</h5>
          </Card.Header>
          <Card.Body>
            <Row>
              <Col md={2} className="text-center mb-3">
                <LinkContainer to="/diet-form">
                  <Button variant="primary" className="w-100">
                    Update Diet Plan
                  </Button>
                </LinkContainer>
              </Col>
              <Col md={2} className="text-center mb-3">
                <LinkContainer to="/meals">
                  <Button variant="success" className="w-100">
                    Log Meals
                  </Button>
                </LinkContainer>
              </Col>
              <Col md={2} className="text-center mb-3">
                <LinkContainer to="/water">
                  <Button variant="info" className="w-100">
                    Log Water
                  </Button>
                </LinkContainer>
              </Col>
              <Col md={2} className="text-center mb-3">
                <LinkContainer to="/exercise">
                  <Button variant="warning" className="w-100">
                    Track Exercise
                  </Button>
                </LinkContainer>
              </Col>
              <Col md={2} className="text-center mb-3">
                <LinkContainer to="/reports">
                  <Button variant="secondary" className="w-100">
                    View Reports
                  </Button>
                </LinkContainer>
              </Col>
            </Row>
          </Card.Body>
        </Card>
      </Container>
    </div>
  );
};

export default Dashboard;
