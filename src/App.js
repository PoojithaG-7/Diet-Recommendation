import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import ProtectedRoute from './components/ProtectedRoute';
import Landing from './pages/Landing';
import Auth from './pages/Auth';
import DietForm from './pages/DietForm';
import Dashboard from './pages/Dashboard';
import WaterLog from './pages/WaterLog';
import ExerciseLog from './pages/ExerciseLog';
import MealLog from './pages/MealLog';
import Reports from './pages/Reports';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navigation />
        <main className="main-content">
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Landing />} />
            <Route path="/auth" element={<Auth />} />
            
            {/* Protected routes - require authentication */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/diet-form" element={
              <ProtectedRoute>
                <DietForm />
              </ProtectedRoute>
            } />
            <Route path="/exercise" element={
              <ProtectedRoute>
                <ExerciseLog />
              </ProtectedRoute>
            } />
            <Route path="/water" element={
              <ProtectedRoute>
                <WaterLog />
              </ProtectedRoute>
            } />
            <Route path="/meals" element={
              <ProtectedRoute>
                <MealLog />
              </ProtectedRoute>
            } />
            <Route path="/reports" element={
              <ProtectedRoute>
                <Reports />
              </ProtectedRoute>
            } />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
