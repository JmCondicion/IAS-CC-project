from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from app import db


class Student(db.Model):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    course = Column(String(100), nullable=False)
    qr_code = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to attendance records
    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'course': self.course,
            'qr_code': self.qr_code,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Student {self.name} ({self.student_id})>'


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    status = Column(String(10), nullable=False)  # 'IN' or 'OUT'
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_student_timestamp', 'student_id', 'timestamp'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'status': self.status
        }
    
    def __repr__(self):
        return f'<AttendanceRecord {self.student_id} - {self.status} at {self.timestamp}>'
