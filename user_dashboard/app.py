from flask import Flask, jsonify, render_template_string
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)

# Configuration
MAIN_SYSTEM_URL = "http://localhost:5000"  # URL of the main diet system
ADMIN_EMAIL = "admin@diet-system.com"
ADMIN_PASSWORD = "admin123"

# HTML Template for the Admin Dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Diet System - User Data Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .dashboard-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            margin: 20px auto;
            max-width: 1400px;
            padding: 30px;
            backdrop-filter: blur(10px);
        }
        .header-section {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            color: white;
        }
        .stats-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            transition: transform 0.3s ease;
        }
        .stats-card:hover {
            transform: translateY(-5px);
        }
        .user-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        .user-card:hover {
            transform: translateY(-3px);
        }
        .status-badge {
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .status-active {
            background: #d4edda;
            color: #155724;
        }
        .status-inactive {
            background: #f8d7da;
            color: #721c24;
        }
        .refresh-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .data-table {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        .table thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .loading-spinner {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .error-message {
            display: none;
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="dashboard-container">
            <!-- Header -->
            <div class="header-section">
                <h1><i class="fas fa-users"></i> Diet Recommendation System</h1>
                <h2>User Data Dashboard</h2>
                <p class="mb-0">Real-time monitoring of all registered users</p>
            </div>

            <!-- Controls -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <button class="refresh-btn" onclick="loadUserData()">
                        <i class="fas fa-sync-alt"></i> Refresh Data
                    </button>
                </div>
                <div class="col-md-6 text-end">
                    <small class="text-muted">Last updated: <span id="lastUpdated">Never</span></small>
                </div>
            </div>

            <!-- Error Message -->
            <div id="errorMessage" class="error-message">
                <i class="fas fa-exclamation-triangle"></i> <span id="errorText"></span>
            </div>

            <!-- Loading Spinner -->
            <div id="loadingSpinner" class="loading-spinner">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading user data...</p>
            </div>

            <!-- Statistics Cards -->
            <div id="statsContainer" class="row mb-4">
                <!-- Stats will be populated here -->
            </div>

            <!-- Users Table -->
            <div id="usersContainer">
                <!-- Users data will be populated here -->
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let userData = [];
        
        async function loadUserData() {
            const loadingSpinner = document.getElementById('loadingSpinner');
            const errorMessage = document.getElementById('errorMessage');
            const errorText = document.getElementById('errorText');
            const lastUpdated = document.getElementById('lastUpdated');
            
            // Show loading
            loadingSpinner.style.display = 'block';
            errorMessage.style.display = 'none';
            
            try {
                // Get admin token
                const tokenResponse = await fetch('/get-admin-token');
                const tokenData = await tokenResponse.json();
                
                if (!tokenData.success) {
                    throw new Error('Failed to get admin token');
                }
                
                // Get all user data
                const usersResponse = await fetch('/get-all-users', {
                    headers: {
                        'Authorization': `Bearer ${tokenData.token}`
                    }
                });
                
                const usersData = await usersResponse.json();
                
                if (!usersData.success) {
                    throw new Error(usersData.error || 'Failed to fetch user data');
                }
                
                userData = usersData.users;
                displayStats();
                displayUsers();
                
                // Update last updated time
                lastUpdated.textContent = new Date().toLocaleString();
                
            } catch (error) {
                console.error('Error loading user data:', error);
                errorText.textContent = error.message;
                errorMessage.style.display = 'block';
            } finally {
                loadingSpinner.style.display = 'none';
            }
        }
        
        function displayStats() {
            const statsContainer = document.getElementById('statsContainer');
            
            const totalUsers = userData.length;
            const activeUsers = userData.filter(user => user.has_diet_plan).length;
            const inactiveUsers = totalUsers - activeUsers;
            const avgAge = userData.length > 0 ? 
                Math.round(userData.reduce((sum, user) => sum + (user.age || 0), 0) / userData.length) : 0;
            
            const genderStats = userData.reduce((acc, user) => {
                const gender = user.gender || 'unknown';
                acc[gender] = (acc[gender] || 0) + 1;
                return acc;
            }, {});
            
            statsContainer.innerHTML = `
                <div class="col-md-3">
                    <div class="stats-card text-center">
                        <h3 class="text-primary">${totalUsers}</h3>
                        <p class="mb-0">Total Users</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card text-center">
                        <h3 class="text-success">${activeUsers}</h3>
                        <p class="mb-0">Active Users</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card text-center">
                        <h3 class="text-warning">${inactiveUsers}</h3>
                        <p class="mb-0">Inactive Users</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card text-center">
                        <h3 class="text-info">${avgAge}</h3>
                        <p class="mb-0">Average Age</p>
                    </div>
                </div>
            `;
        }
        
        function displayUsers() {
            const usersContainer = document.getElementById('usersContainer');
            
            if (userData.length === 0) {
                usersContainer.innerHTML = `
                    <div class="text-center py-5">
                        <i class="fas fa-users fa-3x text-muted mb-3"></i>
                        <h4 class="text-muted">No users found</h4>
                        <p class="text-muted">No users have registered yet.</p>
                    </div>
                `;
                return;
            }
            
            let tableHTML = `
                <div class="data-table">
                    <table class="table table-hover mb-0">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Age</th>
                                <th>Gender</th>
                                <th>Phone</th>
                                <th>Weight</th>
                                <th>Height</th>
                                <th>BMI</th>
                                <th>Goal</th>
                                <th>Activity</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            userData.forEach(user => {
                const statusClass = user.has_diet_plan ? 'status-active' : 'status-inactive';
                const statusText = user.has_diet_plan ? 'Active' : 'Inactive';
                const statusIcon = user.has_diet_plan ? 'fa-check-circle' : 'fa-times-circle';
                
                tableHTML += `
                    <tr>
                        <td>${user.id || 'N/A'}</td>
                        <td>${user.name || 'N/A'}</td>
                        <td>${user.email || 'N/A'}</td>
                        <td>${user.age || 'N/A'}</td>
                        <td>${user.gender || 'N/A'}</td>
                        <td>${user.phone || 'N/A'}</td>
                        <td>${user.weight ? user.weight + ' kg' : 'N/A'}</td>
                        <td>${user.height ? user.height + ' cm' : 'N/A'}</td>
                        <td>${user.bmi ? user.bmi.toFixed(1) : 'N/A'}</td>
                        <td>${user.goal || 'N/A'}</td>
                        <td>${user.activity_level || 'N/A'}</td>
                        <td>
                            <span class="status-badge ${statusClass}">
                                <i class="fas ${statusIcon}"></i> ${statusText}
                            </span>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="viewUserDetails('${user.id}')">
                                <i class="fas fa-eye"></i> Details
                            </button>
                        </td>
                    </tr>
                `;
            });
            
            tableHTML += `
                        </tbody>
                    </table>
                </div>
            `;
            
            usersContainer.innerHTML = tableHTML;
        }
        
        function viewUserDetails(userId) {
            const user = userData.find(u => u.id === userId);
            if (!user) return;
            
            const details = `
                User ID: ${user.id || 'N/A'}
                Name: ${user.name || 'N/A'}
                Email: ${user.email || 'N/A'}
                Age: ${user.age || 'N/A'}
                Gender: ${user.gender || 'N/A'}
                Phone: ${user.phone || 'N/A'}
                Weight: ${user.weight ? user.weight + ' kg' : 'N/A'}
                Height: ${user.height ? user.height + ' cm' : 'N/A'}
                BMI: ${user.bmi ? user.bmi.toFixed(1) : 'N/A'}
                Goal: ${user.goal || 'N/A'}
                Activity Level: ${user.activity_level || 'N/A'}
                Dietary Notes: ${user.dietary_notes || 'N/A'}
                Has Diet Plan: ${user.has_diet_plan ? 'Yes' : 'No'}
                Daily Calories: ${user.daily_calories_needed || 'N/A'}
            `;
            
            alert(details);
        }
        
        // Auto-refresh every 30 seconds
        setInterval(loadUserData, 30000);
        
        // Load data on page load
        window.onload = function() {
            loadUserData();
        };
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Render the admin dashboard"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/get-admin-token', methods=['POST'])
def get_admin_token():
    """Get admin token from main system"""
    try:
        response = requests.post(f"{MAIN_SYSTEM_URL}/api/auth/login", 
                               json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD})
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'token': data['token']
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to authenticate with main system'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Connection error: {str(e)}'
        }), 500

@app.route('/get-all-users', methods=['GET'])
def get_all_users():
    """Get all users data from main system"""
    try:
        # Get admin token
        auth_response = requests.post(f"{MAIN_SYSTEM_URL}/api/auth/login", 
                                    json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD})
        
        if auth_response.status_code != 200:
            return jsonify({
                'success': False,
                'error': 'Failed to authenticate'
            }), 401
        
        token = auth_response.json()['token']
        
        # Get all user profiles
        users_response = requests.get(f"{MAIN_SYSTEM_URL}/api/auth/profile", 
                                    headers={'Authorization': f'Bearer {token}'})
        
        if users_response.status_code != 200:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch user data'
            }), 400
        
        profile_data = users_response.json()
        
        # Extract users from user_profiles (simulate getting all users)
        # In a real system, you'd have an endpoint to get all users
        # For now, we'll return the current admin user as an example
        users = []
        
        if profile_data.get('profile'):
            user = profile_data['profile']
            users.append({
                'id': user.get('id', '1'),
                'name': user.get('name', 'Unknown'),
                'email': user.get('email', 'unknown@example.com'),
                'age': user.get('age', 0),
                'gender': user.get('gender', 'unknown'),
                'phone': user.get('phone', ''),
                'weight': user.get('weight', 0),
                'height': user.get('height', 0),
                'bmi': user.get('bmi', 0),
                'goal': user.get('goal', 'unknown'),
                'activity_level': user.get('activity_level', 'unknown'),
                'dietary_notes': user.get('dietary_notes', ''),
                'has_diet_plan': bool(user.get('weight') and user.get('height')),
                'daily_calories_needed': user.get('daily_calories_needed', 0),
                'diet_plan': user.get('diet_plan', {}),
                'created_at': '2026-04-02T00:00:00Z'
            })
        
        return jsonify({
            'success': True,
            'users': users,
            'total_count': len(users)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error fetching user data: {str(e)}'
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'User Data Dashboard'
    })

if __name__ == '__main__':
    print("Starting User Data Dashboard...")
    print(f"Main System URL: {MAIN_SYSTEM_URL}")
    print("Dashboard will be available at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
