from flask import render_template, request, redirect, url_for, flash, g, send_file, jsonify
from datetime import datetime, date, timedelta
import os
import base64
import io
from PIL import Image
from utils.database import get_db
from config import Config
import calendar
from decimal import Decimal

def init_routes(app):
    
    @app.route('/')
    def index():
        # Keep the public landing page independent from MySQL availability.
        # Its programs and facilities are defined directly in the template.
        return render_template('index.html')

    @app.route('/profile')
    def profile():
        if not g.user:
            flash("Silakan login terlebih dahulu.")
            return redirect(url_for('auth.login'))
        
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT id, username, full_name, role, bio, avatar FROM users WHERE id=%s", (g.user['id'],))
        user = cur.fetchone()
        cur.close()
        
        if not user:
            flash("Profil tidak ditemukan.")
            return redirect(url_for('index'))
        
        return render_template('profile.html', user=user)

    # ==============================================
    # FINANCE ROUTES - SIMPLE IMPLEMENTATION
    # ==============================================
    
    @app.route('/admin/finance')
    def finance_dashboard():
        """Dashboard keuangan sederhana"""
        if not g.user or g.user.get('role') != 'admin':
            flash('Akses ditolak. Hanya admin yang dapat mengakses.', 'danger')
            return redirect(url_for('index'))
        
        # Get current year and month
        today = date.today()
        year = request.args.get('year', today.year, type=int)
        month = request.args.get('month', today.month, type=int)
        
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        try:
            # Total Income for selected month
            cur.execute("""
                SELECT COALESCE(SUM(amount), 0) as total_income
                FROM finance_transactions 
                WHERE type = 'income' 
                AND YEAR(transaction_date) = %s 
                AND MONTH(transaction_date) = %s
            """, (year, month))
            income_result = cur.fetchone()
            total_income = float(income_result['total_income'] or 0)
            
            # Total Expense for selected month
            cur.execute("""
                SELECT COALESCE(SUM(amount), 0) as total_expense
                FROM finance_transactions 
                WHERE type = 'expense' 
                AND YEAR(transaction_date) = %s 
                AND MONTH(transaction_date) = %s
            """, (year, month))
            expense_result = cur.fetchone()
            total_expense = float(expense_result['total_expense'] or 0)
            
            # Current Balance (all time)
            cur.execute("""
                SELECT 
                    COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_all_income,
                    COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_all_expense
                FROM finance_transactions
            """)
            all_result = cur.fetchone()
            current_balance = float(all_result['total_all_income'] or 0) - float(all_result['total_all_expense'] or 0)
            
            # Recent transactions (last 10)
            cur.execute("""
                SELECT ft.*, u.full_name as created_by_name
                FROM finance_transactions ft
                JOIN users u ON ft.created_by = u.id
                ORDER BY ft.transaction_date DESC, ft.created_at DESC
                LIMIT 10
            """)
            recent_transactions = cur.fetchall()
            
            # Top categories
            cur.execute("""
                SELECT type, category, SUM(amount) as total, COUNT(*) as count
                FROM finance_transactions
                WHERE YEAR(transaction_date) = %s AND MONTH(transaction_date) = %s
                GROUP BY type, category
                ORDER BY total DESC
                LIMIT 5
            """, (year, month))
            top_categories = cur.fetchall()
            
            # Monthly summary for chart
            cur.execute("""
                SELECT 
                    MONTH(transaction_date) as month,
                    SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income,
                    SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expense
                FROM finance_transactions
                WHERE YEAR(transaction_date) = %s
                GROUP BY MONTH(transaction_date)
                ORDER BY month
            """, (year,))
            monthly_data = cur.fetchall()
            
        except Exception as e:
            print(f"Error loading finance dashboard: {str(e)}")
            total_income = 0
            total_expense = 0
            current_balance = 0
            recent_transactions = []
            top_categories = []
            monthly_data = []
        
        cur.close()
        
        # Format currency function
        def format_currency(value):
            return f"Rp {value:,.0f}".replace(',', '.')
        
        # Month names
        month_names = [
            'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
            'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
        ]
        
        return render_template('admin/finance/dashboard.html',
                             total_income=total_income,
                             total_expense=total_expense,
                             current_balance=current_balance,
                             net_income=total_income - total_expense,
                             recent_transactions=recent_transactions,
                             top_categories=top_categories,
                             monthly_data=monthly_data,
                             current_year=year,
                             current_month=month,
                             month_name=month_names[month-1],
                             format_currency=format_currency)
    
    @app.route('/admin/finance/transactions')
    def finance_transactions():
        """View all transactions"""
        if not g.user or g.user.get('role') != 'admin':
            flash('Akses ditolak. Hanya admin yang dapat mengakses.', 'danger')
            return redirect(url_for('index'))
        
        # Get filters
        transaction_type = request.args.get('type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search = request.args.get('search')
        
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        # Build query with filters
        where_clause = "1=1"
        params = []
        
        if transaction_type in ['income', 'expense']:
            where_clause += " AND ft.type = %s"
            params.append(transaction_type)
        
        if start_date:
            where_clause += " AND ft.transaction_date >= %s"
            params.append(start_date)
        
        if end_date:
            where_clause += " AND ft.transaction_date <= %s"
            params.append(end_date)
        
        if search:
            where_clause += " AND (ft.description LIKE %s OR ft.reference_number LIKE %s OR ft.category LIKE %s)"
            params.append(f"%{search}%")
            params.append(f"%{search}%")
            params.append(f"%{search}%")
        
        # Get transactions
        query = f"""
            SELECT ft.*, 
                   u.full_name as created_by_name,
                   u.username as created_by_username
            FROM finance_transactions ft
            JOIN users u ON ft.created_by = u.id
            WHERE {where_clause}
            ORDER BY ft.transaction_date DESC, ft.created_at DESC
        """
        
        cur.execute(query, tuple(params))
        transactions = cur.fetchall()
        
        # Get summary stats
        cur.execute(f"""
            SELECT 
                COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_income,
                COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_expense
            FROM finance_transactions ft
            WHERE {where_clause}
        """, tuple(params))
        stats = cur.fetchone()
        
        # Get unique categories for filter
        cur.execute("SELECT DISTINCT category FROM finance_transactions ORDER BY category")
        categories = [row['category'] for row in cur.fetchall()]
        
        cur.close()
        
        def format_currency(value):
            return f"Rp {value:,.0f}".replace(',', '.')
        
        return render_template('admin/finance/transactions.html',
                             transactions=transactions,
                             total_income=float(stats['total_income'] or 0),
                             total_expense=float(stats['total_expense'] or 0),
                             categories=categories,
                             filters={
                                 'type': transaction_type,
                                 'start_date': start_date,
                                 'end_date': end_date,
                                 'search': search
                             },
                             format_currency=format_currency)
    
    @app.route('/admin/finance/transaction/create', methods=['GET', 'POST'])
    def create_finance_transaction():
        """Create new transaction"""
        if not g.user or g.user.get('role') != 'admin':
            flash('Akses ditolak. Hanya admin yang dapat mengakses.', 'danger')
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            try:
                # Get form data
                transaction_type = request.form['type']
                category = request.form['category'].strip()
                
                # Handle amount
                amount_str = request.form['amount'].replace('.', '').replace(',', '')
                try:
                    amount = Decimal(amount_str)
                except:
                    flash('Format jumlah tidak valid. Gunakan angka saja.', 'danger')
                    return redirect(url_for('create_finance_transaction'))
                
                description = request.form.get('description', '').strip()
                payment_method = request.form.get('payment_method', '').strip()
                reference_number = request.form.get('reference_number', '').strip()
                transaction_date = request.form['transaction_date']
                
                # Validate
                if not transaction_type or not category or amount <= 0 or not transaction_date:
                    flash('Harap isi semua field yang wajib diisi.', 'danger')
                    return redirect(url_for('create_finance_transaction'))
                
                # Handle file upload
                attachment_path = None
                file = request.files.get('attachment')
                if file and file.filename:
                    # Simple validation
                    allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png', 'gif'}
                    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                        flash('Format file tidak diizinkan. Gunakan PDF, JPG, PNG, atau GIF.', 'danger')
                        return redirect(url_for('create_finance_transaction'))
                    
                    # Save file
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    original_filename = file.filename
                    extension = original_filename.rsplit('.', 1)[1].lower()
                    safe_filename = f"finance_{transaction_type}_{timestamp}.{extension}"
                    
                    upload_folder = Config.UPLOAD_FOLDER
                    os.makedirs(upload_folder, exist_ok=True)
                    file.save(os.path.join(upload_folder, safe_filename))
                    attachment_path = safe_filename
                
                # Insert into database
                db = get_db()
                cur = db.cursor()
                
                cur.execute("""
                    INSERT INTO finance_transactions 
                    (type, category, amount, description, payment_method, 
                     reference_number, transaction_date, created_by, attachment_path)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    transaction_type,
                    category,
                    amount,
                    description,
                    payment_method,
                    reference_number,
                    transaction_date,
                    g.user['id'],
                    attachment_path
                ))
                
                db.commit()
                cur.close()
                
                flash(f'Transaksi berhasil ditambahkan!', 'success')
                return redirect(url_for('finance_transactions'))
                
            except Exception as e:
                print(f"Error creating transaction: {str(e)}")
                flash(f'Terjadi kesalahan: {str(e)}', 'danger')
                return redirect(url_for('create_finance_transaction'))
        
        # GET request - show form
        default_date = date.today().strftime('%Y-%m-%d')
        
        # Get existing categories
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT DISTINCT category, type FROM finance_transactions ORDER BY type, category")
        categories = cur.fetchall()
        cur.close()
        
        # Common categories
        common_categories = {
            'income': ['Pendaftaran', 'Pendidikan', 'Sertifikasi', 'Magang', 'Donasi', 'Lainnya'],
            'expense': ['Gaji Pengajar', 'Operasional', 'Sewa Tempat', 'ATK', 'Internet & Listrik', 
                       'Pemeliharaan', 'Transportasi', 'Konsumsi', 'Lainnya']
        }
        
        return render_template('admin/finance/create_transaction.html',
                             default_date=default_date,
                             categories=categories,
                             common_categories=common_categories)
    
    @app.route('/admin/finance/transaction/<int:transaction_id>/edit', methods=['GET', 'POST'])
    def edit_finance_transaction(transaction_id):
        """Edit transaction"""
        if not g.user or g.user.get('role') != 'admin':
            flash('Akses ditolak. Hanya admin yang dapat mengakses.', 'danger')
            return redirect(url_for('index'))
        
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        try:
            # Get transaction
            cur.execute("""
                SELECT ft.*, u.full_name as created_by_name
                FROM finance_transactions ft
                JOIN users u ON ft.created_by = u.id
                WHERE ft.id = %s
            """, (transaction_id,))
            transaction = cur.fetchone()
            
            if not transaction:
                flash('Transaksi tidak ditemukan.', 'danger')
                cur.close()
                return redirect(url_for('finance_transactions'))
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
            cur.close()
            return redirect(url_for('finance_transactions'))
        
        if request.method == 'POST':
            try:
                # Get form data
                transaction_type = request.form['type']
                category = request.form['category'].strip()
                
                # Handle amount
                amount_str = request.form['amount'].replace('.', '').replace(',', '')
                try:
                    amount = Decimal(amount_str)
                except:
                    flash('Format jumlah tidak valid.', 'danger')
                    return redirect(url_for('edit_finance_transaction', transaction_id=transaction_id))
                
                description = request.form.get('description', '').strip()
                payment_method = request.form.get('payment_method', '').strip()
                reference_number = request.form.get('reference_number', '').strip()
                transaction_date = request.form['transaction_date']
                
                # Validate
                if not transaction_type or not category or amount <= 0 or not transaction_date:
                    flash('Harap isi semua field yang wajib diisi.', 'danger')
                    return redirect(url_for('edit_finance_transaction', transaction_id=transaction_id))
                
                # Handle file upload/removal
                attachment_path = transaction['attachment_path']
                remove_attachment = request.form.get('remove_attachment') == 'yes'
                
                if remove_attachment and attachment_path:
                    # Delete old file
                    old_path = os.path.join(Config.UPLOAD_FOLDER, attachment_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                    attachment_path = None
                
                file = request.files.get('attachment')
                if file and file.filename:
                    # Validate file
                    allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png', 'gif'}
                    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                        flash('Format file tidak diizinkan.', 'danger')
                        return redirect(url_for('edit_finance_transaction', transaction_id=transaction_id))
                    
                    # Delete old file if exists
                    if attachment_path:
                        old_path = os.path.join(Config.UPLOAD_FOLDER, attachment_path)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    
                    # Save new file
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    extension = file.filename.rsplit('.', 1)[1].lower()
                    safe_filename = f"finance_{transaction_type}_{timestamp}.{extension}"
                    
                    upload_folder = Config.UPLOAD_FOLDER
                    file.save(os.path.join(upload_folder, safe_filename))
                    attachment_path = safe_filename
                
                # Update database
                cur.execute("""
                    UPDATE finance_transactions 
                    SET type = %s, category = %s, amount = %s, description = %s, 
                        payment_method = %s, reference_number = %s, 
                        transaction_date = %s, attachment_path = %s,
                        updated_at = %s
                    WHERE id = %s
                """, (
                    transaction_type,
                    category,
                    amount,
                    description,
                    payment_method,
                    reference_number,
                    transaction_date,
                    attachment_path,
                    datetime.now(),
                    transaction_id
                ))
                
                db.commit()
                flash('Transaksi berhasil diperbarui!', 'success')
                return redirect(url_for('finance_transactions'))
                
            except Exception as e:
                flash(f'Terjadi kesalahan: {str(e)}', 'danger')
                return redirect(url_for('edit_finance_transaction', transaction_id=transaction_id))
        
        # GET request - show form
        # Get existing categories
        cur.execute("SELECT DISTINCT category, type FROM finance_transactions ORDER BY type, category")
        categories = cur.fetchall()
        cur.close()
        
        return render_template('admin/finance/edit_transaction.html',
                             transaction=transaction,
                             categories=categories)
    
    @app.route('/admin/finance/transaction/<int:transaction_id>/delete', methods=['POST'])
    def delete_finance_transaction(transaction_id):
        """Delete transaction"""
        if not g.user or g.user.get('role') != 'admin':
            flash('Akses ditolak. Hanya admin yang dapat mengakses.', 'danger')
            return redirect(url_for('index'))
        
        try:
            db = get_db()
            cur = db.cursor()
            
            # Get attachment path first
            cur.execute("SELECT attachment_path FROM finance_transactions WHERE id = %s", (transaction_id,))
            result = cur.fetchone()
            
            # Delete from database
            cur.execute("DELETE FROM finance_transactions WHERE id = %s", (transaction_id,))
            db.commit()
            cur.close()
            
            # Delete attachment file if exists
            if result and result[0]:
                file_path = os.path.join(Config.UPLOAD_FOLDER, result[0])
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            flash('Transaksi berhasil dihapus!', 'success')
            
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
        
        return redirect(url_for('finance_transactions'))
    
    @app.route('/admin/finance/report')
    def finance_report():
        """Financial report"""
        if not g.user or g.user.get('role') != 'admin':
            flash('Akses ditolak. Hanya admin yang dapat mengakses.', 'danger')
            return redirect(url_for('index'))
        
        year = request.args.get('year', date.today().year, type=int)
        
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        try:
            # Monthly breakdown
            cur.execute("""
                SELECT 
                    MONTH(transaction_date) as month,
                    SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income,
                    SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expense
                FROM finance_transactions
                WHERE YEAR(transaction_date) = %s
                GROUP BY MONTH(transaction_date)
                ORDER BY month
            """, (year,))
            monthly_data = cur.fetchall()
            
            # Yearly totals
            cur.execute("""
                SELECT 
                    SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
                    SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
                FROM finance_transactions
                WHERE YEAR(transaction_date) = %s
            """, (year,))
            yearly_totals = cur.fetchone()
            
            # Top income categories
            cur.execute("""
                SELECT category, SUM(amount) as total, COUNT(*) as count
                FROM finance_transactions
                WHERE type = 'income' AND YEAR(transaction_date) = %s
                GROUP BY category
                ORDER BY total DESC
                LIMIT 10
            """, (year,))
            top_income = cur.fetchall()
            
            # Top expense categories
            cur.execute("""
                SELECT category, SUM(amount) as total, COUNT(*) as count
                FROM finance_transactions
                WHERE type = 'expense' AND YEAR(transaction_date) = %s
                GROUP BY category
                ORDER BY total DESC
                LIMIT 10
            """, (year,))
            top_expense = cur.fetchall()
            
        except Exception as e:
            print(f"Error loading report: {str(e)}")
            monthly_data = []
            yearly_totals = {'total_income': 0, 'total_expense': 0}
            top_income = []
            top_expense = []
        
        cur.close()
        
        def format_currency(value):
            return f"Rp {value:,.0f}".replace(',', '.')
        
        return render_template('admin/finance/report.html',
                             monthly_data=monthly_data,
                             yearly_totals=yearly_totals,
                             top_income=top_income,
                             top_expense=top_expense,
                             current_year=year,
                             format_currency=format_currency)

    # ==============================================
    # PROFILE ROUTES - FIXED AVATAR
    # ==============================================

    @app.route('/profile/edit', methods=['GET', 'POST'])
    def edit_profile():
        if not g.user:
            flash("Silakan login terlebih dahulu.")
            return redirect(url_for('auth.login'))
        
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT id, username, full_name, bio, avatar FROM users WHERE id=%s", (g.user['id'],))
        user = cur.fetchone()
        cur.close()
        
        if not user:
            flash("Profil tidak ditemukan.")
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            full_name = request.form.get('full_name', '').strip() or None
            bio = request.form.get('bio', '').strip() or None
            avatar_filename = user.get('avatar')
            
            # Handle avatar upload (base64 from cropper)
            avatar_data = request.form.get('avatar')
            
            if avatar_data and avatar_data.startswith('data:image'):
                try:
                    # Parse base64 data
                    header, encoded = avatar_data.split(',', 1)
                    image_data = base64.b64decode(encoded)
                    
                    # Open image with PIL
                    img = Image.open(io.BytesIO(image_data))
                    
                    # ✅ PERBAIKAN: Resize dengan mempertahankan rasio aspek asli
                    # Tentukan ukuran maksimal (600px untuk sisi terpanjang)
                    max_size = 600
                    
                    # Hitung rasio resize
                    width, height = img.size
                    if width > height:
                        # Landscape atau square
                        new_width = max_size
                        new_height = int((max_size / width) * height)
                    else:
                        # Portrait
                        new_height = max_size
                        new_width = int((max_size / height) * width)
                    
                    # Resize dengan mempertahankan aspect ratio
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Convert RGBA to RGB if needed
                    if img.mode == 'RGBA':
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Generate filename
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    safe_username = g.user['username'].replace(' ', '_').replace('/', '_').replace('\\', '_')
                    final_name = f"{safe_username}_{timestamp}_avatar.jpg"
                    save_path = os.path.join(Config.UPLOAD_FOLDER, final_name)
                    
                    # Ensure upload folder exists
                    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                    
                    # Save file with quality optimization
                    img.save(save_path, 'JPEG', quality=85, optimize=True)
                    
                    # Delete old avatar if exists and not default
                    if avatar_filename and avatar_filename != 'default_avatar.png':
                        old_path = os.path.join(Config.UPLOAD_FOLDER, avatar_filename)
                        if os.path.exists(old_path):
                            try:
                                os.remove(old_path)
                            except Exception as e:
                                print(f"Failed to delete old avatar: {e}")
                    
                    avatar_filename = final_name
                    
                except Exception as e:
                    print(f"Error saving avatar: {str(e)}")
                    flash(f'Gagal menyimpan foto: {str(e)}')
                    return redirect(url_for('edit_profile'))
            
            # Update database
            db = get_db()
            cur = db.cursor()
            cur.execute("UPDATE users SET full_name=%s, bio=%s, avatar=%s WHERE id=%s",
                       (full_name, bio, avatar_filename, g.user['id']))
            db.commit()
            cur.close()
            
            flash('Profil berhasil diperbarui.')
            return redirect(url_for('profile'))
        
        return render_template('edit_profile.html', user=user)

    @app.route('/uploads/<path:filename>')
    def download_file(filename):
        """Route untuk download atau view uploaded files"""
        try:
            # Normalize path
            if filename.startswith('uploads/'):
                filename = filename[8:]
            
            # Construct full file path
            file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            
            # Check if file exists
            if os.path.exists(file_path):
                # Determine mimetype based on file extension
                mimetype = None
                if filename.lower().endswith('.pdf'):
                    mimetype = 'application/pdf'
                elif filename.lower().endswith(('.jpg', '.jpeg')):
                    mimetype = 'image/jpeg'
                elif filename.lower().endswith('.png'):
                    mimetype = 'image/png'
                elif filename.lower().endswith('.gif'):
                    mimetype = 'image/gif'
                
                # Check if this is a download request (from query parameter)
                download = request.args.get('download', 'false').lower() == 'true'
                
                if download:
                    # Force download
                    return send_file(
                        file_path, 
                        mimetype=mimetype,
                        as_attachment=True,
                        download_name=os.path.basename(filename)
                    )
                else:
                    # Force inline display (preview without download)
                    response = send_file(
                        file_path, 
                        mimetype=mimetype
                    )
                    # Explicitly set inline disposition
                    response.headers['Content-Disposition'] = f'inline; filename="{os.path.basename(filename)}"'
                    response.headers['Content-Type'] = mimetype if mimetype else 'application/octet-stream'
                    # Disable cache to prevent download behavior
                    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                    response.headers['Pragma'] = 'no-cache'
                    response.headers['Expires'] = '0'
                    return response
            else:
                flash("File tidak ditemukan.")
                return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error membuka file: {str(e)}")
            return redirect(url_for('index'))

    # Fix avatars route (one-time use)
    @app.route('/fix-avatars')
    def fix_avatars():
        """Fix avatar filenames yang mengandung spasi"""
        if not g.user or g.user.get('role') != 'admin':
            flash('Unauthorized')
            return redirect(url_for('index'))
        
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT id, username, avatar FROM users WHERE avatar IS NOT NULL AND avatar != 'default_avatar.png'")
        users = cur.fetchall()
        
        fixed_count = 0
        errors = []
        
        for user in users:
            old_filename = user['avatar']
            old_path = os.path.join(Config.UPLOAD_FOLDER, old_filename)
            
            # Generate new safe filename
            if ' ' in old_filename or '/' in old_filename or '\\' in old_filename:
                new_filename = old_filename.replace(' ', '_').replace('/', '_').replace('\\', '_')
                new_path = os.path.join(Config.UPLOAD_FOLDER, new_filename)
                
                # Rename file if exists
                if os.path.exists(old_path):
                    try:
                        os.rename(old_path, new_path)
                        
                        # Update database
                        cur2 = db.cursor()
                        cur2.execute("UPDATE users SET avatar=%s WHERE id=%s", (new_filename, user['id']))
                        db.commit()
                        cur2.close()
                        
                        fixed_count += 1
                    except Exception as e:
                        errors.append(f"Error fixing {old_filename}: {str(e)}")
                else:
                    errors.append(f"File not found: {old_path}")
        
        cur.close()
        
        if errors:
            flash(f'Fixed {fixed_count} avatars with {len(errors)} errors.', 'warning')
        else:
            flash(f'Successfully fixed {fixed_count} avatar filenames!', 'success')
        
        return redirect(url_for('profile'))

# Initialize routes
from app import app
init_routes(app)