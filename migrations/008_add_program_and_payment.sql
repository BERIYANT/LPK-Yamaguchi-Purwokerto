-- Create programs table
CREATE TABLE IF NOT EXISTS programs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    terms TEXT,
    duration_days INT DEFAULT 90,
    max_students INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Add payment related columns to users table
-- Using stored procedure for compatibility with MySQL < 8.0
DELIMITER //

CREATE PROCEDURE AddPaymentColumnsIfNotExists()
BEGIN
  DECLARE CONTINUE HANDLER FOR 1060 BEGIN END;
  
  ALTER TABLE users ADD COLUMN program_id INT;
  ALTER TABLE users ADD COLUMN payment_status VARCHAR(50) DEFAULT 'pending';
  ALTER TABLE users ADD COLUMN registration_completed BOOLEAN DEFAULT FALSE;
END //

DELIMITER ;

CALL AddPaymentColumnsIfNotExists();
DROP PROCEDURE AddPaymentColumnsIfNotExists;

-- Create payments table
CREATE TABLE IF NOT EXISTS payments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    program_id INT NOT NULL,
    transaction_id VARCHAR(100) UNIQUE,
    midtrans_order_id VARCHAR(100) UNIQUE,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    payment_method VARCHAR(100),
    payment_date TIMESTAMP NULL,
    verified_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_midtrans_order_id (midtrans_order_id)
);

-- Insert sample programs
INSERT INTO programs (name, description, price, terms, duration_days) VALUES
('Bahasa Korea', 'Program pembelajaran Bahasa Korea untuk persiapan kerja di Jepang. Durasi 3 bulan dengan pembelajaran intensif.', 0, '<ul><li><i class="fa-solid fa-circle-check"></i> Usia 18–39 tahun</li><li><i class="fa-solid fa-circle-check"></i> Pendidikan minimal SMP</li><li><i class="fa-solid fa-circle-check"></i> Tidak terkena TB</li><li><i class="fa-solid fa-circle-check"></i> Tidak hepatitis</li><li><i class="fa-solid fa-circle-check"></i> Catatan: tinggi/berat & mata minus tidak masalah</li></ul>', 90),
('Tokutei Ginou (SSW)', 'Program visa kerja ke Jepang dengan penempatan kerja. Program unggulan kami dengan tingkat keberhasilan tertinggi.', 0, '<ul><li><i class="fa-solid fa-circle-check"></i> Laki-laki/Perempuan (Lajang/Menikah)</li><li><i class="fa-solid fa-circle-check"></i> Lulusan MA/SMA/SMK/Paket C/D3/S1</li><li><i class="fa-solid fa-circle-check"></i> Usia 18–40 tahun</li><li><i class="fa-solid fa-circle-check"></i> Mata minus ≤ 1 (untuk laki-laki)</li><li><i class="fa-solid fa-circle-check"></i> Tidak bertato/bertindik</li><li><i class="fa-solid fa-circle-check"></i> Sehat jasmani & rohani</li></ul>', 180),
('Kuliah Sambil Kerja', 'Program pendidikan dengan skema kerja paruh waktu di Jepang. Kombinasi studi dan pengalaman kerja.', 0, '<ul><li><i class="fa-solid fa-circle-check"></i> Laki-laki/Perempuan (Lajang/Menikah)</li><li><i class="fa-solid fa-circle-check"></i> Lulusan MA/SMA/SMK/Paket C/D3</li><li><i class="fa-solid fa-circle-check"></i> Usia 18–30 tahun</li><li><i class="fa-solid fa-circle-check"></i> Mata minus tidak masalah</li><li><i class="fa-solid fa-circle-check"></i> Berkelakuan baik</li><li><i class="fa-solid fa-circle-check"></i> Sehat jasmani & rohani</li></ul>', 730),
('Engineer', 'Program khusus untuk tenaga teknis dan engineer yang ingin bekerja di industri Jepang.', 0, '<ul><li><i class="fa-solid fa-circle-check"></i> Laki-laki/Perempuan (Lajang/Menikah)</li><li><i class="fa-solid fa-circle-check"></i> Minimal D3 Teknik</li><li><i class="fa-solid fa-circle-check"></i> Usia 18–40 tahun</li><li><i class="fa-solid fa-circle-check"></i> Mata minus ≤ 1 (untuk laki-laki)</li><li><i class="fa-solid fa-circle-check"></i> Tidak bertato/bertindik</li><li><i class="fa-solid fa-circle-check"></i> Tidak memiliki riwayat penyakit kronis</li><li><i class="fa-solid fa-circle-check"></i> Sehat jasmani & rohani</li></ul>', 90),
('Magang ke Jepang', 'Program magang bergengsi di Jepang melalui skema IM JAPAN & SO (Sending Organization).', 0, '<ul><li><i class="fa-solid fa-circle-check"></i> Laki-laki/Perempuan (Lajang/Menikah)</li><li><i class="fa-solid fa-circle-check"></i> Lulusan MA/SMA/SMK/Paket C/D3/S1</li><li><i class="fa-solid fa-circle-check"></i> Usia 18–26 tahun</li><li><i class="fa-solid fa-circle-check"></i> Tinggi min: L 160cm, P 150cm</li><li><i class="fa-solid fa-circle-check"></i> Mata minus ≤ 1 (untuk laki-laki)</li><li><i class="fa-solid fa-circle-check"></i> Tidak bertato/bertindik</li><li><i class="fa-solid fa-circle-check"></i> Sehat jasmani & rohani</li></ul>', 60),
('Basic English Course', 'Program dasar untuk pemula Bahasa Inggris. Durasi 3 bulan dengan 12 sesi pembelajaran.', 299000, '<ul><li><i class="fa-solid fa-circle-check"></i> Materi pembelajaran dalam 12 modul</li><li><i class="fa-solid fa-circle-check"></i> Akses selamanya ke materi kursus</li><li><i class="fa-solid fa-circle-check"></i> Sertifikat resmi setelah menyelesaikan program</li><li><i class="fa-solid fa-circle-check"></i> Pendampingan sensei via forum online</li></ul>', 90),
('Intermediate English Course', 'Program lanjutan untuk meningkatkan kemampuan Bahasa Inggris. Durasi 3 bulan dengan 16 sesi pembelajaran.', 499000, '<ul><li><i class="fa-solid fa-circle-check"></i> Materi pembelajaran dalam 16 modul advanced</li><li><i class="fa-solid fa-circle-check"></i> Akses selamanya ke materi kursus</li><li><i class="fa-solid fa-circle-check"></i> Sertifikat internasional (TOEIC prep)</li><li><i class="fa-solid fa-circle-check"></i> Live class 2x seminggu dengan sensei</li><li><i class="fa-solid fa-circle-check"></i> Konsultasi personal pembelajaran</li></ul>', 90),
('Advanced English & Business Communication', 'Program profesional untuk komunikasi bisnis dan advanced English. Durasi 4 bulan dengan 20 sesi pembelajaran.', 799000, '<ul><li><i class="fa-solid fa-circle-check"></i> Materi pembelajaran dalam 20 modul premium</li><li><i class="fa-solid fa-circle-check"></i> Akses selamanya ke materi kursus</li><li><i class="fa-solid fa-circle-check"></i> Sertifikat internasional (TOEFL iBT prep)</li><li><i class="fa-solid fa-circle-check"></i> Live class 3x seminggu dengan native speaker</li><li><i class="fa-solid fa-circle-check"></i> Konsultasi personal dan CV review</li><li><i class="fa-solid fa-circle-check"></i> Job placement assistance</li></ul>', 120),
('Listening & Speaking Intensive', 'Program intensif untuk meningkatkan kemampuan mendengarkan dan berbicara. Durasi 2 bulan dengan 10 sesi pembelajaran.', 399000, '<ul><li><i class="fa-solid fa-circle-check"></i> Materi pembelajaran dalam 10 modul fokus speaking</li><li><i class="fa-solid fa-circle-check"></i> Akses selamanya ke materi kursus</li><li><i class="fa-solid fa-circle-check"></i> Sertifikat penyelesaian program</li><li><i class="fa-solid fa-circle-check"></i> Live class 3x seminggu dengan native speaker</li><li><i class="fa-solid fa-circle-check"></i> Recording session untuk evaluasi progress</li></ul>', 60),
('Flexible & Self-Paced Program', 'Program fleksibel tanpa jadwal terikat. Belajar sesuai kecepatan Anda sendiri. Durasi hingga 6 bulan.', 199000, '<ul><li><i class="fa-solid fa-circle-check"></i> Materi pembelajaran lengkap tanpa jadwal fixed</li><li><i class="fa-solid fa-circle-check"></i> Akses selamanya ke materi kursus</li><li><i class="fa-solid fa-circle-check"></i> Sertifikat penyelesaian program</li><li><i class="fa-solid fa-circle-check"></i> Forum diskusi dengan peserta lain</li><li><i class="fa-solid fa-circle-check"></i> Support via email (respons dalam 24 jam)</li></ul>', 180);

-- Add foreign key constraint to users table
-- Using stored procedure to handle errors gracefully
DELIMITER //

CREATE PROCEDURE AddForeignKeyConstraint()
BEGIN
  DECLARE CONTINUE HANDLER FOR 1060 BEGIN END;
  DECLARE CONTINUE HANDLER FOR 1824 BEGIN END;
  
  ALTER TABLE users ADD CONSTRAINT fk_user_program 
  FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE SET NULL;
END //

DELIMITER ;

CALL AddForeignKeyConstraint();
DROP PROCEDURE AddForeignKeyConstraint;
