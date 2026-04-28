import pytest
from unittest.mock import patch, MagicMock
from app import app
from flask import session
from datetime import datetime

@pytest.fixture(autouse=True)
def fake_db_connection():
    """Mocking koneksi database MySQL secara global agar tidak ada error."""
    with patch('mysql.connector.connect') as mock_conn:
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.return_value = mock_db
        mock_db.cursor.return_value = mock_cursor

        def fetchone_side_effect(*args, **kwargs):
            return {'id': 1, 'role': 'sensei', 'username': 'guru123', 'created_by': 1, 'created_at': datetime.now(), 'password': 'hashed_password_dummy'}

        mock_cursor.fetchone.side_effect = fetchone_side_effect
        yield mock_conn

@pytest.fixture
def client():
    """Fixture untuk environment testing Flask."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def logged_in_teacher_client(client):
    """Fixture khusus yang mensimulasikan sesi guru (sensei)."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'sensei'
        sess['username'] = 'guru123'
    return client

# ==========================================
# 1. GENERAL ROUTING & MIDDLEWARE TESTS
# ==========================================

def test_index_page(client):
    """Path coverage - Test routing index utama (berhasil HTTP 200 / Dialihkan)."""
    response = client.get('/')
    assert response.status_code in [200, 302]

def test_dashboard_unauthorized(client):
    """Security coverage - Tolak akses dashboard bagi user yang belum login."""
    response = client.get('/admin/dashboard')
    assert response.status_code == 302
    assert '/login' in response.headers.get('Location', '')

@patch('controllers.auth_controller.render_template')
def test_login_invalid(mock_render, client):
    """Branch statement coverage - Test respon saat login gagal (username salah)."""
    # Mem-bypass masalah render WTForms / CSRF error pada unit test murni
    mock_render.return_value = "Login Gagal Disimulasikan"
    
    response = client.post('/login', data={
        'username': 'fakeuser',
        'password': 'wrongpassword'
    }, follow_redirects=False)
    
    # Harapanya akan dikembalikan view form login dengan error message (HTTP 200)
    assert response.status_code == 200
    assert mock_render.called

# ==========================================
# 2. QUESTION BANK CONTROLLER TESTS
# ==========================================

@patch('models.question_bank_model.QuestionBankModel.get_by_teacher')
@patch('models.question_bank_model.AssignmentBankModel.get_by_teacher')
@patch('models.question_bank_model.MaterialBankModel.get_by_teacher')
def test_bank_index(mock_material, mock_assignment, mock_question, logged_in_teacher_client):
    """Integration & Path coverage - Tampilkan list bank soal untuk guru."""
    mock_question.return_value = [{'id': 1, 'name': 'Bank Matematika'}]
    mock_assignment.return_value = []
    mock_material.return_value = []
    
    response = logged_in_teacher_client.get('/teacher/bank/')
    assert response.status_code == 200

@patch('models.question_bank_model.QuestionBankModel.create')
def test_create_bank_success(mock_create_bank, logged_in_teacher_client):
    """Branch statement coverage - Sukses menambah bank soal baru."""
    mock_create_bank.return_value = 1
    
    response = logged_in_teacher_client.post('/teacher/bank/create', data={
        'name': 'Bank Fisika Terpadu',
        'description': 'Latihan soal persiapan ujian nasional'
    }, follow_redirects=False)
    
    # Redirect ke halaman detail bank soal
    assert response.status_code == 302 
    mock_create_bank.assert_called_once_with('Bank Fisika Terpadu', 1, 'Latihan soal persiapan ujian nasional')

@patch('models.question_bank_model.QuestionBankModel.get_by_id')
@patch('models.question_bank_model.QuestionBankModel.delete')
def test_delete_bank_success(mock_delete, mock_get, logged_in_teacher_client):
    """Branch statement coverage - Sukses menghapus bank soal."""
    # Mock data return dari db
    mock_get.return_value = {'id': 1, 'name': 'Bank yang Ingin Dihapus', 'created_by': 1}
    
    response = logged_in_teacher_client.get('/teacher/bank/1/delete', follow_redirects=False)
    
    # Redirect ke halaman index bank soal setelah dihapus
    assert response.status_code == 302
    mock_delete.assert_called_once_with(1)

def test_bank_index_unauthorized(client):
    """Security coverage - Memastikan URL teacher hanya bisa diakses sensei."""
    response = client.get('/teacher/bank/')
    assert response.status_code == 302
    assert '/login' in response.headers.get('Location', '')
