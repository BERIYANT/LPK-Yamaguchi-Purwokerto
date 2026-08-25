import sys
import os
import traceback

log_file_path = '/home/lpkd3153/yamaguchipwt/wsgi_debug.log'


def load_private_environment():
    """Load cPanel-only variables when LiteSpeed omits PassengerEnvVar."""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.isfile(env_path):
        return

    with open(env_path, encoding='utf-8-sig') as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            name, value = line.split('=', 1)
            name = name.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            # File ini privat dan khusus production; nilainya harus mengganti
            # environment lama/fallback yang mungkin diwariskan Passenger.
            os.environ[name] = value


load_private_environment()

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
