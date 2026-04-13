-- Migration: Create Question Bank System
-- Purpose: Allows teachers to create and reuse question banks across multiple classes

-- Table for storing question banks
CREATE TABLE IF NOT EXISTS question_banks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_created_by (created_by),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table for storing questions in bank (reusable questions)
CREATE TABLE IF NOT EXISTS bank_questions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    bank_id INT NOT NULL,
    question TEXT NOT NULL,
    image_path VARCHAR(255),
    audio_path VARCHAR(255),
    option_a VARCHAR(255) NOT NULL,
    option_b VARCHAR(255) NOT NULL,
    option_c VARCHAR(255) NOT NULL,
    option_d VARCHAR(255) NOT NULL,
    option_e VARCHAR(255),
    correct_option VARCHAR(1) NOT NULL,
    option_a_img VARCHAR(255),
    option_b_img VARCHAR(255),
    option_c_img VARCHAR(255),
    option_d_img VARCHAR(255),
    option_e_img VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bank_id) REFERENCES question_banks(id) ON DELETE CASCADE,
    INDEX idx_bank_id (bank_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table for tracking which questions from bank are used in which quizzes
CREATE TABLE IF NOT EXISTS quiz_from_bank (
    id INT PRIMARY KEY AUTO_INCREMENT,
    quiz_id INT NOT NULL,
    bank_question_id INT NOT NULL,
    source_bank_id INT NOT NULL,
    question_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE,
    FOREIGN KEY (bank_question_id) REFERENCES bank_questions(id) ON DELETE CASCADE,
    FOREIGN KEY (source_bank_id) REFERENCES question_banks(id) ON DELETE CASCADE,
    UNIQUE KEY unique_quiz_bank_question (quiz_id, bank_question_id),
    INDEX idx_quiz_id (quiz_id),
    INDEX idx_bank_question_id (bank_question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table for assignment banks (similar concept for tugas/assignment)
CREATE TABLE IF NOT EXISTS assignment_banks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    content TEXT,
    file_path VARCHAR(255),
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_created_by (created_by),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Track which assignments are from banks
CREATE TABLE IF NOT EXISTS assignment_from_bank (
    id INT PRIMARY KEY AUTO_INCREMENT,
    task_id INT NOT NULL,
    bank_assignment_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (bank_assignment_id) REFERENCES assignment_banks(id) ON DELETE CASCADE,
    INDEX idx_task_id (task_id),
    INDEX idx_bank_assignment_id (bank_assignment_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
