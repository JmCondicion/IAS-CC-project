from app import login_manager
from app.routes.admin import AdminUser
import os


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    expected_username = os.getenv('ADMIN_USERNAME', 'admin')
    if user_id == expected_username:
        return AdminUser(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Handle unauthorized access."""
    from flask import redirect, url_for
    return redirect(url_for('admin.login'))
