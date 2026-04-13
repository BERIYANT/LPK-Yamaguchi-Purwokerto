# controllers/finance_controller.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, jsonify, send_file
import os
import json
from datetime import datetime, date, timedelta
from decimal import Decimal
import calendar
from utils.authentication import login_required, admin_required
from utils.database import get_db
from utils.file_handler import allowed_file, save_uploaded_file, delete_file
from models.finance_model import FinanceModel

finance_bp = Blueprint('finance', __name__, url_prefix='/finance')

@finance_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Financial dashboard"""
    # Get current year and month
    today = date.today()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)
    
    # Get summary
    summary = FinanceModel.get_summary('month', year, month)
    
    # Get categories for filter
    categories = FinanceModel.get_categories()
    
    # Get recent transactions
    recent = FinanceModel.get_all_transactions(page=1, per_page=10)
    
    # Format currency
    def format_currency(value):
        return f"Rp {value:,.0f}".replace(',', '.')
    
    return render_template('admin/finance/dashboard.html',
                         summary=summary,
                         categories=categories,
                         recent_transactions=recent['transactions'],
                         current_year=year,
                         current_month=month,
                         month_name=calendar.month_name[month],
                         format_currency=format_currency)

@finance_bp.route('/transactions')
@login_required
@admin_required
def transactions():
    """View all transactions"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filters
    filters = {}
    transaction_type = request.args.get('type')
    if transaction_type in ['income', 'expense']:
        filters['type'] = transaction_type
    
    category = request.args.get('category')
    if category:
        filters['category'] = category
    
    start_date = request.args.get('start_date')
    if start_date:
        filters['start_date'] = start_date
    
    end_date = request.args.get('end_date')
    if end_date:
        filters['end_date'] = end_date
    
    payment_method = request.args.get('payment_method')
    if payment_method:
        filters['payment_method'] = payment_method
    
    search = request.args.get('search')
    if search:
        filters['search'] = search
    
    # Get transactions
    result = FinanceModel.get_all_transactions(page, per_page, filters)
    
    # Get categories for filter dropdown
    categories = FinanceModel.get_categories()
    
    # Get unique payment methods
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT DISTINCT payment_method FROM finance_transactions WHERE payment_method IS NOT NULL AND payment_method != ''")
    payment_methods = [row[0] for row in cur.fetchall()]
    cur.close()
    
    # Format currency helper
    def format_currency(value):
        return f"Rp {value:,.0f}".replace(',', '.')
    
    return render_template('admin/finance/transactions.html',
                         transactions=result['transactions'],
                         pagination=result,
                         categories=categories,
                         payment_methods=payment_methods,
                         filters=filters,
                         format_currency=format_currency)

@finance_bp.route('/transaction/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_transaction():
    """Create new transaction"""
    if request.method == 'POST':
        try:
            # Get form data
            transaction_type = request.form['type']
            category = request.form['category']
            amount_str = request.form['amount'].replace('.', '').replace(',', '.')
            amount = Decimal(amount_str)
            description = request.form.get('description', '').strip()
            payment_method = request.form.get('payment_method', '').strip()
            reference_number = request.form.get('reference_number', '').strip()
            transaction_date = request.form['transaction_date']
            
            # Validate required fields
            if not transaction_type or not category or not amount or not transaction_date:
                flash('Harap isi semua field yang wajib diisi.', 'danger')
                return redirect(url_for('finance.create_transaction'))
            
            if amount <= 0:
                flash('Jumlah harus lebih dari 0.', 'danger')
                return redirect(url_for('finance.create_transaction'))
            
            # Handle file upload
            attachment_path = None
            file = request.files.get('attachment')
            if file and file.filename:
                if not allowed_file(file.filename, ['pdf', 'jpg', 'jpeg', 'png', 'gif']):
                    flash('Format file tidak diizinkan. Gunakan PDF, JPG, PNG, atau GIF.', 'danger')
                    return redirect(url_for('finance.create_transaction'))
                
                try:
                    # Save file
                    filename = f"finance_{transaction_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                    attachment_path = save_uploaded_file(file, 'finance', filename)
                except Exception as e:
                    flash(f'Gagal mengupload file: {str(e)}', 'danger')
                    return redirect(url_for('finance.create_transaction'))
            
            # Create transaction data
            transaction_data = {
                'type': transaction_type,
                'category': category,
                'amount': amount,
                'description': description,
                'payment_method': payment_method,
                'reference_number': reference_number,
                'transaction_date': transaction_date,
                'created_by': g.user['id'],
                'attachment_path': attachment_path
            }
            
            # Save to database
            transaction_id = FinanceModel.create_transaction(transaction_data)
            
            # Auto-create categories if they don't exist in the categories table
            db = get_db()
            cur = db.cursor(dictionary=True)
            cur.execute("SELECT id FROM finance_categories WHERE name = %s AND type = %s", 
                       (category, transaction_type))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO finance_categories (name, type, description, is_active)
                    VALUES (%s, %s, %s, 1)
                """, (category, transaction_type, f"Auto-created from transaction"))
                db.commit()
            cur.close()
            
            flash(f'Transaksi {transaction_type} berhasil ditambahkan!', 'success')
            return redirect(url_for('finance.transactions'))
            
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
            return redirect(url_for('finance.create_transaction'))
    
    # GET request - show form
    categories = FinanceModel.get_categories()
    
    # Default values
    default_date = date.today().strftime('%Y-%m-%d')
    
    return render_template('admin/finance/create_transaction.html',
                         categories=categories,
                         default_date=default_date)

@finance_bp.route('/transaction/<int:transaction_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_transaction(transaction_id):
    """Edit existing transaction"""
    transaction = FinanceModel.get_transaction_by_id(transaction_id)
    if not transaction:
        flash('Transaksi tidak ditemukan.', 'danger')
        return redirect(url_for('finance.transactions'))
    
    if request.method == 'POST':
        try:
            # Get form data
            transaction_type = request.form['type']
            category = request.form['category']
            amount_str = request.form['amount'].replace('.', '').replace(',', '.')
            amount = Decimal(amount_str)
            description = request.form.get('description', '').strip()
            payment_method = request.form.get('payment_method', '').strip()
            reference_number = request.form.get('reference_number', '').strip()
            transaction_date = request.form['transaction_date']
            
            # Validate
            if not transaction_type or not category or not amount or not transaction_date:
                flash('Harap isi semua field yang wajib diisi.', 'danger')
                return redirect(url_for('finance.edit_transaction', transaction_id=transaction_id))
            
            if amount <= 0:
                flash('Jumlah harus lebih dari 0.', 'danger')
                return redirect(url_for('finance.edit_transaction', transaction_id=transaction_id))
            
            # Handle file upload/removal
            attachment_path = transaction['attachment_path']
            remove_attachment = request.form.get('remove_attachment') == 'yes'
            
            if remove_attachment and attachment_path:
                # Delete old file
                delete_file(attachment_path)
                attachment_path = None
            
            file = request.files.get('attachment')
            if file and file.filename:
                if not allowed_file(file.filename, ['pdf', 'jpg', 'jpeg', 'png', 'gif']):
                    flash('Format file tidak diizinkan. Gunakan PDF, JPG, PNG, atau GIF.', 'danger')
                    return redirect(url_for('finance.edit_transaction', transaction_id=transaction_id))
                
                # Delete old file if exists
                if attachment_path:
                    delete_file(attachment_path)
                
                # Save new file
                try:
                    filename = f"finance_{transaction_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                    attachment_path = save_uploaded_file(file, 'finance', filename)
                except Exception as e:
                    flash(f'Gagal mengupload file: {str(e)}', 'danger')
                    return redirect(url_for('finance.edit_transaction', transaction_id=transaction_id))
            
            # Update transaction data
            transaction_data = {
                'type': transaction_type,
                'category': category,
                'amount': amount,
                'description': description,
                'payment_method': payment_method,
                'reference_number': reference_number,
                'transaction_date': transaction_date,
                'attachment_path': attachment_path
            }
            
            # Update in database
            success = FinanceModel.update_transaction(transaction_id, transaction_data)
            
            if success:
                flash('Transaksi berhasil diperbarui!', 'success')
            else:
                flash('Gagal memperbarui transaksi.', 'danger')
            
            return redirect(url_for('finance.transactions'))
            
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
            return redirect(url_for('finance.edit_transaction', transaction_id=transaction_id))
    
    # GET request - show form
    categories = FinanceModel.get_categories()
    
    return render_template('admin/finance/edit_transaction.html',
                         transaction=transaction,
                         categories=categories)

@finance_bp.route('/transaction/<int:transaction_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_transaction(transaction_id):
    """Delete transaction"""
    try:
        success = FinanceModel.delete_transaction(transaction_id)
        if success:
            flash('Transaksi berhasil dihapus!', 'success')
        else:
            flash('Gagal menghapus transaksi.', 'danger')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('finance.transactions'))

@finance_bp.route('/reports')
@login_required
@admin_required
def reports():
    """Financial reports"""
    year = request.args.get('year', date.today().year, type=int)
    
    # Get yearly report
    yearly_report = FinanceModel.get_yearly_report(year)
    
    # Get available years
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT DISTINCT YEAR(transaction_date) as year FROM finance_transactions ORDER BY year DESC")
    years = [row[0] for row in cur.fetchall()]
    cur.close()
    
    # Format currency helper
    def format_currency(value):
        return f"Rp {value:,.0f}".replace(',', '.')
    
    return render_template('admin/finance/reports.html',
                         yearly_report=yearly_report,
                         years=years,
                         current_year=year,
                         format_currency=format_currency)

@finance_bp.route('/export')
@login_required
@admin_required
def export_data():
    """Export financial data to Excel"""
    try:
        import pandas as pd
        from io import BytesIO
        
        # Get filters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        transaction_type = request.args.get('type')
        
        # Build query
        where_clause = "1=1"
        params = []
        
        if start_date:
            where_clause += " AND transaction_date >= %s"
            params.append(start_date)
        
        if end_date:
            where_clause += " AND transaction_date <= %s"
            params.append(end_date)
        
        if transaction_type in ['income', 'expense']:
            where_clause += " AND type = %s"
            params.append(transaction_type)
        
        # Get data
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(f"""
            SELECT 
                transaction_date,
                CASE type 
                    WHEN 'income' THEN 'Pemasukan' 
                    WHEN 'expense' THEN 'Pengeluaran' 
                END as jenis,
                category as kategori,
                amount as jumlah,
                description as deskripsi,
                payment_method as metode_pembayaran,
                reference_number as nomor_referensi
            FROM finance_transactions
            WHERE {where_clause}
            ORDER BY transaction_date DESC
        """, tuple(params))
        
        data = cur.fetchall()
        cur.close()
        
        if not data:
            flash('Tidak ada data untuk diexport.', 'warning')
            return redirect(url_for('finance.transactions'))
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Transaksi Keuangan', index=False)
            
            # Add summary sheet
            summary_data = {
                'Total Pemasukan': [df[df['jenis'] == 'Pemasukan']['jumlah'].sum()],
                'Total Pengeluaran': [df[df['jenis'] == 'Pengeluaran']['jumlah'].sum()],
                'Saldo': [df[df['jenis'] == 'Pemasukan']['jumlah'].sum() - df[df['jenis'] == 'Pengeluaran']['jumlah'].sum()]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Ringkasan', index=False)
        
        output.seek(0)
        
        # Generate filename
        filename = f"laporan_keuangan_{date.today().strftime('%Y%m%d')}.xlsx"
        
        return send_file(output, 
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        as_attachment=True,
                        download_name=filename)
        
    except ImportError:
        flash('Library pandas dan openpyxl diperlukan untuk export Excel.', 'danger')
        return redirect(url_for('finance.transactions'))
    except Exception as e:
        flash(f'Terjadi kesalahan saat export: {str(e)}', 'danger')
        return redirect(url_for('finance.transactions'))

@finance_bp.route('/api/summary')
@login_required
@admin_required
def api_summary():
    """API endpoint for financial summary (for AJAX requests)"""
    period = request.args.get('period', 'month')
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    
    summary = FinanceModel.get_summary(period, year, month)
    
    return jsonify({
        'success': True,
        'data': {
            'total_income': float(summary['total_income']),
            'total_expense': float(summary['total_expense']),
            'current_balance': float(summary['current_balance']),
            'net_income': float(summary['net_income'])
        }
    })

@finance_bp.route('/api/chart-data')
@login_required
@admin_required
def api_chart_data():
    """API endpoint for chart data"""
    year = request.args.get('year', date.today().year, type=int)
    
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    # Monthly data for line chart
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
    
    # Expense by category for pie chart
    cur.execute("""
        SELECT category, SUM(amount) as total
        FROM finance_transactions
        WHERE type = 'expense' AND YEAR(transaction_date) = %s
        GROUP BY category
        ORDER BY total DESC
        LIMIT 10
    """, (year,))
    expense_by_category = cur.fetchall()
    
    # Income by category for pie chart
    cur.execute("""
        SELECT category, SUM(amount) as total
        FROM finance_transactions
        WHERE type = 'income' AND YEAR(transaction_date) = %s
        GROUP BY category
        ORDER BY total DESC
        LIMIT 10
    """, (year,))
    income_by_category = cur.fetchall()
    
    cur.close()
    
    # Format data for charts
    months = list(range(1, 13))
    income_data = [0] * 12
    expense_data = [0] * 12
    
    for item in monthly_data:
        month_idx = item['month'] - 1
        income_data[month_idx] = float(item['income'] or 0)
        expense_data[month_idx] = float(item['expense'] or 0)
    
    return jsonify({
        'success': True,
        'data': {
            'months': months,
            'income_data': income_data,
            'expense_data': expense_data,
            'expense_by_category': [
                {'category': item['category'], 'total': float(item['total'] or 0)}
                for item in expense_by_category
            ],
            'income_by_category': [
                {'category': item['category'], 'total': float(item['total'] or 0)}
                for item in income_by_category
            ]
        }
    })

@finance_bp.route('/categories')
@login_required
@admin_required
def categories():
    """Manage finance categories"""
    categories = FinanceModel.get_categories()
    
    return render_template('admin/finance/categories.html',
                         categories=categories)

@finance_bp.route('/category/create', methods=['POST'])
@login_required
@admin_required
def create_category():
    """Create new category"""
    try:
        name = request.form['name'].strip()
        category_type = request.form['type']
        description = request.form.get('description', '').strip()
        
        if not name or not category_type:
            flash('Nama dan jenis kategori harus diisi.', 'danger')
            return redirect(url_for('finance.categories'))
        
        db = get_db()
        cur = db.cursor()
        
        # Check if category already exists
        cur.execute("SELECT id FROM finance_categories WHERE name = %s AND type = %s", 
                   (name, category_type))
        if cur.fetchone():
            flash('Kategori dengan nama dan jenis yang sama sudah ada.', 'danger')
            cur.close()
            return redirect(url_for('finance.categories'))
        
        # Insert new category
        cur.execute("""
            INSERT INTO finance_categories (name, type, description, is_active)
            VALUES (%s, %s, %s, 1)
        """, (name, category_type, description))
        
        db.commit()
        cur.close()
        
        flash('Kategori berhasil ditambahkan!', 'success')
        
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('finance.categories'))

@finance_bp.route('/category/<int:category_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_category(category_id):
    """Toggle category active status"""
    try:
        db = get_db()
        cur = db.cursor()
        
        cur.execute("SELECT is_active FROM finance_categories WHERE id = %s", (category_id,))
        result = cur.fetchone()
        
        if not result:
            flash('Kategori tidak ditemukan.', 'danger')
            return redirect(url_for('finance.categories'))
        
        new_status = 0 if result[0] else 1
        
        cur.execute("UPDATE finance_categories SET is_active = %s WHERE id = %s", 
                   (new_status, category_id))
        db.commit()
        cur.close()
        
        status_text = "diaktifkan" if new_status else "dinonaktifkan"
        flash(f'Kategori berhasil {status_text}!', 'success')
        
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('finance.categories'))