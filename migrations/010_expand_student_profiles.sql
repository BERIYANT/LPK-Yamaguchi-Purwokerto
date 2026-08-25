-- Tambahkan kolom biodata hanya jika belum tersedia.
-- Kompatibel untuk MySQL/cPanel dan aman dijalankan ulang.

SET @db := DATABASE();

SET @sql := IF(
    EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='student_profiles' AND COLUMN_NAME='school_name'),
    'SELECT 1', 'ALTER TABLE `student_profiles` ADD COLUMN `school_name` VARCHAR(200) NULL AFTER `birth_date`'
); PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := IF(
    EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='student_profiles' AND COLUMN_NAME='nik'),
    'SELECT 1', 'ALTER TABLE `student_profiles` ADD COLUMN `nik` VARCHAR(30) NULL AFTER `school_name`'
); PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := IF(
    EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='student_profiles' AND COLUMN_NAME='rt_rw'),
    'SELECT 1', 'ALTER TABLE `student_profiles` ADD COLUMN `rt_rw` VARCHAR(20) NULL AFTER `address`'
); PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := IF(
    EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='student_profiles' AND COLUMN_NAME='village'),
    'SELECT 1', 'ALTER TABLE `student_profiles` ADD COLUMN `village` VARCHAR(100) NULL AFTER `rt_rw`'
); PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := IF(
    EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='student_profiles' AND COLUMN_NAME='district'),
    'SELECT 1', 'ALTER TABLE `student_profiles` ADD COLUMN `district` VARCHAR(100) NULL AFTER `village`'
); PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := IF(
    EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='student_profiles' AND COLUMN_NAME='city'),
    'SELECT 1', 'ALTER TABLE `student_profiles` ADD COLUMN `city` VARCHAR(100) NULL AFTER `district`'
); PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := IF(
    EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='student_profiles' AND COLUMN_NAME='province'),
    'SELECT 1', 'ALTER TABLE `student_profiles` ADD COLUMN `province` VARCHAR(100) NULL AFTER `city`'
); PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := IF(
    EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='student_profiles' AND COLUMN_NAME='graduation_date'),
    'SELECT 1', 'ALTER TABLE `student_profiles` ADD COLUMN `graduation_date` DATE NULL AFTER `enrollment_date`'
); PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := IF(
    EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='student_profiles' AND COLUMN_NAME='departure_date'),
    'SELECT 1', 'ALTER TABLE `student_profiles` ADD COLUMN `departure_date` DATE NULL AFTER `graduation_date`'
); PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := IF(
    EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='student_profiles' AND COLUMN_NAME='job_sector'),
    'SELECT 1', 'ALTER TABLE `student_profiles` ADD COLUMN `job_sector` VARCHAR(150) NULL AFTER `departure_date`'
); PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := IF(
    EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='student_profiles' AND COLUMN_NAME='placement'),
    'SELECT 1', 'ALTER TABLE `student_profiles` ADD COLUMN `placement` VARCHAR(150) NULL AFTER `job_sector`'
); PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := IF(
    EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='student_profiles' AND COLUMN_NAME='notes'),
    'SELECT 1', 'ALTER TABLE `student_profiles` ADD COLUMN `notes` VARCHAR(255) NULL AFTER `status`'
); PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql := NULL;
SET @db := NULL;
