from utils.database import get_db

class ProgramModel:
    
    @staticmethod
    def get_by_class_type(class_type):
        """Get program by class type (Reguler or Karyawan)"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("""
            SELECT * FROM programs 
            WHERE class_type = %s AND is_active = 1 
            LIMIT 1
        """, (class_type,))
        program = cur.fetchone()
        cur.close()
        return program
    
    @staticmethod
    def get_by_id(program_id):
        """Get program by ID"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM programs WHERE id = %s", (program_id,))
        program = cur.fetchone()
        cur.close()
        return program
    
    @staticmethod
    def get_all_active():
        """Get all active programs"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM programs WHERE is_active = 1")
        programs = cur.fetchall()
        
        # Add calculated price field for compatibility
        for program in programs:
            # Calculate initial payment (registration + pre_mcu)
            program['price'] = float(program.get('registration_fee', 0)) + float(program.get('pre_mcu_fee', 0))
            program['total_fee'] = float(program.get('education_fee', 0))
        
        cur.close()
        return programs
    
    @staticmethod
    def get_all():
        """Get all programs"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM programs")
        programs = cur.fetchall()
        cur.close()
        return programs
    
    @staticmethod
    def calculate_total_fee(program_id):
        """Calculate total fee for a program"""
        program = ProgramModel.get_by_id(program_id)
        if not program:
            return 0
        
        total = 0
        total += float(program.get('registration_fee', 0))
        total += float(program.get('education_fee', 0))
        total += float(program.get('post_job_fee', 0))
        total += float(program.get('pre_mcu_fee', 0))
        total += float(program.get('certification_fee', 0))
        total += float(program.get('mcu_fee', 0))
        total += float(program.get('passport_fee', 0))
        total += float(program.get('so_fee_min', 0))
        
        return total