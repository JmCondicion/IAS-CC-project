from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime


class StudentSchema(Schema):
    id = fields.Int(dump_only=True)
    student_id = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    course = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    qr_code = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    
    @validates('student_id')
    def validate_student_id(self, value):
        if not value.strip():
            raise ValidationError('Student ID cannot be empty')


class AttendanceRecordSchema(Schema):
    id = fields.Int(dump_only=True)
    student_id = fields.Int(required=True)
    student_name = fields.Str(dump_only=True)
    timestamp = fields.DateTime(dump_only=True)
    status = fields.Str(validate=validate.OneOf(['IN', 'OUT']))


class ScanQRSchema(Schema):
    qr_data = fields.Str(required=True, validate=validate.Length(min=1))


class AttendanceListSchema(Schema):
    records = fields.Nested(AttendanceRecordSchema, many=True)
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
    pages = fields.Int()


# Instance schemas for single objects
student_schema = StudentSchema()
students_schema = StudentSchema(many=True)
attendance_schema = AttendanceRecordSchema()
attendance_list_schema = AttendanceListSchema()
scan_qr_schema = ScanQRSchema()
