import React, { useState, useEffect, useCallback } from 'react';
import { Container, Card, ButtonGroup, Button, Table, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ML_PER_GLASS = 250;

const Reports = () => {
  const { token, authFetch } = useAuth();
  const navigate = useNavigate();
  const [range, setRange] = useState('week');
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    const res = await authFetch(`/api/reports/summary?range=${range}`);
    if (res.status === 401) {
      navigate('/login');
      return;
    }
    const json = await res.json();
    if (!res.ok) {
      setError(json.error || 'Failed to load reports');
      setData(null);
      return;
    }
    setError('');
    setData(json);
  }, [authFetch, navigate, range]);

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    load();
  }, [token, navigate, load]);

  const waterRows = data ? Object.entries(data.water_by_day) : [];
  const exRows = data ? Object.entries(data.exercise_by_day) : [];
  const exCalRows = data ? Object.entries(data.exercise_calories_by_day || {}) : [];

  return (
    <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-4">
        <h2 className="mb-0">Reports</h2>
        <ButtonGroup>
          <Button variant={range === 'week' ? 'primary' : 'outline-primary'} onClick={() => setRange('week')}>
            Week
          </Button>
          <Button variant={range === 'month' ? 'primary' : 'outline-primary'} onClick={() => setRange('month')}>
            Month
          </Button>
        </ButtonGroup>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      {data && (
        <>
          <Card className="mb-4">
            <Card.Body>
              <Card.Title>Summary</Card.Title>
              <p className="mb-1">
                <strong>Water:</strong> {data.water_total_ml} ml (~{(data.water_total_ml / ML_PER_GLASS).toFixed(1)}{' '}
                glasses) over {data.days} days
              </p>
              <p className="mb-0">
                <strong>Exercise:</strong> {data.exercise_sessions} sessions, {data.exercise_total_minutes} minutes total
              </p>
              {data.exercise_total_calories_burned != null && (
                <p className="mb-0">
                  <strong>Calories burned:</strong> {data.exercise_total_calories_burned} kcal
                </p>
              )}
            </Card.Body>
          </Card>

          <RowCards waterRows={waterRows} exRows={exRows} exCalRows={exCalRows} />
        </>
      )}
    </Container>
  );
};

function RowCards({ waterRows, exRows, exCalRows }) {
  const calByDay = Object.fromEntries(exCalRows);
  return (
    <div className="row g-3">
      <div className="col-md-6">
        <Card>
          <Card.Header>Water by day</Card.Header>
          <Table responsive size="sm" className="mb-0">
            <thead>
              <tr>
                <th>Date</th>
                <th>ml</th>
                <th>Glasses</th>
              </tr>
            </thead>
            <tbody>
              {waterRows.length === 0 ? (
                <tr>
                  <td colSpan={3} className="text-muted">
                    No water logged in this range
                  </td>
                </tr>
              ) : (
                waterRows.map(([day, ml]) => (
                  <tr key={day}>
                    <td>{day}</td>
                    <td>{ml}</td>
                    <td>{(ml / ML_PER_GLASS).toFixed(1)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </Table>
        </Card>
      </div>
      <div className="col-md-6">
        <Card>
          <Card.Header>Exercise by day</Card.Header>
          <Table responsive size="sm" className="mb-0">
            <thead>
              <tr>
                <th>Date</th>
                <th>Minutes</th>
                <th>Calories</th>
              </tr>
            </thead>
            <tbody>
              {exRows.length === 0 ? (
                <tr>
                  <td colSpan={3} className="text-muted">
                    No exercise logged in this range
                  </td>
                </tr>
              ) : (
                exRows.map(([day, minutes]) => (
                  <tr key={day}>
                    <td>{day}</td>
                    <td>{minutes}</td>
                    <td>{calByDay[day] != null ? calByDay[day] : '—'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </Table>
        </Card>
      </div>
    </div>
  );
}

export default Reports;
