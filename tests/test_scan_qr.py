import pytest
from app import create_app, db
from app.models import Student, AttendanceRecord
from datetime import datetime, timedelta
import json


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['RATELIMIT_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_student(app):
    """Create a sample student for testing."""
    with app.app_context():
        student = Student(
            student_id='STU001',
            name='John Doe',
            course='Computer Science',
            qr_code='test-qr-code-123'
        )
        db.session.add(student)
        db.session.commit()
        return student


class TestScanQR:
    """Test cases for /scan_qr endpoint."""
    
    def test_valid_scan(self, client, sample_student):
        """Test valid QR code scan."""
        response = client.post(
            '/api/scan_qr',
            data=json.dumps({'qr_data': 'test-qr-code-123'}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['name'] == 'John Doe'
        assert data['status'] == 'IN'
        
        # Verify record was created
        record = AttendanceRecord.query.first()
        assert record is not None
        assert record.student_id == sample_student.id
    
    def test_invalid_qr_code(self, client):
        """Test invalid QR code that doesn't match any student."""
        response = client.post(
            '/api/scan_qr',
            data=json.dumps({'qr_data': 'invalid-qr-code'}),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'not found' in data['message'].lower()
    
    def test_duplicate_scan_within_cooldown(self, client, sample_student, monkeypatch):
        """Test duplicate scan within 10 minute cooldown period."""
        # Mock check_cooldown to always return True (within cooldown)
        from app.utils import helpers
        monkeypatch.setattr(helpers, 'check_cooldown', lambda student_id, cooldown_minutes=10: True)
        
        response = client.post(
            '/api/scan_qr',
            data=json.dumps({'qr_data': 'test-qr-code-123'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'duplicate' in data['message'].lower() or 'wait' in data['message'].lower()
    
    def test_missing_payload(self, client):
        """Test request with missing JSON payload."""
        response = client.post(
            '/api/scan_qr',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'missing' in data['message'].lower()
    
    def test_db_error_handling(self, client, sample_student, monkeypatch):
        """Test database error handling."""
        # Mock db.session.commit to raise an exception
        def mock_commit():
            raise Exception("Database connection error")
        
        monkeypatch.setattr(db.session, 'commit', mock_commit)
        
        response = client.post(
            '/api/scan_qr',
            data=json.dumps({'qr_data': 'test-qr-code-123'}),
            content_type='application/json'
        )
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'internal server error' in data['message'].lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
