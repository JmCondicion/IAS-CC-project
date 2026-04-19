import uuid
import redis
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import jsonify


# In-memory cooldown cache (fallback if Redis is not available)
cooldown_cache = {}


def get_redis_client():
    """Get Redis client if available, otherwise return None."""
    try:
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        client = redis.from_url(redis_url)
        client.ping()  # Test connection
        return client
    except Exception:
        return None


def generate_qr_code():
    """Generate a unique QR code string."""
    return str(uuid.uuid4())


def check_cooldown(student_id, cooldown_minutes=10):
    """
    Check if a student is within the cooldown period.
    Returns True if within cooldown (should block), False otherwise.
    """
    redis_client = get_redis_client()
    
    if redis_client:
        # Use Redis for distributed caching
        key = f"cooldown:{student_id}"
        ttl = redis_client.ttl(key)
        if ttl > 0:
            return True
        return False
    else:
        # Fallback to in-memory cache
        now = datetime.now()
        if student_id in cooldown_cache:
            last_scan, cooldown_end = cooldown_cache[student_id]
            if now < cooldown_end:
                return True
            else:
                del cooldown_cache[student_id]
        return False


def set_cooldown(student_id, cooldown_minutes=10):
    """Set cooldown for a student."""
    redis_client = get_redis_client()
    cooldown_end = datetime.now() + timedelta(minutes=cooldown_minutes)
    
    if redis_client:
        key = f"cooldown:{student_id}"
        redis_client.setex(key, cooldown_minutes * 60, str(cooldown_end.isoformat()))
    else:
        cooldown_cache[student_id] = (datetime.now(), cooldown_end)


def validate_request_data(required_fields):
    """Decorator to validate request JSON data."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'status': 'error',
                    'message': 'Missing JSON payload'
                }), 400
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
