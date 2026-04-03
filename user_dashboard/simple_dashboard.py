from flask import Flask, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Configuration
MAIN_SYSTEM_URL = "http://localhost:5000"
ADMIN_EMAIL = "admin@diet-system.com"
ADMIN_PASSWORD = "admin123"

@app.route('/')
def dashboard():
    """Simple dashboard page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>User Data Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
            .header { text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .stats { display: flex; justify-content: space-around; margin-bottom: 20px; }
            .stat-card { background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; min-width: 150px; }
            .user-table { width: 100%; border-collapse: collapse; }
            .user-table th, .user-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            .user-table th { background: #f8f9fa; }
            .btn { padding: 5px 10px; border: none; border-radius: 4px; cursor: pointer; }
            .btn-primary { background: #007bff; color: white; }
            .loading { text-align: center; padding: 20px; }
            .error { background: #f8d7da; color: #721c24; padding: 10px; border-radius: 4px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>User Data Dashboard</h1>
                <p>Diet Recommendation System - User Monitoring</p>
            </div>
            
            <div id="loading" class="loading">Loading user data...</div>
            <div id="error" class="error" style="display: none;"></div>
            
            <div id="content" style="display: none;">
                <div class="stats" id="stats"></div>
                <div id="userTable"></div>
                <button onclick="loadData()" class="btn btn-primary">Refresh Data</button>
            </div>
        </div>
        
        <script>
            async function loadData() {
                document.getElementById('loading').style.display = 'block';
                document.getElementById('error').style.display = 'none';
                document.getElementById('content').style.display = 'none';
                
                try {
                    const response = await fetch('/api/users');
                    const data = await response.json();
                    
                    if (data.success) {
                        displayStats(data.stats);
                        displayUsers(data.users);
                        document.getElementById('content').style.display = 'block';
                    } else {
                        throw new Error(data.error || 'Failed to load data');
                    }
                } catch (error) {
                    document.getElementById('error').textContent = 'Error: ' + error.message;
                    document.getElementById('error').style.display = 'block';
                } finally {
                    document.getElementById('loading').style.display = 'none';
                }
            }
            
            function displayStats(stats) {
                document.getElementById('stats').innerHTML = `
                    <div class="stat-card">
                        <h3>${stats.total_users}</h3>
                        <p>Total Users</p>
                    </div>
                    <div class="stat-card">
                        <h3>${stats.active_users}</h3>
                        <p>Active Users</p>
                    </div>
                    <div class="stat-card">
                        <h3>${stats.inactive_users}</h3>
                        <p>Inactive Users</p>
                    </div>
                    <div class="stat-card">
                        <h3>${stats.avg_age}</h3>
                        <p>Average Age</p>
                    </div>
                `;
            }
            
            function displayUsers(users) {
                let tableHTML = `
                    <table class="user-table">
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Age</th>
                            <th>Gender</th>
                            <th>Weight</th>
                            <th>Height</th>
                            <th>BMI</th>
                            <th>Status</th>
                        </tr>
                `;
                
                users.forEach(user => {
                    const status = user.has_diet_plan ? 'Active' : 'Inactive';
                    const statusColor = user.has_diet_plan ? '#28a745' : '#dc3545';
                    
                    tableHTML += `
                        <tr>
                            <td>${user.name || 'N/A'}</td>
                            <td>${user.email || 'N/A'}</td>
                            <td>${user.age || 'N/A'}</td>
                            <td>${user.gender || 'N/A'}</td>
                            <td>${user.weight ? user.weight + ' kg' : 'N/A'}</td>
                            <td>${user.height ? user.height + ' cm' : 'N/A'}</td>
                            <td>${user.bmi ? user.bmi.toFixed(1) : 'N/A'}</td>
                            <td style="color: ${statusColor}">${status}</td>
                        </tr>
                    `;
                });
                
                tableHTML += '</table>';
                document.getElementById('userTable').innerHTML = tableHTML;
            }
            
            // Load data on page load
            window.onload = loadData;
        </script>
    </body>
    </html>
    """

@app.route('/api/users')
def get_users():
    """Get all users data"""
    try:
        # Get admin token
        auth_response = requests.post(f"{MAIN_SYSTEM_URL}/api/auth/login", 
                                    json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD})
        
        if auth_response.status_code != 200:
            return jsonify({
                'success': False,
                'error': 'Failed to authenticate with main system'
            })
        
        token = auth_response.json()['token']
        
        # Get user profile
        profile_response = requests.get(f"{MAIN_SYSTEM_URL}/api/auth/profile", 
                                        headers={'Authorization': f'Bearer {token}'})
        
        if profile_response.status_code != 200:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch user data'
            })
        
        profile_data = profile_response.json()
        
        # Extract user data
        users = []
        if profile_data.get('profile'):
            user = profile_data['profile']
            users.append({
                'name': user.get('name', 'Unknown'),
                'email': user.get('email', 'unknown@example.com'),
                'age': user.get('age', 0),
                'gender': user.get('gender', 'unknown'),
                'weight': user.get('weight', 0),
                'height': user.get('height', 0),
                'bmi': user.get('bmi', 0),
                'goal': user.get('goal', 'unknown'),
                'activity_level': user.get('activity_level', 'unknown'),
                'has_diet_plan': bool(user.get('weight') and user.get('height'))
            })
        
        # Calculate stats
        total_users = len(users)
        active_users = len([u for u in users if u['has_diet_plan']])
        inactive_users = total_users - active_users
        avg_age = sum(u['age'] for u in users) / total_users if total_users > 0 else 0
        
        return jsonify({
            'success': True,
            'users': users,
            'stats': {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': inactive_users,
                'avg_age': round(avg_age, 1)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        })

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'User Data Dashboard'
    })

if __name__ == '__main__':
    print("Starting User Data Dashboard...")
    print("Dashboard will be available at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=5001, debug=False)
