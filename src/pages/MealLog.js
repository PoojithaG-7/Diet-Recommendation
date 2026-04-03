import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Table } from 'react-bootstrap';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

// Import food database for displaying nutrition info
const FOOD_DATABASE = {
  'rice': { calories: 130, protein: 2.7, carbs: 28, fats: 0.3 },
  'chapati': { calories: 104, protein: 3.0, carbs: 18.0, fats: 1.5 },
  'dal': { calories: 116, protein: 8.0, carbs: 20.0, fats: 0.5 },
  'samosa': { calories: 262, protein: 4.0, carbs: 24.0, fats: 16.0 },
  'paneer tikka': { calories: 265, protein: 18.0, carbs: 8.0, fats: 20.0 },
  'butter chicken': { calories: 238, protein: 27.0, carbs: 3.0, fats: 14.0 },
  'idli': { calories: 112, protein: 4.0, carbs: 18.0, fats: 3.0 },
  'dosa': { calories: 133, protein: 2.6, carbs: 25.0, fats: 2.7 },
  'sambhar': { calories: 87, protein: 2.5, carbs: 13.0, fats: 3.0 },
  'chicken breast': { calories: 165, protein: 31.0, carbs: 0.0, fats: 3.6 },
  'egg': { calories: 155, protein: 13.0, carbs: 1.1, fats: 11.0 },
  'banana': { calories: 89, protein: 1.1, carbs: 23.0, fats: 0.3 },
  'apple': { calories: 52, protein: 0.3, carbs: 14.0, fats: 0.2 },
  'milk': { calories: 42, protein: 3.4, carbs: 5.0, fats: 1.0 },
  'bread': { calories: 265, protein: 9.0, carbs: 49.0, fats: 3.2 },
  'yogurt': { calories: 59, protein: 10.0, carbs: 3.6, fats: 0.4 },
  'aloo paratha': { calories: 208, protein: 3.0, carbs: 32.0, fats: 8.0 },
  'rajma': { calories: 140, protein: 9.0, carbs: 20.0, fats: 4.0 },
  'vegetable curry': { calories: 95, protein: 3.0, carbs: 12.0, fats: 4.0 },
  'salad': { calories: 17, protein: 1.4, carbs: 3.0, fats: 0.2 },
  'orange': { calories: 47, protein: 0.9, carbs: 12.0, fats: 0.1 },
  'tea': { calories: 2, protein: 0.0, carbs: 0.5, fats: 0.0 },
  'coffee': { calories: 1, protein: 0.1, carbs: 0.0, fats: 0.0 }
};

const MealLog = () => {
  const { token, authFetch } = useAuth();
  const navigate = useNavigate();
  const [meals, setMeals] = useState([]);
  const [formData, setFormData] = useState({
    meal_type: 'breakfast',
    food_name: '',
    serving_size: 100,
    calories: '',
    protein: '',
    carbs: '',
    fats: ''
  });
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [hasDietPlan, setHasDietPlan] = useState(false);

  // Simplified - remove diet plan gating for smooth operation
  useEffect(() => {
    // Just load meals without diet plan checks
  }, []);

  const mealTypes = ['breakfast', 'lunch', 'dinner', 'snack'];

  useEffect(() => {
    loadTodayMeals();
  }, []);

  const searchFoods = async (query) => {
    if (!query || query.length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    try {
      const res = await authFetch(`/api/foods/search?q=${encodeURIComponent(query)}`);
      if (res.ok) {
        const data = await res.json();
        setSuggestions(data.foods || []);
        setShowSuggestions(true);
      }
    } catch (err) {
      console.error('Failed to search foods:', err);
    }
  };

  const calculateNutrition = async (foodName, servingSize) => {
    try {
      const res = await authFetch(`/api/foods/nutrition?food=${encodeURIComponent(foodName)}&serving=${servingSize}`);
      if (res.ok) {
        const data = await res.json();
        const nutrition = data.nutrition;
        
        setFormData(prev => ({
          ...prev,
          calories: nutrition.calories,
          protein: nutrition.protein,
          carbs: nutrition.carbs,
          fats: nutrition.fats
        }));
      }
    } catch (err) {
      console.error('Error calculating nutrition:', err);
    }
  };

  const selectFood = async (food) => {
    console.log('selectFood called with:', food);
    try {
      const res = await authFetch(`/api/foods/nutrition?food=${encodeURIComponent(food)}&serving=${formData.serving_size}`);
      if (res.ok) {
        const data = await res.json();
        const nutrition = data.nutrition;
        console.log('Nutrition data received:', nutrition);
        
        setFormData({
          ...formData,
          food_name: food,
          calories: nutrition.calories,
          protein: nutrition.protein,
          carbs: nutrition.carbs,
          fats: nutrition.fats
        });
        setShowSuggestions(false);
        setSuggestions([]);
        console.log('Form data updated:', {
          food_name: food,
          calories: nutrition.calories,
          protein: nutrition.protein,
          carbs: nutrition.carbs,
          fats: nutrition.fats
        });
      } else {
        console.error('Failed to get nutrition:', res.status);
        // Still set the food name even if nutrition fails
        setFormData({
          ...formData,
          food_name: food
        });
        setShowSuggestions(false);
        setSuggestions([]);
      }
    } catch (err) {
      console.error('Error selecting food:', err);
      // Still set the food name even if there's an error
      setFormData({
        ...formData,
        food_name: food
      });
      setShowSuggestions(false);
      setSuggestions([]);
    }
  };

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showSuggestions && !event.target.closest('.position-relative')) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showSuggestions]);

  const loadTodayMeals = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      console.log('Loading meals for date:', today);
      const res = await authFetch(`/api/diet-log?date=${today}`);
      console.log('Meals response status:', res.status);
      if (res.ok) {
        const data = await res.json();
        console.log('Meals data received:', data);
        setMeals(data.meals || []);
        console.log('Meals set:', data.meals || []);
      } else {
        console.log('Failed to load meals:', res.status);
      }
    } catch (err) {
      console.error('Failed to load meals:', err);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    
    // Trigger food search when food name changes
    if (name === 'food_name') {
      searchFoods(value);
    }
    
    // Recalculate nutrition when serving size changes and food is selected
    if (name === 'serving_size' && formData.food_name) {
      calculateNutrition(formData.food_name, value);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const mealData = {
        ...formData,
        calories: parseInt(formData.calories) || 0,
        protein: parseFloat(formData.protein) || 0,
        carbs: parseFloat(formData.carbs) || 0,
        fats: parseFloat(formData.fats) || 0,
        date: new Date().toISOString().split('T')[0]
      };

      const res = await authFetch('/api/diet-log', {
        method: 'POST',
        body: mealData
      });

      if (res.ok) {
        console.log('Meal logged successfully:', res);
        setFormData({
          meal_type: 'breakfast',
          food_name: '',
          serving_size: 100,
          calories: '',
          protein: '',
          carbs: '',
          fats: ''
        });
        loadTodayMeals();
      } else {
        const data = await res.json();
        setError(data.error || 'Failed to log meal');
      }
    } catch (err) {
      setError('Failed to log meal. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getTotalNutrients = () => {
    return meals.reduce((totals, meal) => ({
      calories: totals.calories + (meal.calories || 0),
      protein: totals.protein + (meal.protein || 0),
      carbs: totals.carbs + (meal.carbs || 0),
      fats: totals.fats + (meal.fats || 0)
    }), { calories: 0, protein: 0, carbs: 0, fats: 0 });
  };

  const deleteMeal = async (mealId) => {
    if (!window.confirm('Are you sure you want to delete this meal?')) {
      return;
    }
    
    try {
      const res = await authFetch(`/api/diet-log/${mealId}`, {
        method: 'DELETE'
      });
      
      if (res.ok) {
        loadTodayMeals(); // Reload meals after deletion
      } else {
        const data = await res.json();
        setError(data.error || 'Failed to delete meal');
      }
    } catch (err) {
      setError('Failed to delete meal. Please try again.');
    }
  };

  const searchMeals = (searchTerm) => {
    if (!searchTerm) {
      loadTodayMeals(); // Load all meals if search is empty
      return;
    }
    
    // Filter meals based on search term
    const filtered = meals.filter(meal => 
      meal.food_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      meal.meal_type.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setMeals(filtered);
  };

  const handleSearchChange = (e) => {
    const searchTerm = e.target.value;
    searchMeals(searchTerm);
  };

  const totals = getTotalNutrients();

  return (
    <Container className="mt-4">
      <h2 className="mb-4">Smart Meal Logging</h2>
      
      <Alert variant="info" className="mb-4">
        <h6 className="alert-heading">🍽️ Auto-Calculate Nutrition!</h6>
        <p className="mb-2">
          <strong>Simply type a food name</strong> (e.g., "rice", "chicken", "apple")<br/>
          <strong>Select from suggestions</strong> to auto-fill calories, protein, carbs, fats<br/>
          <strong>Adjust serving size</strong> if needed (default: 100g)
        </p>
        <hr />
        <p className="mb-0 text-muted small">
          Database includes Indian foods like chapati, dal, samosa, paneer tikka, idli, dosa, and common foods.
        </p>
      </Alert>
      
      <Row>
        <Col md={4}>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Log Your Meal</h5>
            </Card.Header>
            <Card.Body>
              <Alert variant="info" className="mb-3">
              <strong>🍽️ How to log your meal:</strong><br/>
              1. Type food name (e.g., "rice", "chicken", "apple")<br/>
              2. Select from suggestions or enter custom food<br/>
              3. Adjust serving size (nutrition auto-calculates)<br/>
              4. Click "Log Meal" to save
            </Alert>
            
            {error && <Alert variant="danger">{error}</Alert>}
      
      {!hasDietPlan && (
        <Alert variant="warning" className="mb-3">
          <strong>Please complete your diet plan first to access meal logging.</strong><br/>
          Go to <a href="/diet-form" style={{textDecoration: 'none'}}>Diet Plan</a> to set up your personalized meal recommendations.
        </Alert>
      )}
              
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>Meal Type</Form.Label>
                  <Form.Select name="meal_type" value={formData.meal_type} onChange={handleChange}>
                    {mealTypes.map(type => (
                      <option key={type} value={type}>
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Food Name</Form.Label>
                  <div className="position-relative">
                    <Form.Control
                      type="text"
                      name="food_name"
                      value={formData.food_name}
                      onChange={handleChange}
                      placeholder="e.g., Rice, Chicken, Apple"
                      required
                      autoComplete="off"
                    />
                    {showSuggestions && suggestions.length > 0 && (
                      <div className="position-absolute w-100 bg-white border rounded mt-1 shadow" 
                           style={{ zIndex: 1000, maxHeight: '200px', overflowY: 'auto', cursor: 'pointer' }}>
                        {suggestions.map((food, index) => {
                          const foodName = typeof food === 'string' ? food : food.name;
                          return (
                          <div
                            key={index}
                            className="p-2 border-bottom hover:bg-light"
                            onClick={() => {
                              console.log('Food clicked:', foodName);
                              selectFood(foodName);
                            }}
                            onMouseDown={(e) => e.preventDefault()}
                            style={{ 
                              cursor: 'pointer',
                              backgroundColor: formData.food_name.toLowerCase() === foodName.toLowerCase() ? '#f8f9fa' : 'transparent'
                            }}
                          >
                            <strong>{foodName.charAt(0).toUpperCase() + foodName.slice(1)}</strong>
                            <small className="text-muted d-block">
                              {typeof food === 'object' && food.calories ? 
                                `${food.calories} cal per 100g` : 
                                FOOD_DATABASE[foodName.toLowerCase()] ? 
                                  `${FOOD_DATABASE[foodName.toLowerCase()].calories} cal per 100g` : 
                                  'Custom food'
                              }
                            </small>
                          </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </Form.Group>

                <Row>
                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>Serving Size (g)</Form.Label>
                      <Form.Control
                        type="number"
                        name="serving_size"
                        value={formData.serving_size}
                        onChange={handleChange}
                        placeholder="100"
                        min="1"
                        max="1000"
                      />
                    </Form.Group>
                  </Col>
                  <Col md={2}>
                    <Form.Group className="mb-3">
                      <Form.Label>Calories <span className="text-muted">(auto)</span></Form.Label>
                      <Form.Control
                        type="number"
                        name="calories"
                        value={formData.calories}
                        onChange={handleChange}
                        placeholder="Auto-calculated"
                        readOnly
                        style={{ backgroundColor: '#f8f9fa' }}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={2}>
                    <Form.Group className="mb-3">
                      <Form.Label>Protein (g) <span className="text-muted">(auto)</span></Form.Label>
                      <Form.Control
                        type="number"
                        name="protein"
                        value={formData.protein}
                        onChange={handleChange}
                        placeholder="Auto-calculated"
                        readOnly
                        style={{ backgroundColor: '#f8f9fa' }}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={2}>
                    <Form.Group className="mb-3">
                      <Form.Label>Carbs (g) <span className="text-muted">(auto)</span></Form.Label>
                      <Form.Control
                        type="number"
                        name="carbs"
                        value={formData.carbs}
                        onChange={handleChange}
                        placeholder="Auto-calculated"
                        readOnly
                        style={{ backgroundColor: '#f8f9fa' }}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={2}>
                    <Form.Group className="mb-3">
                      <Form.Label>Fats (g) <span className="text-muted">(auto)</span></Form.Label>
                      <Form.Control
                        type="number"
                        name="fats"
                        value={formData.fats}
                        onChange={handleChange}
                        placeholder="Auto-calculated"
                        readOnly
                        style={{ backgroundColor: '#f8f9fa' }}
                      />
                    </Form.Group>
                  </Col>
                </Row>

                <Button variant="primary" type="submit" className="w-100" disabled={loading}>
                  {loading ? 'Logging...' : 'Log Meal'}
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>

        <Col md={8}>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Today's Meals</h5>
            </Card.Header>
            <Card.Body>
              <div className="mb-4">
                <h6>Search Meals</h6>
                <Form.Control
                  type="text"
                  placeholder="Search by food name or meal type..."
                  onChange={handleSearchChange}
                  className="mb-3"
                />
              </div>
              
              <div className="mb-4">
                <h6>Daily Totals</h6>
                <Row>
                  <Col><strong>Calories:</strong> {totals.calories}</Col>
                  <Col><strong>Protein:</strong> {totals.protein.toFixed(1)}g</Col>
                  <Col><strong>Carbs:</strong> {totals.carbs.toFixed(1)}g</Col>
                  <Col><strong>Fats:</strong> {totals.fats.toFixed(1)}g</Col>
                </Row>
              </div>

              {meals.length > 0 ? (
                <Table striped hover>
                  <thead>
                    <tr>
                      <th>Meal</th>
                      <th>Food</th>
                      <th>Calories</th>
                      <th>Protein</th>
                      <th>Carbs</th>
                      <th>Fats</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {meals.map((meal, index) => (
                      <tr key={index}>
                        <td>{meal.meal_type}</td>
                        <td>{meal.food_name}</td>
                        <td>{meal.calories}</td>
                        <td>{meal.protein}g</td>
                        <td>{meal.carbs}g</td>
                        <td>{meal.fats}g</td>
                        <td>
                          <Button 
                            variant="danger" 
                            size="sm"
                            onClick={() => deleteMeal(meal.id || index)}
                          >
                            🗑️ Delete
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <p className="text-muted">No meals logged today. Start logging your meals to see them here!</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default MealLog;
