from config import Config
import mysql.connector

try:
    db = mysql.connector.connect(**Config.DB_CONFIG)
    cur = db.cursor()
    columns_to_add = [
        ("nik", "VARCHAR(20)"),
        ("height", "INT"),
        ("weight", "INT"),
        ("blood_type", "VARCHAR(5)"),
        ("father_name", "VARCHAR(100)"),
        ("mother_name", "VARCHAR(100)"),
        ("parent_phone", "VARCHAR(20)"),
        ("parent_address", "TEXT"),
        ("sd_year", "VARCHAR(10)"),
        ("smp_year", "VARCHAR(10)"),
        ("sma_year", "VARCHAR(10)"),
        ("d3_year", "VARCHAR(10)")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cur.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type};")
            print(f"Added {col_name}")
        except Exception as e:
            print(f"Failed {col_name} (might already exist): {e}")
            
    db.commit()
    cur.close()
    db.close()
    print("Columns added successfully!")
except Exception as e:
    print("DB connection error:", e)
