# models/finance_model.py

import os
from datetime import datetime, date, timedelta
from decimal import Decimal
from utils.database import get_db

class FinanceModel:
    
    @staticmethod
    def get_transaction_by_id(transaction_id):
        """Get single transaction by ID"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("""
            SELECT ft.*, 
                   u.full_name as created_by_name,
                   u.username as created_by_username
            FROM finance_transactions ft
            JOIN users u ON ft.created_by = u.id
            WHERE ft.id = %s
        """, (transaction_id,))
        transaction = cur.fetchone()
        cur.close()
        return transaction
    
    @staticmethod
    def get_all_transactions(page=1, per_page=20, filters=None):
        """Get all transactions with pagination and filters"""
        if filters is None:
            filters = {}
        
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        where_clause = "1=1"
        params = []
        
        # Apply filters
        if filters.get('type'):
            where_clause += " AND ft.type = %s"
            params.append(filters['type'])
        
        if filters.get('category'):
            where_clause += " AND ft.category = %s"
            params.append(filters['category'])
        
        if filters.get('start_date'):
            where_clause += " AND ft.transaction_date >= %s"
            params.append(filters['start_date'])
        
        if filters.get('end_date'):
            where_clause += " AND ft.transaction_date <= %s"
            params.append(filters['end_date'])
        
        if filters.get('payment_method'):
            where_clause += " AND ft.payment_method = %s"
            params.append(filters['payment_method'])
        
        if filters.get('search'):
            where_clause += " AND (ft.description LIKE %s OR ft.reference_number LIKE %s)"
            params.append(f"%{filters['search']}%")
            params.append(f"%{filters['search']}%")
        
        # Count total for pagination
        count_query = f"""
            SELECT COUNT(*) as total 
            FROM finance_transactions ft
            WHERE {where_clause}
        """
        cur.execute(count_query, tuple(params))
        total = cur.fetchone()['total']
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get data
        query = f"""
            SELECT ft.*, 
                   u.full_name as created_by_name,
                   u.username as created_by_username
            FROM finance_transactions ft
            JOIN users u ON ft.created_by = u.id
            WHERE {where_clause}
            ORDER BY ft.transaction_date DESC, ft.created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([per_page, offset])
        
        cur.execute(query, tuple(params))
        transactions = cur.fetchall()
        
        cur.close()
        
        return {
            'transactions': transactions,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page if total > 0 else 1
        }
    
    @staticmethod
    def create_transaction(data):
        """Create new transaction"""
        db = get_db()
        cur = db.cursor()
        
        query = """
            INSERT INTO finance_transactions 
            (type, category, amount, description, payment_method, 
             reference_number, transaction_date, created_by, attachment_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            data['type'],
            data['category'],
            data['amount'],
            data.get('description', ''),
            data.get('payment_method', ''),
            data.get('reference_number', ''),
            data['transaction_date'],
            data['created_by'],
            data.get('attachment_path')
        )
        
        cur.execute(query, params)
        transaction_id = cur.lastrowid
        db.commit()
        cur.close()
        
        return transaction_id
    
    @staticmethod
    def update_transaction(transaction_id, data):
        """Update existing transaction"""
        db = get_db()
        cur = db.cursor()
        
        query = """
            UPDATE finance_transactions 
            SET type = %s, category = %s, amount = %s, description = %s, 
                payment_method = %s, reference_number = %s, 
                transaction_date = %s, attachment_path = %s,
                updated_at = %s
            WHERE id = %s
        """
        
        params = (
            data['type'],
            data['category'],
            data['amount'],
            data.get('description', ''),
            data.get('payment_method', ''),
            data.get('reference_number', ''),
            data['transaction_date'],
            data.get('attachment_path'),
            datetime.now(),
            transaction_id
        )
        
        cur.execute(query, params)
        db.commit()
        cur.close()
        
        return cur.rowcount > 0
    
    @staticmethod
    def delete_transaction(transaction_id):
        """Delete transaction"""
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
            from utils.file_handler import delete_file
            delete_file(result[0])
        
        return True
    
    @staticmethod
    def get_summary(period='month', year=None, month=None):
        """Get financial summary"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        # Set default to current month if not specified
        if not year or not month:
            today = date.today()
            year = today.year
            month = today.month
        
        # Total Income
        cur.execute("""
            SELECT COALESCE(SUM(amount), 0) as total_income
            FROM finance_transactions 
            WHERE type = 'income' 
            AND YEAR(transaction_date) = %s 
            AND MONTH(transaction_date) = %s
        """, (year, month))
        income_result = cur.fetchone()
        total_income = income_result['total_income'] or 0
        
        # Total Expense
        cur.execute("""
            SELECT COALESCE(SUM(amount), 0) as total_expense
            FROM finance_transactions 
            WHERE type = 'expense' 
            AND YEAR(transaction_date) = %s 
            AND MONTH(transaction_date) = %s
        """, (year, month))
        expense_result = cur.fetchone()
        total_expense = expense_result['total_expense'] or 0
        
        # Current Balance (total all time)
        cur.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_all_income,
                COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_all_expense
            FROM finance_transactions
        """)
        all_result = cur.fetchone()
        current_balance = (all_result['total_all_income'] or 0) - (all_result['total_all_expense'] or 0)
        
        # Top expense categories
        cur.execute("""
            SELECT category, SUM(amount) as total
            FROM finance_transactions 
            WHERE type = 'expense' 
            AND YEAR(transaction_date) = %s 
            AND MONTH(transaction_date) = %s
            GROUP BY category 
            ORDER BY total DESC 
            LIMIT 5
        """, (year, month))
        top_expenses = cur.fetchall()
        
        # Income by category
        cur.execute("""
            SELECT category, SUM(amount) as total
            FROM finance_transactions 
            WHERE type = 'income' 
            AND YEAR(transaction_date) = %s 
            AND MONTH(transaction_date) = %s
            GROUP BY category 
            ORDER BY total DESC
        """, (year, month))
        income_by_category = cur.fetchall()
        
        # Recent transactions
        cur.execute("""
            SELECT ft.*, u.full_name as created_by_name
            FROM finance_transactions ft
            JOIN users u ON ft.created_by = u.id
            WHERE YEAR(ft.transaction_date) = %s AND MONTH(ft.transaction_date) = %s
            ORDER BY ft.transaction_date DESC, ft.created_at DESC
            LIMIT 10
        """, (year, month))
        recent_transactions = cur.fetchall()
        
        cur.close()
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'current_balance': current_balance,
            'top_expenses': top_expenses,
            'income_by_category': income_by_category,
            'recent_transactions': recent_transactions,
            'month': month,
            'year': year,
            'net_income': total_income - total_expense
        }
    
    @staticmethod
    def get_categories(transaction_type=None):
        """Get all categories"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        if transaction_type:
            cur.execute("""
                SELECT * FROM finance_categories 
                WHERE is_active = 1 AND type = %s
                ORDER BY name
            """, (transaction_type,))
        else:
            cur.execute("""
                SELECT * FROM finance_categories 
                WHERE is_active = 1
                ORDER BY type, name
            """)
        
        categories = cur.fetchall()
        cur.close()
        return categories
    
    @staticmethod
    def get_yearly_report(year):
        """Get yearly financial report"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        
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
        
        cur.close()
        
        return {
            'monthly_data': monthly_data,
            'yearly_totals': yearly_totals or {'total_income': 0, 'total_expense': 0},
            'year': year
        }
    
    @staticmethod
    def get_daily_summary(date_obj):
        """Get daily summary"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        cur.execute("""
            SELECT 
                type,
                category,
                SUM(amount) as total,
                COUNT(*) as count
            FROM finance_transactions
            WHERE transaction_date = %s
            GROUP BY type, category
            ORDER BY type, total DESC
        """, (date_obj,))
        
        daily_summary = cur.fetchall()
        cur.close()
        return daily_summary