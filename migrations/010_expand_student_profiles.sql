-- Pisahkan biodata siswa agar informasi tidak ditumpuk di kolom alamat.
ALTER TABLE student_profiles
    ADD COLUMN school_name VARCHAR(200) NULL AFTER birth_date,
    ADD COLUMN nik VARCHAR(30) NULL AFTER school_name,
    ADD COLUMN rt_rw VARCHAR(20) NULL AFTER address,
    ADD COLUMN village VARCHAR(100) NULL AFTER rt_rw,
    ADD COLUMN district VARCHAR(100) NULL AFTER village,
    ADD COLUMN city VARCHAR(100) NULL AFTER district,
    ADD COLUMN province VARCHAR(100) NULL AFTER city,
    ADD COLUMN graduation_date DATE NULL AFTER enrollment_date,
    ADD COLUMN departure_date DATE NULL AFTER graduation_date,
    ADD COLUMN job_sector VARCHAR(150) NULL AFTER departure_date,
    ADD COLUMN placement VARCHAR(150) NULL AFTER job_sector,
    ADD COLUMN notes VARCHAR(255) NULL AFTER status;
