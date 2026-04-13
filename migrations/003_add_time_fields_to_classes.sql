-- Add time fields to classes table
ALTER TABLE `classes` 
ADD COLUMN `start_time` TIME DEFAULT NULL AFTER `schedule`,
ADD COLUMN `end_time` TIME DEFAULT NULL AFTER `start_time`;

-- Update existing classes with time from schedule if possible
-- Format dari schedule: "Senin–Jumat,15.00–17.00" atau "Senin & Rabu, 09:00-11:00"
UPDATE `classes` 
SET `start_time` = '15:00', `end_time` = '17:00' 
WHERE `id` = 74;

UPDATE `classes` 
SET `start_time` = '15:00', `end_time` = '17:00' 
WHERE `id` = 75;
