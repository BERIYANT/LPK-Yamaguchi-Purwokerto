import pytest
from unittest.mock import patch, MagicMock
from app import app
from datetime import datetime

class MockRow(dict):
    def __getitem__(self, key):
        if key in self:
            return super().__getitem__(key)
        if key == 'id': return 1
        if key == 'role': return 'admin'
        if key == 'role_id': return 1
        if key == 'username': return 'test_user'
        if key == 'password': return 'hashed'
        if key == 'title': return 'Test Title'
        if key == 'name': return 'Test Name'
        if key == 'description': return 'Test Desc'
        if any(x in key for x in ['_time', '_date', '_at', 'tanggal', 'waktu']): return datetime.now()
        if 'total' in key or 'count' in key: return 10
        if 'id' in key: return 1
        if 'amount' in key or 'fee' in key: return 50000
        if key == 'content': return 'Mock Content'
        if key == 'file_path': return 'dummy.pdf'
        if key == 'status': return 'active'
        return f"mock_{key}"

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

@pytest.fixture(autouse=True)
def mock_db_global():
    with patch('mysql.connector.connect') as mock_conn:
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.return_value = mock_db
        mock_db.cursor.return_value = mock_cursor

        def fetchone_side_effect(*args, **kwargs):
            return MockRow()

        def fetchall_side_effect(*args, **kwargs):
            return [MockRow(), MockRow()]

        mock_cursor.fetchone.side_effect = fetchone_side_effect
        mock_cursor.fetchall.side_effect = fetchall_side_effect
        
        # Bypass file storage operations to avoid errors
        with patch('werkzeug.datastructures.FileStorage.save'), \
             patch('os.path.exists', return_value=True), \
             patch('os.remove', return_value=True):
            yield mock_conn

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = True
    with app.test_client() as client:
        # Patch jinja globals if missing
        if 'csrf_token' not in app.jinja_env.globals:
            app.jinja_env.globals['csrf_token'] = lambda: ''
        yield client

@pytest.fixture
def logged_in_admin(client):
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['user_id'] = 1
        sess['user_role'] = 'admin'
        sess['username'] = 'admin'
    return client

@pytest.fixture
def logged_in_teacher(client):
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['user_id'] = 2
        sess['user_role'] = 'sensei'
        sess['username'] = 'teacher1'
        sess['selected_class_id'] = 1
    return client

@pytest.fixture
def logged_in_student(client):
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['user_id'] = 3
        sess['user_role'] = 'student'
        sess['username'] = 'student1'
        sess['class_id'] = 1
    return client


ADMIN_ROUTES = [
    '/admin/dashboard',
    '/admin/users',
    '/admin/classes',
    '/admin/certificates',
    '/admin/payments',
    '/admin/activities',
    '/admin/job/create',
    '/admin/jobs',
    '/admin/finance',
    '/admin/finance/transactions',
    '/admin/finance/report'
]

TEACHER_ROUTES = [
    '/teacher/dashboard',
    '/teacher/attendance/list',
    '/teacher/bank/',
    '/teacher/bank/material/',
    '/teacher/bank/assignment/'
]

STUDENT_ROUTES = [
    '/student/dashboard',
    '/student/attendance/history',
    '/student/my-certificates',
    '/student/my-quiz-history',
    '/student/my-task-scores'
]

PUBLIC_ROUTES = [
    '/',
    '/login',
    '/register',
    '/register-student',
    '/forum'
]

@pytest.mark.parametrize("route", ADMIN_ROUTES)
def test_admin_routes(logged_in_admin, route):
    response = logged_in_admin.get(route)
    assert response.status_code in [200, 302, 308] # Allow ok or redirect

@pytest.mark.parametrize("route", TEACHER_ROUTES)
def test_teacher_routes(logged_in_teacher, route):
    response = logged_in_teacher.get(route)
    assert response.status_code in [200, 302, 308]

@pytest.mark.parametrize("route", STUDENT_ROUTES)
def test_student_routes(logged_in_student, route):
    response = logged_in_student.get(route)
    assert response.status_code in [200, 302, 308]

@pytest.mark.parametrize("route", PUBLIC_ROUTES)
def test_public_routes(client, route):
    response = client.get(route)
    assert response.status_code in [200, 302, 308]

# Custom parameterized views that might need DB IDs
def test_specific_features_admin(logged_in_admin):
    # Test edit and view endpoints randomly to ensure no 500
    res = logged_in_admin.get('/admin/user/1/edit')
    assert res.status_code in [200, 302]
    
    res = logged_in_admin.get('/admin/class/1/edit')
    assert res.status_code in [200, 302]
    
    res = logged_in_admin.get('/admin/job/1/edit')
    assert res.status_code in [200, 302]

def test_specific_features_forum(logged_in_student):
    res = logged_in_student.get('/forum/post/1')
    assert res.status_code in [200, 302]

def test_specific_features_assignment(logged_in_student):
    res = logged_in_student.get('/student/assignment/1')
    assert res.status_code in [200, 302]

def test_specific_features_teacher(logged_in_teacher):
    res = logged_in_teacher.get('/teacher/quiz/1/edit')
    assert res.status_code in [200, 302]
    
    res = logged_in_teacher.get('/teacher/assignment/1/edit')
    assert res.status_code in [200, 302]

    res = logged_in_teacher.get('/teacher/attendance/report/1')
    assert res.status_code in [200, 302]

