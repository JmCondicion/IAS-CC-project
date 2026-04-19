from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, limiter
from app.models import Student, AttendanceRecord
from datetime import datetime
import os

admin_bp = Blueprint('admin', __name__)


class AdminUser:
    """Simple admin user class for Flask-Login."""
    def __init__(self, username):
        self.username = username
        self.id = username
    
    def get_id(self):
        return self.username
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False


@admin_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """Admin login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        expected_username = os.getenv('ADMIN_USERNAME', 'admin')
        expected_password = os.getenv('ADMIN_PASSWORD', 'admin')
        
        if username == expected_username and password == expected_password:
            user = AdminUser(username)
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def logout():
    """Admin logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard showing attendance statistics."""
    today = datetime.now().date()
    
    # Get today's attendance count
    today_count = AttendanceRecord.query.filter(
        db.func.date(AttendanceRecord.timestamp) == today
    ).count()
    
    # Get total students
    total_students = Student.query.count()
    
    # Get recent records
    recent_records = AttendanceRecord.query.order_by(
        AttendanceRecord.timestamp.desc()
    ).limit(20).all()
    
    return render_template('admin/dashboard.html', 
                         today_count=today_count,
                         total_students=total_students,
                         recent_records=recent_records)


@admin_bp.route('/students')
@login_required
def manage_students():
    """Manage students page."""
    students = Student.query.order_by(Student.created_at.desc()).all()
    return render_template('admin/students.html', students=students)


@admin_bp.route('/attendance')
@login_required
def view_attendance():
    """View all attendance records."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    pagination = AttendanceRecord.query.order_by(
        AttendanceRecord.timestamp.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/attendance.html', 
                         records=pagination.items,
                         pagination=pagination)
