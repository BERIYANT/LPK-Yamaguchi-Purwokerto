from flask import Blueprint
from utils.authentication import login_required

quiz_bp = Blueprint('quiz', __name__)

# Routes are handled in student_controller and teacher_controller
# This blueprint is for organization purposes