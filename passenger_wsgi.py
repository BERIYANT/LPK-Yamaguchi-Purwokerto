import sys
import os
import traceback

log_file_path = '/home/lpkd3153/yamaguchipwt/wsgi_debug.log'


try:
    with open(log_file_path, 'a') as f:
        f.write(f"\n--- STARTUP ATTEMPT: Python {sys.version} ---\n")
        variable_names = ('DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME', 'SECRET_KEY')
        present = [name for name in variable_names if os.getenv(name)]
        missing = [name for name in variable_names if not os.getenv(name)]
        f.write(f"Environment variables present: {', '.join(present) or 'none'}\n")
        f.write(f"Environment variables missing: {', '.join(missing) or 'none'}\n")
        
    # Menambahkan folder site-packages virtualenv secara eksplisit agar terbaca oleh Passenger cPanel
    sys.path.insert(0, '/home/lpkd3153/virtualenv/yamaguchipwt/3.13/lib/python3.13/site-packages')
    sys.path.insert(0, os.path.dirname(__file__))

    from app import app as application
    
    with open(log_file_path, 'a') as f:
        f.write("Flask app imported successfully!\n")
        
except Exception as e:
    with open(log_file_path, 'a') as f:
        f.write(f"Error occurred during startup: {str(e)}\n")
        traceback.print_exc(file=f)
    raise
