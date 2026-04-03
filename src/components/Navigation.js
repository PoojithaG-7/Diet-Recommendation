import React from 'react';
import { Navbar, Nav, Container, NavDropdown } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navigation = () => {
  const { isAuthenticated, logout, token } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Hide navigation on landing page
  if (location.pathname === '/') {
    return null;
  }

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <Navbar bg="light" expand="lg" fixed="top" className="navbar-custom">
      <Container>
        <LinkContainer to="/diet-form">
          <Navbar.Brand>Diet Recommendation System</Navbar.Brand>
        </LinkContainer>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto">
            {isAuthenticated && token && (
              <>
                <LinkContainer to="/diet-form">
                  <Nav.Link>🥗 Diet Plan</Nav.Link>
                </LinkContainer>
                <LinkContainer to="/dashboard">
                  <Nav.Link>📊 Dashboard</Nav.Link>
                </LinkContainer>
                <LinkContainer to="/meals">
                  <Nav.Link>🍽️ Meals</Nav.Link>
                </LinkContainer>
                <LinkContainer to="/exercise">
                  <Nav.Link>🏋️ Exercise</Nav.Link>
                </LinkContainer>
                <LinkContainer to="/water">
                  <Nav.Link>💧 Water</Nav.Link>
                </LinkContainer>
                <LinkContainer to="/reports">
                  <Nav.Link>📈 Reports</Nav.Link>
                </LinkContainer>
              </>
            )}
            <NavDropdown title="Account" id="basic-nav-dropdown">
              {!isAuthenticated ? (
                <>
                  <LinkContainer to="/auth">
                    <NavDropdown.Item>Login / Sign Up</NavDropdown.Item>
                  </LinkContainer>
                  <NavDropdown.Divider />
                  <NavDropdown.Item onClick={() => {
                    localStorage.removeItem('diet_auth_token');
                    window.location.reload();
                  }}>
                    Clear Auth Data
                  </NavDropdown.Item>
                </>
              ) : (
                <>
                  <NavDropdown.Item onClick={handleLogout}>Logout</NavDropdown.Item>
                  <NavDropdown.Divider />
                  <NavDropdown.Item onClick={() => {
                    localStorage.removeItem('diet_auth_token');
                    window.location.reload();
                  }}>
                    Clear Auth Data
                  </NavDropdown.Item>
                </>
              )}
            </NavDropdown>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Navigation;
