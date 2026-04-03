from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import csv
import os
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

class AdminDashboard:
    """
    Admin dashboard system to track all user activities
    Perfect for B.Tech project - comprehensive user analytics
    """
    
    def __init__(self):
        """Initialize with all data files"""
        self.users_file = 'users.csv'
        self.activities_file = 'user_activities.csv'
        self.diet_requests_file = 'diet_requests.csv'
        self.ensure_files_exist()
    
    def ensure_files_exist(self):
        """Create all necessary CSV files with headers"""
        
        # User activities file
        if not os.path.exists(self.activities_file):
            with open(self.activities_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['timestamp', 'user_email', 'activity_type', 'details'])
        
        # Diet requests file
        if not os.path.exists(self.diet_requests_file):
            with open(self.diet_requests_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['timestamp', 'user_email', 'weight', 'height', 'age', 'gender', 
                               'activity_level', 'health_conditions', 'bmi', 'bmi_category', 'calories_needed'])
    
    def log_user_activity(self, email, activity_type, details):
        """Log any user activity"""
        try:
            with open(self.activities_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), email, activity_type, details])
            return True
        except Exception as e:
            print(f"Error logging activity: {e}")
            return False
    
    def log_diet_request(self, email, user_data, recommendation):
        """Log diet recommendation requests"""
        try:
            with open(self.diet_requests_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    email,
                    user_data.get('weight', ''),
                    user_data.get('height', ''),
                    user_data.get('age', ''),
                    user_data.get('gender', ''),
                    user_data.get('activity_level', ''),
                    user_data.get('health_conditions', ''),
                    recommendation.get('health_metrics', {}).get('bmi', ''),
                    recommendation.get('health_metrics', {}).get('bmi_category', ''),
                    recommendation.get('health_metrics', {}).get('daily_calorie_needs', '')
                ])
            return True
        except Exception as e:
            print(f"Error logging diet request: {e}")
            return False
    
    def get_all_users(self):
        """Get all registered users"""
        users = []
        try:
            with open(self.users_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 5:
                        users.append({
                            'id': row[0],
                            'name': row[1],
                            'email': row[2],
                            'password': row[3],
                            'registration_date': row[4]
                        })
        except FileNotFoundError:
            pass
        return users
    
    def get_user_activities(self, email=None):
        """Get user activities, optionally filtered by email"""
        activities = []
        try:
            with open(self.activities_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 4:
                        activity = {
                            'timestamp': row[0],
                            'user_email': row[1],
                            'activity_type': row[2],
                            'details': row[3]
                        }
                        if email is None or row[1] == email:
                            activities.append(activity)
        except FileNotFoundError:
            pass
        return activities
    
    def get_diet_requests(self, email=None):
        """Get diet requests, optionally filtered by email"""
        requests = []
        try:
            with open(self.diet_requests_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 11:
                        request = {
                            'timestamp': row[0],
                            'user_email': row[1],
                            'weight': row[2],
                            'height': row[3],
                            'age': row[4],
                            'gender': row[5],
                            'activity_level': row[6],
                            'health_conditions': row[7],
                            'bmi': row[8],
                            'bmi_category': row[9],
                            'calories_needed': row[10]
                        }
                        if email is None or row[1] == email:
                            requests.append(request)
        except FileNotFoundError:
            pass
        return requests
    
    def get_dashboard_stats(self):
        """Get comprehensive dashboard statistics"""
        users = self.get_all_users()
        activities = self.get_user_activities()
        diet_requests = self.get_diet_requests()
        
        # Calculate statistics
        total_users = len(users)
        total_logins = len([a for a in activities if a['activity_type'] == 'login'])
        total_diet_requests = len(diet_requests)
        
        # BMI distribution
        bmi_categories = {}
        for req in diet_requests:
            category = req.get('bmi_category', 'Unknown')
            bmi_categories[category] = bmi_categories.get(category, 0) + 1
        
        # Health conditions distribution
        health_conditions = {}
        for req in diet_requests:
            conditions = req.get('health_conditions', 'none')
            if conditions != 'none':
                for condition in conditions.split(','):
                    condition = condition.strip()
                    health_conditions[condition] = health_conditions.get(condition, 0) + 1
        
        # Recent activities
        recent_activities = sorted(activities, key=lambda x: x['timestamp'], reverse=True)[:10]
        
        return {
            'total_users': total_users,
            'total_logins': total_logins,
            'total_diet_requests': total_diet_requests,
            'bmi_distribution': bmi_categories,
            'health_conditions': health_conditions,
            'recent_activities': recent_activities,
            'users': users
        }

# Initialize admin dashboard
admin = AdminDashboard()

# HTML Template for Admin Dashboard
ADMIN_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Diet Recommendation System - Admin Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
        }
        .stat-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
        .activity-item {
            border-left: 4px solid #667eea;
            padding-left: 1rem;
            margin-bottom: 0.5rem;
        }
    </style>
</head>
<body>
    <div class="dashboard-header">
        <div class="container">
            <h1>🏥 Diet Recommendation System</h1>
            <h2>Admin Dashboard</h2>
            <p class="mb-0">Monitor user activities and health analytics</p>
        </div>
    </div>

    <div class="container">
        <!-- Statistics Cards -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="stat-card text-center">
                    <div class="stat-number">{{ total_users }}</div>
                    <div class="text-muted">Total Users</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card text-center">
                    <div class="stat-number">{{ total_logins }}</div>
                    <div class="text-muted">Total Logins</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card text-center">
                    <div class="stat-number">{{ total_diet_requests }}</div>
                    <div class="text-muted">Diet Requests</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card text-center">
                    <div class="stat-number">{{ health_conditions|length }}</div>
                    <div class="text-muted">Health Conditions</div>
                </div>
            </div>
        </div>

        <!-- BMI Distribution -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="stat-card">
                    <h5>📊 BMI Distribution</h5>
                    {% for category, count in bmi_distribution.items() %}
                    <div class="d-flex justify-content-between mb-2">
                        <span>{{ category }}</span>
                        <span class="badge bg-primary">{{ count }}</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
            <div class="col-md-6">
                <div class="stat-card">
                    <h5>🏥 Health Conditions</h5>
                    {% for condition, count in health_conditions.items() %}
                    <div class="d-flex justify-content-between mb-2">
                        <span>{{ condition|title }}</span>
                        <span class="badge bg-warning">{{ count }}</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- Recent Activities -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="stat-card">
                    <h5>📋 Recent Activities</h5>
                    {% for activity in recent_activities %}
                    <div class="activity-item">
                        <strong>{{ activity.timestamp }}</strong> - 
                        {{ activity.user_email }} - 
                        {{ activity.activity_type|title }}
                        {% if activity.details %}
                        <br><small class="text-muted">{{ activity.details }}</small>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- All Users Table -->
        <div class="row">
            <div class="col-12">
                <div class="stat-card">
                    <h5>👥 All Registered Users</h5>
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Registration Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for user in users %}
                                <tr>
                                    <td>{{ user.id }}</td>
                                    <td>{{ user.name }}</td>
                                    <td>{{ user.email }}</td>
                                    <td>{{ user.registration_date }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard HTML page"""
    stats = admin.get_dashboard_stats()
    return render_template_string(ADMIN_DASHBOARD_HTML, **stats)

@app.route('/api/admin/stats')
def get_admin_stats():
    """Get dashboard statistics as JSON"""
    return jsonify(admin.get_dashboard_stats())

@app.route('/api/admin/users')
def get_admin_users():
    """Get all users data"""
    return jsonify({
        'success': True,
        'users': admin.get_all_users()
    })

@app.route('/api/admin/activities')
def get_admin_activities():
    """Get all user activities"""
    email = request.args.get('email')
    return jsonify({
        'success': True,
        'activities': admin.get_user_activities(email)
    })

@app.route('/api/admin/diet-requests')
def get_admin_diet_requests():
    """Get all diet requests"""
    email = request.args.get('email')
    return jsonify({
        'success': True,
        'diet_requests': admin.get_diet_requests(email)
    })

@app.route('/api/admin/log-activity', methods=['POST'])
def log_activity():
    """Log user activity (called by other endpoints)"""
    try:
        data = request.get_json()
        email = data.get('email')
        activity_type = data.get('activity_type')
        details = data.get('details', '')
        
        if admin.log_user_activity(email, activity_type, details):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Failed to log activity'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/admin/log-diet-request', methods=['POST'])
def log_diet_request():
    """Log diet recommendation request with detailed data"""
    try:
        data = request.get_json()
        email = data.get('email')
        user_data = data.get('user_data', {})
        recommendation = data.get('recommendation', {})
        
        if admin.log_diet_request(email, user_data, recommendation):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Failed to log diet request'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    print("Starting Admin Dashboard...")
    print("Access the dashboard at: http://localhost:5001/admin")
    print("API endpoints:")
    print("  GET  /admin - Dashboard HTML")
    print("  GET  /api/admin/stats - Dashboard statistics")
    print("  GET  /api/admin/users - All users")
    print("  GET  /api/admin/activities - User activities")
    print("  GET  /api/admin/diet-requests - Diet requests")
    print("\nAdmin Dashboard running on http://localhost:5001")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
