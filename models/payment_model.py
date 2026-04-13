from utils.database import get_db

class PaymentModel:
    
    @staticmethod
    def create(user_id, program_id, payment_type, amount, proof_file=None, status='pending'):
        """Create a new payment record"""
        db = get_db()
        cur = db.cursor()
        
        cur.execute("""
            INSERT INTO payments (user_id, program_id, payment_type, amount, proof_file, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, program_id, payment_type, amount, proof_file, status))
        
        payment_id = cur.lastrowid
        db.commit()
        cur.close()
        
        return payment_id
    
    @staticmethod
    def get_by_id(payment_id):
        """Get payment by ID"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM payments WHERE id = %s", (payment_id,))
        payment = cur.fetchone()
        cur.close()
        return payment
    
    @staticmethod
    def get_by_user_id(user_id, payment_type=None):
        """Get payments by user ID, optionally filtered by payment type"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        if payment_type:
            cur.execute("""
                SELECT * FROM payments 
                WHERE user_id = %s AND payment_type = %s
                ORDER BY created_at DESC
            """, (user_id, payment_type))
        else:
            cur.execute("""
                SELECT * FROM payments 
                WHERE user_id = %s 
                ORDER BY created_at DESC
            """, (user_id,))
        
        payments = cur.fetchall()
        cur.close()
        return payments
    
    @staticmethod
    def get_all(status=None, payment_type=None, limit=100):
        """Get all payments with optional filters"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        query = "SELECT * FROM payments WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        if payment_type:
            query += " AND payment_type = %s"
            params.append(payment_type)
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        cur.execute(query, tuple(params))
        payments = cur.fetchall()
        cur.close()
        return payments
    
    @staticmethod
    def update_status(payment_id, status, verified_by=None, rejection_reason=None):
        """Update payment status"""
        db = get_db()
        cur = db.cursor()
        
        if status == 'verified':
            cur.execute("""
                UPDATE payments 
                SET status = %s, 
                    verified_by = %s, 
                    verified_at = NOW(),
                    rejection_reason = NULL
                WHERE id = %s
            """, (status, verified_by, payment_id))
        elif status == 'rejected':
            cur.execute("""
                UPDATE payments 
                SET status = %s, 
                    verified_by = %s, 
                    verified_at = NOW(),
                    rejection_reason = %s
                WHERE id = %s
            """, (status, verified_by, rejection_reason, payment_id))
        else:
            cur.execute("""
                UPDATE payments 
                SET status = %s,
                    verified_by = NULL,
                    verified_at = NULL,
                    rejection_reason = NULL
                WHERE id = %s
            """, (status, payment_id))
        
        db.commit()
        cur.close()
        return True
    
    @staticmethod
    def update_payment_proof(payment_id, proof_file):
        """Update payment proof file"""
        db = get_db()
        cur = db.cursor()
        
        cur.execute("""
            UPDATE payments 
            SET proof_file = %s,
                status = 'pending'
            WHERE id = %s
        """, (proof_file, payment_id))
        
        db.commit()
        cur.close()
        return True
    
    @staticmethod
    def get_statistics():
        """Get payment statistics"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        cur.execute("""
            SELECT 
                COUNT(*) as total_payments,
                SUM(amount) as total_amount,
                SUM(CASE WHEN status = 'pending' THEN amount ELSE 0 END) as pending_amount,
                SUM(CASE WHEN status = 'verified' THEN amount ELSE 0 END) as verified_amount,
                SUM(CASE WHEN status = 'rejected' THEN amount ELSE 0 END) as rejected_amount,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_count,
                COUNT(CASE WHEN status = 'verified' THEN 1 END) as verified_count,
                COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected_count
            FROM payments
        """)
        
        stats = cur.fetchone()
        cur.close()
        
        # Convert None to 0
        for key in stats:
            if stats[key] is None:
                stats[key] = 0
        
        return stats
    
    @staticmethod
    def get_recent_activity(limit=10):
        """Get recent payment activity"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        cur.execute("""
            SELECT p.*, u.full_name, u.username, pr.name as program_name
            FROM payments p
            JOIN users u ON p.user_id = u.id
            JOIN programs pr ON p.program_id = pr.id
            ORDER BY p.created_at DESC
            LIMIT %s
        """, (limit,))
        
        activities = cur.fetchall()
        cur.close()
        return activities
    
    # Tambahkan method untuk compatibilitas dengan kode lama
    @staticmethod
    def get_by_order_id(order_id):
        """Get payment by order_id (untuk compatibilitas dengan kode lama yang pakai Midtrans)"""
        # Karena kita tidak pakai Midtrans, return None
        return None
    
    @staticmethod
    def update_payment_status(order_id, status, transaction_id=None):
        """Update payment status by order_id (untuk compatibilitas)"""
        # Karena kita tidak pakai Midtrans, return False
        return False
    
    @staticmethod
    def mark_user_as_verified(user_id, program_id):
        """Mark user as verified (untuk compatibilitas)"""
        db = get_db()
        cur = db.cursor()
        
        cur.execute("""
            UPDATE users 
            SET payment_status = 'verified', 
                registration_completed = 1 
            WHERE id = %s
        """, (user_id,))
        
        db.commit()
        cur.close()
        return True