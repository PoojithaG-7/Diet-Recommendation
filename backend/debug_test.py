@app.route('/api/debug/user-lookup', methods=['POST'])
def debug_user_lookup():
    """Debug endpoint to test user lookup only"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        print(f"DEBUG: Looking up user for email: {email}")
        
        if email not in users:
            return jsonify({'error': 'User not found'}), 404
            
        user = users[email]
        print(f"DEBUG: User found: {user}")
        print(f"DEBUG: User type: {type(user)}")
        
        return jsonify({
            'success': True,
            'message': 'User lookup successful',
            'user': user
        })
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    create_default_admin()
    print("\n" + "="*60)
    print("Starting OPTIMIZED Diet Recommendation System...")
    print("  FAST - Optimized for speed")
    print("  COMPLETE - Diet + Exercise + Water + Weekly Schedule + Reports + Compliance Tracking")
    print("\nAvailable endpoints:")
    print("  GET  /api/health - Health check")
    print("  POST /api/auth/register - User registration")
    print("  POST /api/auth/login - User login")
    print("  GET  /api/profile - Get user profile")
    print("  POST /api/save-profile - Save profile & get recommendations")
    print("  POST /api/bmi-calculator - Calculate BMI")
    print("  POST /api/water - Complete predefined water task (tick-based)")
    print("  GET  /api/water - Get water tasks for date")
    print("  POST /api/exercise - Complete predefined exercise task (tick-based)")
    print("  GET  /api/exercise - Get exercise tasks for date")
    print("  POST /api/diet-log - Log diet intake")
    print("  GET  /api/diet-log - Get diet logs")
    print("  GET  /api/personalized-plan - Get personalized exercise, water & reports")
    print("  GET  /api/daily-tasks - Get predefined daily tasks to complete")
    print("  POST /api/complete-task - Complete task with random encouragement + IMAGE")
    print("  GET  /api/achievement-reward - Get visual reward for achievement level")
    print("  GET  /api/weekly-reward - Get weekly visual reward based on progress")
    print("  GET  /api/user-activities - Get what user actually completed")
    print("  GET  /api/progress-report - Get detailed report of user activities")
    print("  GET  /api/calendar - Get monthly compliance calendar with encouragement")
    print("  GET  /api/calendar/day - Get detailed compliance for specific day")
    print("  GET  /api/compliance-report - Get compliance report with encouragement")
    print("  GET  /api/reports/summary - Get reports summary")
    print("\nFeatures:")
    print("  [OK] Personalized diet recommendations")
    print("  [OK] Predefined daily tasks with tick-to-complete system")
    print("  [OK] TICK-BASED water and exercise logging (no manual input)")
    print("  [OK] Random encouragement messages with emojis (never same)")
    print("  [OK] GOAL-BASED IMAGE REWARDS (muscle growth, fat burning, balance)")
    print("  [OK] Visual motivation images that change based on user's goals")
    print("  [OK] Calendar tracking based on ticked tasks (not manual logs)")
    print("  [OK] Diet compliance checking")
    print("  [OK] Achievement and encouragement System")
    print("  [OK] Monthly compliance calendar with daily encouragement")
    print("  [OK] Streak tracking and progress visualization")
    print("  [OK] Progress reports showing what user actually completed")
    print("  [OK] Weekly reports and analytics")
    print("\nServer running on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
