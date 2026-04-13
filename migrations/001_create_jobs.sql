-- SQL migration to create jobs table
CREATE TABLE IF NOT EXISTS jobs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  company VARCHAR(255) NULL,
  location VARCHAR(255) NULL,
  description TEXT NULL,
  requirements TEXT NULL,
  salary VARCHAR(255) NULL,
  employment_type VARCHAR(100) NULL,
  application_link VARCHAR(500) NULL,
  contact_email VARCHAR(255) NULL,
  deadline DATE NULL,
  status ENUM('active','inactive') NOT NULL DEFAULT 'active',
  created_by INT NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  INDEX idx_status (status),
  INDEX idx_deadline (deadline),
  CONSTRAINT fk_jobs_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;