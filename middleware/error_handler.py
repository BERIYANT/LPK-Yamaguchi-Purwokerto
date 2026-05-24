from flask import render_template
import traceback

def register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        import traceback
        traceback.print_exc()
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the exception and traceback to console
        import sys
        traceback.print_exc()
        
        # Log the exception and traceback to wsgi_debug.log
        try:
            with open('/home/lpkd3153/yamaguchipwt/wsgi_debug.log', 'a') as f:
                f.write(f"\n--- REQUEST ERROR: {str(e)} ---\n")
                traceback.print_exc(file=f)
        except Exception as log_err:
            pass
            
        return render_template('errors/500.html'), 500