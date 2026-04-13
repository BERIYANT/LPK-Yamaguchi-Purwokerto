-- Migration: Add listening support and flexible option count for quizzes
-- Date: 2026-01-18

-- Add num_options to quizzes table (2-5 options)
ALTER TABLE quizzes ADD COLUMN num_options INT DEFAULT 5 COMMENT 'Jumlah opsi jawaban (2-5)';

-- Add audio_path to quiz_questions table for listening questions
ALTER TABLE quiz_questions ADD COLUMN audio_path VARCHAR(255) DEFAULT NULL COMMENT 'Path file audio untuk soal listening';

-- Create indexes for better performance
CREATE INDEX idx_quiz_questions_audio ON quiz_questions(audio_path);
