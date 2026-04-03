import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Alert, Nav, Tab } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

const Auth = () => {
  const [activeTab, setActiveTab] = useState('login');
  const [loginData, setLoginData] = useState({ email: '', password: '' });
  const [registerData, setRegisterData] = useState({
    name: '',
    email: '',
    password: '',
    age: '',
    gender: '',
    phone: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Trim whitespace from inputs
    const trimmedEmail = loginData.email.trim();
    const trimmedPassword = loginData.password.trim();

    if (!trimmedEmail || !trimmedPassword) {
      setError('Please enter both email and password');
      setLoading(false);
      return;
    }

    try {
      const result = await login(trimmedEmail, trimmedPassword);
      navigate('/diet-form');
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await register(registerData);
      navigate('/diet-form');
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <Container>
        <Row className="justify-content-center">
          <Col md={8} lg={6} xl={5}>
            <Card className="auth-card">
              <Card.Header className="text-center">
                <h2 className="auth-title">Welcome to Diet Recommendation System</h2>
                <p className="auth-subtitle">Your health journey starts here</p>
                <small className="text-muted">After login, you'll be guided to create your personalized diet plan</small>
              </Card.Header>
              <Card.Body>
                {error && <Alert variant="danger">{error}</Alert>}
                
                <Tab.Container activeKey={activeTab} onSelect={(k) => setActiveTab(k)}>
                  <Nav variant="pills" className="auth-nav justify-content-center mb-4">
                    <Nav.Item>
                      <Nav.Link eventKey="login">Login</Nav.Link>
                    </Nav.Item>
                    <Nav.Item>
                      <Nav.Link eventKey="register">Sign Up</Nav.Link>
                    </Nav.Item>
                  </Nav>
                  
                  <Tab.Content>
                    <Tab.Pane eventKey="login">
                      <form onSubmit={handleLogin}>
                        <div className="form-group mb-3">
                          <label className="form-label">Email Address</label>
                          <input
                            type="email"
                            className="form-control"
                            placeholder="Enter your email"
                            value={loginData.email}
                            onChange={(e) => setLoginData({...loginData, email: e.target.value})}
                            required
                          />
                          <small className="text-muted">Email is case-insensitive</small>
                        </div>
                        <div className="form-group mb-4">
                          <label className="form-label">Password</label>
                          <input
                            type="password"
                            className="form-control"
                            placeholder="Enter your password"
                            value={loginData.password}
                            onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                            required
                          />
                        </div>
                        <Button 
                          type="submit" 
                          className="auth-btn w-100"
                          disabled={loading}
                        >
                          {loading ? 'Logging in...' : 'Login'}
                        </Button>
                      </form>
                    </Tab.Pane>
                    
                    <Tab.Pane eventKey="register">
                      <form onSubmit={handleRegister}>
                        <div className="form-group mb-3">
                          <label className="form-label">Full Name</label>
                          <input
                            type="text"
                            className="form-control"
                            placeholder="Enter your full name"
                            value={registerData.name}
                            onChange={(e) => setRegisterData({...registerData, name: e.target.value})}
                            required
                          />
                        </div>
                        <div className="form-group mb-3">
                          <label className="form-label">Email Address</label>
                          <input
                            type="email"
                            className="form-control"
                            placeholder="Enter your email"
                            value={registerData.email}
                            onChange={(e) => setRegisterData({...registerData, email: e.target.value})}
                            required
                          />
                        </div>
                        <div className="form-group mb-3">
                          <label className="form-label">Password</label>
                          <input
                            type="password"
                            className="form-control"
                            placeholder="Create a password"
                            value={registerData.password}
                            onChange={(e) => setRegisterData({...registerData, password: e.target.value})}
                            required
                          />
                        </div>
                        <div className="form-group mb-3">
                          <label className="form-label">Age</label>
                          <input
                            type="number"
                            className="form-control"
                            placeholder="Enter your age"
                            value={registerData.age}
                            onChange={(e) => setRegisterData({...registerData, age: e.target.value})}
                            required
                          />
                        </div>
                        <div className="form-group mb-3">
                          <label className="form-label">Gender</label>
                          <select
                            className="form-control"
                            value={registerData.gender}
                            onChange={(e) => setRegisterData({...registerData, gender: e.target.value})}
                            required
                          >
                            <option value="">Select Gender</option>
                            <option value="male">Male</option>
                            <option value="female">Female</option>
                            <option value="other">Other</option>
                          </select>
                        </div>
                        <div className="form-group mb-4">
                          <label className="form-label">Phone Number (Optional)</label>
                          <input
                            type="tel"
                            className="form-control"
                            placeholder="Enter your phone number"
                            value={registerData.phone}
                            onChange={(e) => setRegisterData({...registerData, phone: e.target.value})}
                          />
                        </div>
                        <Button 
                          type="submit" 
                          className="auth-btn w-100"
                          disabled={loading}
                        >
                          {loading ? 'Creating Account...' : 'Sign Up'}
                        </Button>
                      </form>
                    </Tab.Pane>
                  </Tab.Content>
                </Tab.Container>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default Auth;
