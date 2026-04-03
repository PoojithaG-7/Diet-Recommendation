import os
from datetime import datetime, timedelta

from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
    jsonify,
)

from models import db, User, UserProfile


admin_bp = Blueprint('admin', __name__, template_folder='templates')

ACTIVE_MINUTES = int(os.environ.get('ADMIN_ACTIVE_WINDOW_MINUTES', '15'))


def _admin_secret():
    return os.environ.get('ADMIN_SECRET', '').strip()


def admin_session_ok():
    return session.get('admin_authenticated') is True


@admin_bp.route('/admin', methods=['GET'])
def admin_dashboard():
    secret = _admin_secret()
    if not secret:
        return (
            render_template(
                'admin/dashboard.html',
                error='ADMIN_SECRET is not set. Add it to your environment.',
                overview=None,
            ),
            503,
        )
    if not admin_session_ok():
        return render_template('admin/login.html')
    return render_template('admin/dashboard.html', overview=_build_overview(), error=None)


@admin_bp.route('/admin/login', methods=['POST'])
def admin_login():
    key = (request.form.get('admin_key') or '').strip()
    if key and key == _admin_secret():
        session['admin_authenticated'] = True
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('admin/login.html', error='Invalid developer key'), 401


@admin_bp.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin_authenticated', None)
    return redirect(url_for('admin.admin_dashboard'))


def _build_overview():
    now = datetime.utcnow()
    cutoff = now - timedelta(minutes=ACTIVE_MINUTES)
    users = User.query.order_by(User.id.asc()).all()
    total = len(users)
    active = sum(1 for u in users if u.last_activity and u.last_activity >= cutoff)

    rows = []
    for u in users:
        p = UserProfile.query.filter_by(user_id=u.id).first()
        rows.append(
            {
                'id': u.id,
                'email': u.email,
                'name': ' '.join(filter(None, [u.first_name or '', u.last_name or ''])).strip() or '—',
                'bmi_category': p.bmi_category if p else None,
                'daily_calories': int(p.daily_calories_needed) if p and p.daily_calories_needed else None,
                'activity_level': p.activity_level if p else None,
                'goal': p.goal if p else None,
                'dietary_notes': (p.dietary_notes[:200] + '…') if p and p.dietary_notes and len(p.dietary_notes or '') > 200 else (p.dietary_notes if p else None),
                'last_activity': u.last_activity.isoformat() + 'Z' if u.last_activity else None,
            }
        )

    return {
        'total_users': total,
        'active_users': active,
        'active_window_minutes': ACTIVE_MINUTES,
        'users': rows,
    }


@admin_bp.route('/api/admin/overview', methods=['GET'])
def admin_overview_api():
    key = request.headers.get('X-Admin-Key', '').strip()
    if not _admin_secret() or key != _admin_secret():
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(_build_overview())
