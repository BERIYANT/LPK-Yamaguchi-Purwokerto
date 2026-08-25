-- Dashboard administrasi siswa, pembayaran, sensei, dan jadwal mengajar
CREATE TABLE IF NOT EXISTS student_profiles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NULL,
    nis VARCHAR(30) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    gender ENUM('L','P') NULL,
    birth_place VARCHAR(100) NULL,
    birth_date DATE NULL,
    phone VARCHAR(30) NULL,
    address TEXT NULL,
    program_name VARCHAR(150) NULL,
    enrollment_date DATE NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'aktif',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_student_profile_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_student_enrollment_date (enrollment_date),
    INDEX idx_student_name (full_name)
);

CREATE TABLE IF NOT EXISTS student_payments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    payment_type ENUM('registration','education','mcu','dormitory') NOT NULL,
    installment_no TINYINT NULL,
    payment_date DATE NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    note VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_student_payment_student FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
    INDEX idx_student_payment_item (student_id, payment_type, installment_no),
    INDEX idx_student_payment_date (payment_date)
);

CREATE TABLE IF NOT EXISTS sensei_profiles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NULL,
    sensei_code VARCHAR(30) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    phone VARCHAR(30) NULL,
    address TEXT NULL,
    teaching_field VARCHAR(150) NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'aktif',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_sensei_profile_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_sensei_name (full_name)
);

CREATE TABLE IF NOT EXISTS teaching_schedules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sensei_id INT NOT NULL,
    teaching_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    class_name VARCHAR(100) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_schedule_sensei FOREIGN KEY (sensei_id) REFERENCES sensei_profiles(id) ON DELETE CASCADE,
    INDEX idx_schedule_date (teaching_date),
    INDEX idx_schedule_sensei_date (sensei_id, teaching_date)
);
