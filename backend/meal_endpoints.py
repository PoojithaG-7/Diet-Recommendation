@app.route('/api/diet-log', methods=['POST'])
@require_auth
def log_meal():
    """Log meal intake"""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['meal_type', 'food_name', 'calories', 'protein', 'carbs', 'fats']
        for field in required_fields:
            if not data.get(field) and field != 'food_name':
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create meal entry
        meal_entry = {
            'id': str(len(user_logs[user_id]['diet_logs']) + 1),
            'meal_type': data['meal_type'],
            'food_name': data['food_name'],
            'calories': int(data['calories']) or 0,
            'protein': float(data['protein']) or 0.0,
            'carbs': float(data['carbs']) or 0.0,
            'fats': float(data['fats']) or 0.0,
            'date': data.get('date', get_ist_time().date().isoformat()),
            'logged_at': get_ist_time().isoformat()
        }
        
        # Add to user logs
        user_logs[user_id]['diet_logs'].append(meal_entry)
        
        return jsonify({
            'success': True,
            'message': 'Meal logged successfully',
            'meal': meal_entry
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to log meal: {str(e)}'}), 500

@app.route('/api/diet-log', methods=['GET'])
@require_auth
def get_meal_logs():
    """Get meal logs for a specific date"""
    try:
        user_id = request.user_id
        date_param = request.args.get('date')
        
        if not date_param:
            date_param = get_ist_time().date().isoformat()
        
        # Filter logs by date
        logs = []
        for log in user_logs[user_id]['diet_logs']:
            if log['date'] == date_param:
                logs.append(log)
        
        return jsonify({
            'success': True,
            'date': date_param,
            'logs': logs
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get meal logs: {str(e)}'}), 500
