from utils.database import get_db
from datetime import datetime, date, timedelta
import qrcode
import io
import base64
import secrets

class AttendanceModel:
    # Attendance session duration in minutes
    ATTENDANCE_DURATION_MINUTES = 5
    
    @staticmethod
    def create_attendance_session(class_id, teacher_id, date, description=''):
        """Create a new attendance session with a unique barcode"""
        db = get_db()
        cur = db.cursor()
        
        # Generate unique token for barcode
        token = secrets.token_urlsafe(32)
        
        # Set expiry time to 5 minutes from now
        expires_at = datetime.now() + timedelta(minutes=AttendanceModel.ATTENDANCE_DURATION_MINUTES)
        
        cur.execute(
            """INSERT INTO attendance_sessions 
            (class_id, teacher_id, date, token, description, is_active, expires_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (class_id, teacher_id, date, token, description, 1, expires_at)
        )
        db.commit()
        session_id = cur.lastrowid
        cur.close()
        return session_id, token

    @staticmethod
    def get_session_by_token(token):
        """Get attendance session by token"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            """SELECT s.*, c.name as class_name, u.full_name as teacher_name 
            FROM attendance_sessions s
            JOIN classes c ON s.class_id = c.id
            JOIN users u ON s.teacher_id = u.id
            WHERE s.token = %s""",
            (token,)
        )
        session = cur.fetchone()
        cur.close()
        return session

    @staticmethod
    def get_session_by_id(session_id):
        """Get attendance session by ID"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            """SELECT s.*, c.name as class_name, u.full_name as teacher_name 
            FROM attendance_sessions s
            JOIN classes c ON s.class_id = c.id
            JOIN users u ON s.teacher_id = u.id
            WHERE s.id = %s""",
            (session_id,)
        )
        session = cur.fetchone()
        cur.close()
        return session

    @staticmethod
    def deactivate_session(session_id):
        """Deactivate an attendance session"""
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "UPDATE attendance_sessions SET is_active = 0 WHERE id = %s",
            (session_id,)
        )
        db.commit()
        cur.close()

    @staticmethod
    def refresh_token(session_id):
        """Refresh the barcode token and extend expiry by 5 minutes"""
        db = get_db()
        cur = db.cursor()
        
        # Generate new token
        new_token = secrets.token_urlsafe(32)
        
        # Extend expiry time by 5 minutes from now
        new_expires_at = datetime.now() + timedelta(minutes=AttendanceModel.ATTENDANCE_DURATION_MINUTES)
        
        cur.execute(
            """UPDATE attendance_sessions 
            SET token = %s, expires_at = %s 
            WHERE id = %s""",
            (new_token, new_expires_at, session_id)
        )
        db.commit()
        cur.close()
        return new_token, new_expires_at

    @staticmethod
    def is_session_expired(session_id):
        """Check if session has expired"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT expires_at FROM attendance_sessions WHERE id = %s",
            (session_id,)
        )
        session = cur.fetchone()
        cur.close()
        
        if not session or not session['expires_at']:
            return False
        
        return datetime.now() > session['expires_at']

    @staticmethod
    def record_attendance(session_id, student_id):
        """Record student attendance"""
        db = get_db()
        cur = db.cursor()
        
        # Check if already recorded
        cur.execute(
            """SELECT id FROM attendance_records 
            WHERE session_id = %s AND student_id = %s""",
            (session_id, student_id)
        )
        existing = cur.fetchone()
        
        if existing:
            cur.close()
            return None  # Already recorded
        
        # Record attendance
        cur.execute(
            """INSERT INTO attendance_records 
            (session_id, student_id, timestamp) 
            VALUES (%s, %s, %s)""",
            (session_id, student_id, datetime.now())
        )
        db.commit()
        record_id = cur.lastrowid
        cur.close()
        return record_id

    @staticmethod
    def get_attendance_records(session_id):
        """Get all attendance records for a session"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            """SELECT r.*, u.full_name, u.username 
            FROM attendance_records r
            JOIN users u ON r.student_id = u.id
            WHERE r.session_id = %s
            ORDER BY r.timestamp ASC""",
            (session_id,)
        )
        records = cur.fetchall()
        cur.close()
        return records

    @staticmethod
    def get_sessions_by_teacher(teacher_id, date_filter=None):
        """Get all sessions created by a teacher, optionally filtered by date"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        if date_filter:
            cur.execute(
                """SELECT s.*, c.name as class_name,
                (SELECT COUNT(*) FROM attendance_records WHERE session_id = s.id) as total_attendance
                FROM attendance_sessions s
                JOIN classes c ON s.class_id = c.id
                WHERE s.teacher_id = %s AND s.date = %s
                ORDER BY s.created_at DESC""",
                (teacher_id, date_filter)
            )
        else:
            cur.execute(
                """SELECT s.*, c.name as class_name,
                (SELECT COUNT(*) FROM attendance_records WHERE session_id = s.id) as total_attendance
                FROM attendance_sessions s
                JOIN classes c ON s.class_id = c.id
                WHERE s.teacher_id = %s
                ORDER BY s.created_at DESC""",
                (teacher_id,)
            )
        
        sessions = cur.fetchall()
        cur.close()
        return sessions

    @staticmethod
    def get_all_sessions(date_filter=None):
        """Get all attendance sessions (for admin), optionally filtered by date"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        if date_filter:
            cur.execute(
                """SELECT s.*, c.name as class_name, u.full_name as teacher_name,
                (SELECT COUNT(*) FROM attendance_records WHERE session_id = s.id) as total_attendance
                FROM attendance_sessions s
                JOIN classes c ON s.class_id = c.id
                JOIN users u ON s.teacher_id = u.id
                WHERE s.date = %s
                ORDER BY s.created_at DESC""",
                (date_filter,)
            )
        else:
            cur.execute(
                """SELECT s.*, c.name as class_name, u.full_name as teacher_name,
                (SELECT COUNT(*) FROM attendance_records WHERE session_id = s.id) as total_attendance
                FROM attendance_sessions s
                JOIN classes c ON s.class_id = c.id
                JOIN users u ON s.teacher_id = u.id
                ORDER BY s.created_at DESC""",
            )
        
        sessions = cur.fetchall()
        cur.close()
        return sessions

    @staticmethod
    def generate_barcode_image(token, base_url):
        """Generate QR code image from token"""
        # Create QR code with attendance URL
        url = f"{base_url}/student/attendance/scan?token={token}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return img_str

    @staticmethod
    def get_student_attendance_history(student_id, limit=20):
        """Get student's attendance history"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            """SELECT r.*, s.date, s.description, c.name as class_name
            FROM attendance_records r
            JOIN attendance_sessions s ON r.session_id = s.id
            JOIN classes c ON s.class_id = c.id
            WHERE r.student_id = %s
            ORDER BY r.timestamp DESC
            LIMIT %s""",
            (student_id, limit)
        )
        records = cur.fetchall()
        cur.close()
        return records

    @staticmethod
    def get_class_students(class_id):
        """Get all students in a class (uses enrollments table)."""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            """SELECT u.id, u.username, u.full_name
            FROM users u
            JOIN enrollments e ON u.id = e.user_id
            WHERE e.class_id = %s AND u.role = 'student'
            ORDER BY u.full_name""",
            (class_id,)
        )
        students = cur.fetchall()
        cur.close()
        return students

    @staticmethod
    def get_attendance_summary(session_id):
        """Get attendance summary with present and absent students"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        # Get session info
        session = AttendanceModel.get_session_by_id(session_id)
        if not session:
            return None
        
        # Get all students in the class
        all_students = AttendanceModel.get_class_students(session['class_id'])
        
        # Get students who attended
        cur.execute(
            """SELECT student_id FROM attendance_records WHERE session_id = %s""",
            (session_id,)
        )
        present_ids = [row['student_id'] for row in cur.fetchall()]
        cur.close()
        
        # Categorize students
        present_students = [s for s in all_students if s['id'] in present_ids]
        absent_students = [s for s in all_students if s['id'] not in present_ids]
        
        return {
            'session': session,
            'total_students': len(all_students),
            'present_count': len(present_students),
            'absent_count': len(absent_students),
            'present_students': present_students,
            'absent_students': absent_students
        }
