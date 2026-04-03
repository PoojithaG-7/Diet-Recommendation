import React from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';

const Home = () => {
  return (
    <div>
      <div className="hero-section">
        <Container>
          <h1 className="display-4 fw-bold mb-4">Welcome to Diet Recommendation System</h1>
          <p className="lead mb-4">
            Get personalized diet plans tailored to your health goals, dietary preferences, and lifestyle
          </p>
          <div className="d-flex gap-3 justify-content-center">
            <LinkContainer to="/register">
              <Button variant="light" size="lg">Get Started</Button>
            </LinkContainer>
            <LinkContainer to="/login">
              <Button variant="outline-light" size="lg">Login</Button>
            </LinkContainer>
          </div>
        </Container>
      </div>

      <Container className="my-5">
        <h2 className="text-center mb-5">Features</h2>
        <Row>
          <Col md={4} className="mb-4">
            <Card className="feature-card h-100 shadow-sm">
              <Card.Body className="text-center">
                <div className="mb-3">
                  <span style={{ fontSize: '3rem' }}>🎯</span>
                </div>
                <Card.Title>Personalized Plans</Card.Title>
                <Card.Text>
                  Get diet recommendations based on your age, weight, height, and health goals
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4} className="mb-4">
            <Card className="feature-card h-100 shadow-sm">
              <Card.Body className="text-center">
                <div className="mb-3">
                  <span style={{ fontSize: '3rem' }}>📊</span>
                </div>
                <Card.Title>Track Progress</Card.Title>
                <Card.Text>
                  Monitor your nutritional intake and track your health goals over time
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4} className="mb-4">
            <Card className="feature-card h-100 shadow-sm">
              <Card.Body className="text-center">
                <div className="mb-3">
                  <span style={{ fontSize: '3rem' }}>🥗</span>
                </div>
                <Card.Title>Nutrition Insights</Card.Title>
                <Card.Text>
                  Learn about balanced nutrition and make informed food choices
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>

      <Container className="my-5">
        <Row className="align-items-center">
          <Col md={6}>
            <h3>How It Works</h3>
            <ul className="list-unstyled">
              <li className="mb-3">
                <strong>1. Sign Up:</strong> Create your account and set up your profile
              </li>
              <li className="mb-3">
                <strong>2. Fill Diet Form:</strong> Provide your health information and dietary preferences
              </li>
              <li className="mb-3">
                <strong>3. Get Recommendations:</strong> Receive personalized diet plans and meal suggestions
              </li>
              <li className="mb-3">
                <strong>4. Track Progress:</strong> Monitor your journey on your dashboard
              </li>
            </ul>
            <LinkContainer to="/register">
              <Button variant="primary" size="lg">Start Your Journey</Button>
            </LinkContainer>
          </Col>
          <Col md={6}>
            <div className="text-center">
              <span style={{ fontSize: '8rem' }}>🏃‍♂️</span>
            </div>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default Home;
