-- Migration: Add attendance session expiry tracking
-- Date: 2026-01-19

ALTER TABLE attendance_sessions 
ADD COLUMN expires_at TIMESTAMP NULL DEFAULT NULL;

-- Optional: Add index for faster queries on expiry
CREATE INDEX idx_expires_at ON attendance_sessions(expires_at);
