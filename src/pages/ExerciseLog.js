import React, { useState, useEffect, useCallback } from 'react';
import { Container, Card, Form, Button, Row, Col, Alert, Table, Badge } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ExerciseLog = () => {
  const { token, authFetch } = useAuth();
  const navigate = useNavigate();
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [hasDietPlan, setHasDietPlan] = useState(false);

  // Simplified - remove diet plan gating for smooth operation
  useEffect(() => {
    // Just load exercise tasks without diet plan checks
  }, []);

  const [exerciseTasks, setExerciseTasks] = useState([]);
  const [completedTasks, setCompletedTasks] = useState([]);
  const [complianceScore, setComplianceScore] = useState(0);
  const [totalTasks, setTotalTasks] = useState(0);
  const [encouragement, setEncouragement] = useState('');
  const [rewardImage, setRewardImage] = useState('');

  const loadToday = useCallback(async () => {
    const res = await authFetch('/api/exercise');
    if (res.status === 401) {
      navigate('/login');
      return;
    }
    const data = await res.json();
    if (!res.ok) {
      setError(data.error || 'Failed to load exercise tasks');
      return;
    }
    setExerciseTasks(data.exercise_tasks || []);
    setCompletedTasks(data.exercise_tasks?.filter(task => task.completed) || []);
    setComplianceScore(data.compliance_score || 0);
    setTotalTasks(data.total_tasks || 0);
  }, [authFetch, navigate]);

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    loadToday();
  }, [token, navigate, loadToday]);

  const handleTaskComplete = async (taskId) => {
    setError('');
    setLoading(true);
    setEncouragement('');
    setRewardImage('');
    
    try {
      const res = await authFetch('/api/exercise', {
        method: 'POST',
        body: { task_id: taskId },
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || 'Could not complete exercise task');
        return;
      }
      
      // Show encouragement and reward
      setEncouragement(data.encouragement || 'Exercise task completed!');
      setRewardImage(data.reward_image || '');
      
      // Reload tasks
      await loadToday();
    } catch {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="py-4">
      <h2 className="mb-4">🏋️ Exercise Tasks - Tick to Complete</h2>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      {/* Encouragement and Reward Section */}
      {encouragement && (
        <Alert variant="success" className="mb-4">
          <div className="d-flex align-items-center">
            <div className="flex-grow-1">
              <h5 className="mb-2">{encouragement}</h5>
              {rewardImage && (
                <img 
                  src={rewardImage} 
                  alt="Reward" 
                  className="img-fluid rounded" 
                  style={{ maxWidth: '200px', height: 'auto' }}
                />
              )}
            </div>
          </div>
        </Alert>
      )}

      {/* Progress Overview */}
      <Card className="mb-4">
        <Card.Body>
          <Card.Title>Today's Progress</Card.Title>
          <Row className="text-center">
            <Col md={4}>
              <h4>{completedTasks.length}/{totalTasks}</h4>
              <p className="text-muted">Tasks Completed</p>
            </Col>
            <Col md={4}>
              <h4>{complianceScore}%</h4>
              <p className="text-muted">Compliance Score</p>
            </Col>
            <Col md={4}>
              <h4>{completedTasks.reduce((total, task) => {
                const duration = parseInt(task.duration) || 0;
                return total + duration;
              }, 0)} min</h4>
              <p className="text-muted">Exercise Time</p>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Exercise Tasks */}
      <Row>
        <Col md={12}>
          <Card>
            <Card.Body>
              <Card.Title>Today's Exercise Tasks</Card.Title>
              {exerciseTasks.length === 0 ? (
                <Alert variant="info">
                  No exercise tasks available. Please complete your diet plan first.
                </Alert>
              ) : (
                <div className="task-list">
                  {exerciseTasks.map((task) => (
                    <div key={task.id} className="border rounded p-3 mb-3">
                      <div className="d-flex align-items-center justify-content-between">
                        <div className="d-flex align-items-center">
                          <span className="me-3" style={{ fontSize: '1.5rem' }}>
                            {task.icon}
                          </span>
                          <div>
                            <h6 className="mb-1">{task.name}</h6>
                            <p className="mb-0 text-muted">
                              {task.duration} - {task.focus}
                            </p>
                            {task.completed_at && (
                              <small className="text-success">
                                Completed at {task.completed_at && task.completed_at !== 'Invalid Date' ? 
                                  new Date(task.completed_at).toLocaleTimeString('en-US', { 
                                    hour: '2-digit', 
                                    minute: '2-digit',
                                    hour12: true 
                                  }) : 
                                  'Just now'}
                              </small>
                            )}
                          </div>
                        </div>
                        <div className="d-flex align-items-center">
                          {task.completed ? (
                            <Badge bg="success" className="me-2">Completed</Badge>
                          ) : (
                            <Button
                              variant="primary"
                              size="sm"
                              onClick={() => handleTaskComplete(task.id)}
                              disabled={loading}
                            >
                              {loading ? 'Completing...' : 'Complete'}
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default ExerciseLog;
