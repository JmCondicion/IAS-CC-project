from flask import Blueprint, request, jsonify
from app import db, limiter
from app.models import Student, AttendanceRecord
from app.utils.helpers import (
    generate_qr_code, 
    check_cooldown, 
    set_cooldown, 
    validate_request_data
)
from app.utils.schemas import student_schema, attendance_schema, scan_qr_schema
from marshmallow import ValidationError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)


@main_bp.route('/scan_qr', methods=['POST'])
@limiter.limit("10 per minute")
@validate_request_data(['qr_data'])
def scan_qr():
    """
    Scan QR code and record attendance.
    Validates against Student model, prevents duplicate scans within 10 mins.
    """
    try:
        data = request.get_json()
        qr_data = data['qr_data']
        
        # Find student by QR code
        student = Student.query.filter_by(qr_code=qr_data).first()
        
        if not student:
            return jsonify({
                'status': 'error',
                'message': 'Invalid QR code - Student not found'
            }), 404
        
        # Check cooldown
        if check_cooldown(student.id):
            return jsonify({
                'status': 'error',
                'message': 'Duplicate scan - Please wait 10 minutes before scanning again',
                'name': student.name,
                'time': datetime.now().isoformat()
            }), 400
        
        # Determine status (IN or OUT based on last record)
        last_record = AttendanceRecord.query.filter_by(
            student_id=student.id
        ).order_by(AttendanceRecord.timestamp.desc()).first()
        
        if last_record and last_record.status == 'IN':
            status = 'OUT'
        else:
            status = 'IN'
        
        # Create attendance record
        record = AttendanceRecord(
            student_id=student.id,
            status=status
        )
        
        db.session.add(record)
        db.session.commit()
        
        # Set cooldown
        set_cooldown(student.id)
        
        logger.info(f"Attendance recorded for {student.name} ({student.student_id}) - Status: {status}")
        
        return jsonify({
            'status': 'success',
            'name': student.name,
            'student_id': student.student_id,
            'time': record.timestamp.isoformat(),
            'status': status,
            'message': f'Attendance marked as {status}'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error scanning QR: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500


@main_bp.route('/attendance', methods=['GET'])
@limiter.limit("30 per minute")
def get_attendance():
    """
    Get paginated attendance records with optional filters.
    Query params: date (YYYY-MM-DD), student_id, page, per_page
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        date_filter = request.args.get('date')
        student_id_filter = request.args.get('student_id', type=int)
        
        query = AttendanceRecord.query
        
        # Apply filters
        if date_filter:
            try:
                target_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                query = query.filter(db.func.date(AttendanceRecord.timestamp) == target_date)
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        
        if student_id_filter:
            query = query.filter_by(student_id=student_id_filter)
        
        # Order by timestamp descending
        query = query.order_by(AttendanceRecord.timestamp.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        records = pagination.items
        
        return jsonify({
            'status': 'success',
            'records': [record.to_dict() for record in records],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching attendance: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500


@main_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
@validate_request_data(['student_id', 'name', 'course'])
def register_student():
    """
    Register a new student with a unique QR code.
    """
    try:
        data = request.get_json()
        student_id = data['student_id']
        name = data['name']
        course = data['course']
        
        # Validate using schema
        try:
            validated_data = student_schema.load(data)
        except ValidationError as err:
            return jsonify({
                'status': 'error',
                'message': err.messages
            }), 400
        
        # Check if student_id already exists
        existing_student = Student.query.filter_by(student_id=student_id).first()
        if existing_student:
            return jsonify({
                'status': 'error',
                'message': 'Student ID already exists'
            }), 400
        
        # Generate unique QR code
        qr_code = generate_qr_code()
        
        # Create student
        student = Student(
            student_id=student_id,
            name=name,
            course=course,
            qr_code=qr_code
        )
        
        db.session.add(student)
        db.session.commit()
        
        logger.info(f"New student registered: {name} ({student_id})")
        
        return jsonify({
            'status': 'success',
            'message': 'Student registered successfully',
            'student': student.to_dict(),
            'qr_code': qr_code
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registering student: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500


@main_bp.route('/students/<int:student_id>', methods=['GET'])
@limiter.limit("30 per minute")
def get_student(student_id):
    """Get a specific student by ID."""
    try:
        student = Student.query.get(student_id)
        
        if not student:
            return jsonify({
                'status': 'error',
                'message': 'Student not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'student': student.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching student: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500


@main_bp.route('/', methods=['GET'])
def index():
    """Serve the main frontend page."""
    from flask import render_template
    return render_template('index.html')
