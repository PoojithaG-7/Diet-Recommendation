import React from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import './Landing.css';

const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      <div className="hero-section">
        <Container>
          <Row className="align-items-center min-vh-100">
            <Col md={12} className="text-center">
              <div className="hero-content">
                <h1 className="hero-title">🥗 Diet Recommendation System</h1>
                <p className="hero-subtitle">
                  Your personalized journey to better health starts here
                </p>
                <p className="hero-description">
                  Get customized diet plans, track your meals, monitor exercise, 
                  and achieve your health goals with our intelligent recommendation system.
                </p>
                <div className="hero-features">
                  <div className="feature-item">
                    <span className="feature-icon">🍎</span>
                    <span>Personalized Diet Plans</span>
                  </div>
                  <div className="feature-item">
                    <span className="feature-icon">🏃‍♂️</span>
                    <span>Exercise Tracking</span>
                  </div>
                  <div className="feature-item">
                    <span className="feature-icon">💧</span>
                    <span>Water Intake Monitoring</span>
                  </div>
                  <div className="feature-item">
                    <span className="feature-icon">📊</span>
                    <span>Progress Analytics</span>
                  </div>
                </div>
                <Button 
                  variant="primary" 
                  size="lg" 
                  className="get-started-btn"
                  onClick={() => navigate('/auth')}
                >
                  Get Started
                </Button>
              </div>
            </Col>
          </Row>
        </Container>
      </div>
    </div>
  );
};

export default Landing;
