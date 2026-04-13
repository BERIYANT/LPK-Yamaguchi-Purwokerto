import sys
import os

# path ke folder aplikasi
sys.path.insert(0, os.path.dirname(__file__))

from app import app as application
