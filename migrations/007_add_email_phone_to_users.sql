-- Migration: Add email and phone columns to users table
-- Created: 2026-01-21
-- Description: Add email and phone fields for public student registration

ALTER TABLE `users` 
ADD COLUMN `email` VARCHAR(100) NULL AFTER `full_name`,
ADD COLUMN `phone` VARCHAR(20) NULL AFTER `email`;

-- Create index for email lookups
CREATE INDEX `idx_email` ON `users`(`email`);
