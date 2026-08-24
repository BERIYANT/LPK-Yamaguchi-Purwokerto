-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: May 24, 2026 at 05:30 PM
-- Server version: 11.4.10-MariaDB-cll-lve
-- PHP Version: 8.4.21

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `lpkd3153_elearning_lpkyamaguchi`
--
CREATE DATABASE IF NOT EXISTS `lpkd3153_elearning_lpkyamaguchi` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `lpkd3153_elearning_lpkyamaguchi`;

-- --------------------------------------------------------

--
-- Table structure for table `assignment_banks`
--

CREATE TABLE `assignment_banks` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `content` text DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `created_by` int(11) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `assignment_from_bank`
--

CREATE TABLE `assignment_from_bank` (
  `id` int(11) NOT NULL,
  `task_id` int(11) NOT NULL,
  `bank_assignment_id` int(11) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `attendance_records`
--

CREATE TABLE `attendance_records` (
  `id` int(11) NOT NULL,
  `session_id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `timestamp` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `attendance_sessions`
--

CREATE TABLE `attendance_sessions` (
  `id` int(11) NOT NULL,
  `class_id` int(11) NOT NULL,
  `teacher_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `token` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `expires_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `bank_questions`
--

CREATE TABLE `bank_questions` (
  `id` int(11) NOT NULL,
  `bank_id` int(11) NOT NULL,
  `question` text NOT NULL,
  `image_path` varchar(255) DEFAULT NULL,
  `audio_path` varchar(255) DEFAULT NULL,
  `option_a` varchar(255) NOT NULL,
  `option_b` varchar(255) NOT NULL,
  `option_c` varchar(255) NOT NULL,
  `option_d` varchar(255) NOT NULL,
  `option_e` varchar(255) DEFAULT NULL,
  `correct_option` varchar(1) NOT NULL,
  `option_a_img` varchar(255) DEFAULT NULL,
  `option_b_img` varchar(255) DEFAULT NULL,
  `option_c_img` varchar(255) DEFAULT NULL,
  `option_d_img` varchar(255) DEFAULT NULL,
  `option_e_img` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `certificates`
--

CREATE TABLE `certificates` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `class_id` int(11) DEFAULT NULL,
  `certificate_number` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `issued_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `classes`
--

CREATE TABLE `classes` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `teacher_id` int(11) DEFAULT NULL,
  `schedule` varchar(100) DEFAULT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `description` text DEFAULT NULL,
  `capacity` int(11) DEFAULT 15,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `classes`
--

INSERT INTO `classes` (`id`, `name`, `teacher_id`, `schedule`, `start_time`, `end_time`, `description`, `capacity`, `created_at`) VALUES
(80, 'Kelas Reguler', 851, 'Senin–Jumat,', '08:00:00', '15:00:00', 'Kelas Reguler Batch 1', 15, '2026-01-25 18:08:39'),
(81, 'Kelas Karyawan', 878, 'Senin–Jumat', '19:00:00', '21:30:00', 'Kelas Malam Untuk Karyawan', 15, '2026-01-27 13:38:29');

-- --------------------------------------------------------

--
-- Table structure for table `education_installments`
--

CREATE TABLE `education_installments` (
  `id` int(11) NOT NULL,
  `payment_id` int(11) NOT NULL,
  `installment_number` int(11) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `due_date` date NOT NULL,
  `status` enum('pending','paid','overdue') DEFAULT 'pending',
  `paid_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `enrollments`
--

CREATE TABLE `enrollments` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `class_id` int(11) NOT NULL,
  `enrolled_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `enrollments`
--

INSERT INTO `enrollments` (`id`, `user_id`, `class_id`, `enrolled_at`) VALUES
(11, 852, 80, '2026-01-27 12:34:43'),
(16, 857, 80, '2026-01-27 12:42:53'),
(19, 860, 80, '2026-01-27 12:44:28'),
(20, 861, 80, '2026-01-27 12:45:00'),
(27, 862, 80, '2026-01-27 12:49:22'),
(29, 863, 80, '2026-01-27 12:49:49'),
(30, 867, 80, '2026-01-27 12:50:03'),
(32, 865, 80, '2026-01-27 12:50:38'),
(34, 866, 80, '2026-01-27 12:51:03'),
(36, 870, 80, '2026-01-27 12:51:40'),
(37, 868, 80, '2026-01-27 12:53:19'),
(39, 871, 80, '2026-01-27 13:01:26'),
(40, 872, 80, '2026-01-27 13:03:11'),
(41, 873, 80, '2026-01-27 13:04:01'),
(44, 874, 81, '2026-01-27 13:38:44'),
(45, 858, 81, '2026-01-27 13:39:02'),
(46, 856, 81, '2026-01-27 13:39:16'),
(47, 864, 81, '2026-01-27 13:39:29'),
(48, 855, 81, '2026-01-27 13:39:36'),
(49, 869, 81, '2026-01-27 13:39:53'),
(50, 859, 81, '2026-01-27 13:40:08'),
(51, 854, 81, '2026-01-27 13:40:14'),
(52, 853, 81, '2026-01-27 13:40:24');

-- --------------------------------------------------------

--
-- Table structure for table `finance_categories`
--

CREATE TABLE `finance_categories` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `type` enum('income','expense') NOT NULL,
  `description` text DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `finance_categories`
--

INSERT INTO `finance_categories` (`id`, `name`, `type`, `description`, `is_active`, `created_at`) VALUES
(1, 'Pendaftaran', 'income', 'Biaya pendaftaran siswa baru', 1, '2026-01-24 16:32:32'),
(2, 'Pendidikan', 'income', 'Biaya pendidikan/tuition', 1, '2026-01-24 16:32:32'),
(3, 'Sertifikasi', 'income', 'Biaya sertifikasi', 1, '2026-01-24 16:32:32'),
(4, 'Lainnya (Pemasukan)', 'income', 'Pemasukan lainnya', 1, '2026-01-24 16:32:32'),
(5, 'Gaji Pengajar', 'expense', 'Gaji sensei dan pengajar', 1, '2026-01-24 16:32:32'),
(6, 'Operasional', 'expense', 'Biaya operasional harian', 1, '2026-01-24 16:32:32'),
(7, 'Sewa Tempat', 'expense', 'Biaya sewa tempat', 1, '2026-01-24 16:32:32'),
(8, 'Alat Tulis Kantor', 'expense', 'ATK dan perlengkapan', 1, '2026-01-24 16:32:32'),
(9, 'Internet & Listrik', 'expense', 'Biaya internet dan listrik', 1, '2026-01-24 16:32:32'),
(10, 'Pemeliharaan', 'expense', 'Biaya perawatan dan perbaikan', 1, '2026-01-24 16:32:32'),
(11, 'Lainnya (Pengeluaran)', 'expense', 'Pengeluaran lainnya', 1, '2026-01-24 16:32:32');

-- --------------------------------------------------------

--
-- Table structure for table `finance_transactions`
--

CREATE TABLE `finance_transactions` (
  `id` int(11) NOT NULL,
  `type` enum('income','expense') NOT NULL COMMENT 'income: pemasukan, expense: pengeluaran',
  `category` varchar(100) NOT NULL,
  `amount` decimal(15,2) NOT NULL,
  `description` text DEFAULT NULL,
  `payment_method` varchar(50) DEFAULT NULL COMMENT 'cash, transfer, etc',
  `reference_number` varchar(100) DEFAULT NULL COMMENT 'no referensi/kwitansi',
  `attachment_path` varchar(255) DEFAULT NULL,
  `transaction_date` date NOT NULL,
  `created_by` int(11) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `forum_comments`
--

CREATE TABLE `forum_comments` (
  `id` int(11) NOT NULL,
  `post_id` int(11) DEFAULT NULL,
  `body` text DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `forum_posts`
--

CREATE TABLE `forum_posts` (
  `id` int(11) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `body` text DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `forum_replies`
--

CREATE TABLE `forum_replies` (
  `id` int(11) NOT NULL,
  `post_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `body` text NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `jobs`
--

CREATE TABLE `jobs` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `company` varchar(255) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `requirements` text DEFAULT NULL,
  `salary` varchar(255) DEFAULT NULL,
  `employment_type` varchar(100) DEFAULT NULL,
  `application_link` varchar(500) DEFAULT NULL,
  `contact_email` varchar(255) DEFAULT NULL,
  `deadline` date DEFAULT NULL,
  `status` enum('active','inactive') NOT NULL DEFAULT 'active',
  `created_by` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `materials`
--

CREATE TABLE `materials` (
  `id` int(11) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `content` text DEFAULT NULL,
  `file_path` varchar(500) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `class_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `materials`
--

INSERT INTO `materials` (`id`, `title`, `content`, `file_path`, `created_by`, `created_at`, `class_id`) VALUES
(16, 'Tes', 'tes', 'uploads/material_20260413152807_MOU_MEDPART_BASKETBALL.pdf', 851, '2026-04-13 15:28:07', 81);

-- --------------------------------------------------------

--
-- Table structure for table `material_banks`
--

CREATE TABLE `material_banks` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `content` text DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `created_by` int(11) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `material_from_bank`
--

CREATE TABLE `material_from_bank` (
  `id` int(11) NOT NULL,
  `material_id` int(11) NOT NULL,
  `bank_material_id` int(11) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `payments`
--

CREATE TABLE `payments` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `program_id` int(11) NOT NULL,
  `payment_type` varchar(100) NOT NULL COMMENT 'registration, installment_1, installment_2, installment_3, post_job, pre_mcu, certification, mcu, passport, so_50, so_remaining',
  `amount` decimal(10,2) NOT NULL,
  `proof_file` varchar(255) DEFAULT NULL COMMENT 'Path file bukti pembayaran',
  `status` varchar(50) DEFAULT 'pending' COMMENT 'pending, verified, rejected',
  `payment_date` date DEFAULT NULL,
  `verified_by` int(11) DEFAULT NULL,
  `verified_at` timestamp NULL DEFAULT NULL,
  `rejection_reason` text DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `payments`
--

INSERT INTO `payments` (`id`, `user_id`, `program_id`, `payment_type`, `amount`, `proof_file`, `status`, `payment_date`, `verified_by`, `verified_at`, `rejection_reason`, `notes`, `created_at`, `updated_at`) VALUES
(45, 892, 1, 'registration', 350000.00, 'payment_brianfe25_1455_20260524_170441.png', 'pending', NULL, NULL, NULL, NULL, NULL, '2026-05-24 10:04:41', '2026-05-24 10:04:41');

-- --------------------------------------------------------

--
-- Table structure for table `programs`
--

CREATE TABLE `programs` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `class_type` varchar(100) NOT NULL COMMENT 'Reguler atau Karyawan',
  `schedule` text NOT NULL,
  `registration_fee` decimal(10,2) NOT NULL DEFAULT 350000.00,
  `education_fee` decimal(10,2) NOT NULL DEFAULT 7000000.00,
  `education_installment_1` decimal(10,2) NOT NULL DEFAULT 2000000.00,
  `education_installment_2` decimal(10,2) NOT NULL DEFAULT 1500000.00,
  `education_installment_3` decimal(10,2) NOT NULL DEFAULT 1500000.00,
  `post_job_fee` decimal(10,2) NOT NULL DEFAULT 2000000.00,
  `pre_mcu_fee` decimal(10,2) NOT NULL DEFAULT 400000.00,
  `certification_fee` decimal(10,2) NOT NULL DEFAULT 1500000.00,
  `mcu_fee` decimal(10,2) NOT NULL DEFAULT 1500000.00,
  `passport_fee` decimal(10,2) NOT NULL DEFAULT 1750000.00,
  `so_fee_min` decimal(10,2) NOT NULL DEFAULT 25000000.00,
  `so_fee_max` decimal(10,2) NOT NULL DEFAULT 50000000.00,
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `programs`
--

INSERT INTO `programs` (`id`, `name`, `description`, `class_type`, `schedule`, `registration_fee`, `education_fee`, `education_installment_1`, `education_installment_2`, `education_installment_3`, `post_job_fee`, `pre_mcu_fee`, `certification_fee`, `mcu_fee`, `passport_fee`, `so_fee_min`, `so_fee_max`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 'Program Magang Jepang', 'Program pelatihan bahasa Jepang dan keahlian untuk magang ke Jepang. Program ini mencakup pelatihan bahasa Jepang hingga level N4, sertifikasi, pembekalan budaya kerja Jepang, serta pendampingan hingga pemberangkatan.', 'Reguler', 'Senin - Jumat : 08.00 - 15.00\nSabtu : 08.00 - 12.00', 350000.00, 7000000.00, 2000000.00, 1500000.00, 1500000.00, 2000000.00, 400000.00, 1500000.00, 1500000.00, 1750000.00, 25000000.00, 50000000.00, 1, '2026-01-24 10:03:15', '2026-01-24 10:03:15'),
(2, 'Program Magang Jepang', 'Program pelatihan bahasa Jepang dan keahlian untuk magang ke Jepang (Kelas Karyawan). Program ini dirancang khusus untuk karyawan yang ingin meningkatkan kemampuan bahasa Jepang untuk kesempatan magang.', 'Karyawan', 'Senin - Jumat : 19.00 - 21.30', 350000.00, 7000000.00, 2000000.00, 1500000.00, 1500000.00, 2000000.00, 400000.00, 1500000.00, 1500000.00, 1750000.00, 25000000.00, 50000000.00, 1, '2026-01-24 10:03:15', '2026-01-24 10:03:15');

-- --------------------------------------------------------

--
-- Table structure for table `question_banks`
--

CREATE TABLE `question_banks` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `created_by` int(11) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `quizzes`
--

CREATE TABLE `quizzes` (
  `id` int(11) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `due_at` datetime DEFAULT NULL,
  `attempt_limit` int(11) DEFAULT NULL,
  `duration_minutes` int(11) DEFAULT NULL,
  `class_id` int(11) DEFAULT NULL,
  `num_options` int(11) DEFAULT 5 COMMENT 'Jumlah opsi jawaban (2-5)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `quiz_answers`
--

CREATE TABLE `quiz_answers` (
  `id` int(11) NOT NULL,
  `quiz_id` int(11) DEFAULT NULL,
  `question_id` int(11) DEFAULT NULL,
  `student_id` int(11) DEFAULT NULL,
  `selected_option` char(1) DEFAULT NULL,
  `is_correct` tinyint(1) DEFAULT NULL,
  `answered_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `quiz_from_bank`
--

CREATE TABLE `quiz_from_bank` (
  `id` int(11) NOT NULL,
  `quiz_id` int(11) NOT NULL,
  `bank_question_id` int(11) NOT NULL,
  `source_bank_id` int(11) NOT NULL,
  `question_order` int(11) DEFAULT 0,
  `created_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `quiz_questions`
--

CREATE TABLE `quiz_questions` (
  `id` int(11) NOT NULL,
  `quiz_id` int(11) DEFAULT NULL,
  `question` text DEFAULT NULL,
  `image_path` varchar(255) DEFAULT NULL,
  `option_a` varchar(255) DEFAULT NULL,
  `option_b` varchar(255) DEFAULT NULL,
  `option_c` varchar(255) DEFAULT NULL,
  `option_d` varchar(255) DEFAULT NULL,
  `option_e` text DEFAULT NULL,
  `correct_option` char(1) DEFAULT NULL,
  `option_a_img` varchar(255) DEFAULT NULL,
  `option_b_img` varchar(255) DEFAULT NULL,
  `option_c_img` varchar(255) DEFAULT NULL,
  `option_d_img` varchar(255) DEFAULT NULL,
  `option_e_img` varchar(255) DEFAULT NULL,
  `audio_path` varchar(255) DEFAULT NULL COMMENT 'Path file audio untuk soal listening'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `quiz_scores`
--

CREATE TABLE `quiz_scores` (
  `id` int(11) NOT NULL,
  `quiz_id` int(11) DEFAULT NULL,
  `student_id` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `graded_by` int(11) DEFAULT NULL,
  `graded_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tasks`
--

CREATE TABLE `tasks` (
  `id` int(11) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `due_date` datetime DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `class_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `task_submissions`
--

CREATE TABLE `task_submissions` (
  `id` int(11) NOT NULL,
  `task_id` int(11) DEFAULT NULL,
  `student_id` int(11) DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `submitted_at` datetime DEFAULT NULL,
  `grade` float DEFAULT NULL,
  `graded_by` int(11) DEFAULT NULL,
  `graded_at` datetime DEFAULT NULL,
  `score` decimal(5,2) DEFAULT NULL,
  `feedback` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(100) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `role` varchar(20) DEFAULT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `birth_place` varchar(100) DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `address` text DEFAULT NULL,
  `education` varchar(100) DEFAULT NULL,
  `major` varchar(100) DEFAULT NULL,
  `learning_purpose` text DEFAULT NULL,
  `experience` varchar(50) DEFAULT NULL,
  `ktp_file` varchar(255) DEFAULT NULL,
  `pas_foto_file` varchar(255) DEFAULT NULL,
  `ijazah_file` varchar(255) DEFAULT NULL,
  `bio` text DEFAULT NULL,
  `avatar` varchar(255) DEFAULT NULL,
  `program_id` int(11) DEFAULT NULL,
  `selected_class_type` varchar(50) DEFAULT NULL,
  `payment_status` varchar(50) DEFAULT 'pending',
  `registration_completed` tinyint(1) DEFAULT 0,
  `nik` varchar(50) DEFAULT NULL,
  `height` int(11) DEFAULT NULL,
  `weight` int(11) DEFAULT NULL,
  `blood_type` varchar(5) DEFAULT NULL,
  `father_name` varchar(100) DEFAULT NULL,
  `mother_name` varchar(100) DEFAULT NULL,
  `parent_address` text DEFAULT NULL,
  `parent_phone` varchar(20) DEFAULT NULL,
  `sd_year` year(4) DEFAULT NULL,
  `smp_year` year(4) DEFAULT NULL,
  `sma_year` year(4) DEFAULT NULL,
  `d3_year` year(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `phone`, `password`, `role`, `full_name`, `birth_place`, `birth_date`, `address`, `education`, `major`, `learning_purpose`, `experience`, `ktp_file`, `pas_foto_file`, `ijazah_file`, `bio`, `avatar`, `program_id`, `selected_class_type`, `payment_status`, `registration_completed`, `nik`, `height`, `weight`, `blood_type`, `father_name`, `mother_name`, `parent_address`, `parent_phone`, `sd_year`, `smp_year`, `sma_year`, `d3_year`) VALUES
(233, 'admin', NULL, NULL, 'pbkdf2:sha256:600000$DujewVa6ygj4tNlJ$056431949a8939ac84d1af78a9fa5d471df12bf4aec069098713c57ae6349fc2', 'admin', 'Administrator', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Admin LPK Yamaguchi Purwokerto', 'admin_20260125135449_avatar.jpg', NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(851, 'RizkiHusna', NULL, NULL, 'pbkdf2:sha256:600000$6T5dedllwiZUoxx8$eae179085c03a524c7564ce6e77a3095a1a2eb16c1eca89973282e8ebf9c3b66', 'sensei', 'Rizki Husna', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(852, 'ReinaPrimandini', '', '', 'pbkdf2:sha256:600000$EQ5nqKDsqXUUcMnj$10fa8f6d15ca96dd908b905ce635d814e04f8e305bc2815c9d8d9affc9a6a61e', 'student', 'Reina Ursilla Primandini', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(853, 'IndahSutisna', NULL, NULL, 'pbkdf2:sha256:600000$cR04Mi4iZgvnwRo9$eb01181e6469c14278451f8ac63d227345273ca6f808b7f217863858fd0c7805', 'student', 'Indah Indriana Sutisna', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(854, 'MuhammadAssyauqy', NULL, NULL, 'pbkdf2:sha256:600000$roEtMys5wAN0Pi4q$65304824137e3bc477ea8e47b05cea7c3b35c2abb213761fae5ccba56cb8cc3d', 'student', 'Muhammad Rizqy Assyauqy', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(855, 'AbdytaTegar', NULL, NULL, 'pbkdf2:sha256:600000$ThfU88YMLlYfGls8$bb09c215ca9afde45a0223b857b66be8fb326e557389eaeba4ee7d1d24ca6380', 'student', 'Abdyta Pandunk Maola Tegar', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(856, 'SatrioHidayat', NULL, NULL, 'pbkdf2:sha256:600000$74UN9a8GFBnwhkrd$d3055a40149c7e80dd32375cd18eb681cb163e0953841f5d9d66e70859f49f74', 'student', 'Satrio Nur Owan Hidayat', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(857, 'PangestuPrasojo', '', '', 'pbkdf2:sha256:600000$7MKYiuoZGkkH6X6o$0543764848baadb939963398a2d3de741ca597d6e4d720445ca7f28c36ca2cf0', 'student', 'Pangestu Imam Prasojo', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(858, 'FarhanMargianto', NULL, NULL, 'pbkdf2:sha256:600000$pemnyRgahpmqngan$e183c5d641d8235345605aa567067640dc904974a3b843b48fe5e8c0ace16856', 'student', 'Farhan Margianto', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(859, 'PutraAbdillah', NULL, NULL, 'pbkdf2:sha256:600000$lSyu91VdFUxkQzqS$7c0f1b8eb4f9e8a7d4559b286096afb05b5e320fde6c42dd4bf1be5c8d714c96', 'student', 'Putra Slaris Abdillah', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(860, 'GalangPutra', '', '', 'pbkdf2:sha256:600000$zb4Y3Zg8k7baD1xj$694eefc7bfc7fac1b4926de5993ba3976052e17b1788c18a474283eb90a57358', 'student', 'Galang Pradana Arya Putra', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(861, 'AdnanWasesa', '', '', 'pbkdf2:sha256:600000$h24Yc3xFdyMVSwl0$30c1464ae70ee37c045a383c20550ccb4afb9f1c167c8a5d857e4b23fd043d18', 'student', 'Adnan Kesawa Tunggul Djati Wasesa', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(862, 'ElovaniGinting', NULL, NULL, 'pbkdf2:sha256:600000$CQc9QeynrurY4tuJ$8794ee0e4cf244a337099ccb124801fc260d3ac0e8eaec65aca839478fe8cb6a', 'student', 'Elovani Ginting', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(863, 'VionaKhafifah', NULL, NULL, 'pbkdf2:sha256:600000$7amXNfYsHJ42Vgpo$1fde55c3085dc8bcfbbeb0c4b9d98a050199ff9664364872144b1b14c235036f', 'student', 'Viona Nur Khafifah', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(864, 'YunaAfrista', NULL, NULL, 'pbkdf2:sha256:600000$DwlCnR5q2pXHbbGZ$5c54be101a97234c88fe944a1c64ecb16ca12120aef1fbe1e7e1a5156e9d53d9', 'student', 'Yuna Tri Zenza Nur Afrista', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(865, 'EqiPutra', NULL, NULL, 'pbkdf2:sha256:600000$kMNWxuJ3nnHAAJyB$9be6355858af831262a9acf6eca56a8a8552cd2352e34df026362dbb175a3b67', 'student', 'Eqi Octavian Arifianto Putra', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(866, 'NadyaAmalia', NULL, NULL, 'pbkdf2:sha256:600000$v4nue7AQJlR1yFwW$d8b49df50ea0b2efb97742cdc05044514320c9b782c3e1c2586c7c6d2635d976', 'student', 'Nadya Marsya Amalia', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(867, 'AzizFirmansyah', '', '', 'pbkdf2:sha256:600000$x7hRPGpGJi6bsuql$ab9cf602c49a3550bf9ade02d9175a51ccd79a82749b660d6af0b645391bb761', 'student', 'Aziz Astaman Firmansyah', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(868, 'DaffaFalih', NULL, NULL, 'pbkdf2:sha256:600000$Dtb8Rgwcw1CvrXeC$2c57d29c657f9a3f5524969b59870695edbc99bc386fa536272aeff7b5a3fa24', 'student', 'Daffa Nur Falih', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(869, 'SandyPribadi', NULL, NULL, 'pbkdf2:sha256:600000$AqUOuSeO79jLQznu$bafed5d3af41e485f995f1277964399ff044ddca433783177b84f776f824233a', 'student', 'Sandy Topang Pribadi', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(870, 'CholiviaNursafitri', '', '', 'pbkdf2:sha256:600000$Lqs0fKaJJeXK84Bp$6e265b211d9d689e121b15e19e8aa823da49dc0ecf53ac25b285ecb6e5731ca4', 'student', 'Cholivia Intan Nursafitri', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(871, 'UlviLaili', '', '', 'pbkdf2:sha256:600000$HljhUeZPIttyoPKu$6945a954c57e626da9fc9b927de91b364d0000ad28a6954db568024b3cfb6859', 'student', 'Ulvi Nurul Laili', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(872, 'GladisPasa', '', '', 'pbkdf2:sha256:600000$FuiDgN8JAq64SBUI$92bba3a56c5d1de449352b867bf30f5350bf0338b4d16717ce76b9625347fb80', 'student', 'Gladis Naura Pasa', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(873, 'PametaSabila', '', '', 'pbkdf2:sha256:600000$rJOIJyOXYROPkSIQ$8b1bdec6aa3707f2c649fc25bfcb7f32fd17e293b23da6ad0458c41018ffaa79', 'student', 'Pameta Sabila', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(874, 'Khidirfirmansyah', NULL, NULL, 'pbkdf2:sha256:600000$F2tQgWahiYxnfA4w$09432579998944ad2cebb093db240d8bfe4e7e449995ef9a1b23f78226173fd0', 'student', 'Khidir firmansyah', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(876, 'NurZhafirah', NULL, NULL, 'pbkdf2:sha256:600000$PXaXfVlog57EFdsa$3ae555944bee6d5ffab6d8a1c75eef80d0a0daa7a7ca223d19d3de985e54e254', 'sensei', 'Nur Shabrina Zhafirah', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(877, 'ChoirulGhazy', NULL, NULL, 'pbkdf2:sha256:600000$S2cano4J9PhBXGzq$36f9c60e7ab661f02f48d21a02ba4689ccb3fac89d961a9d9a2fd1ace58b6277', 'sensei', 'Choirul Ghazy', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(878, 'Anggitamirulloh', NULL, NULL, 'pbkdf2:sha256:600000$e50TLrVeDj6N24ES$1048e50f985eeffea20e8ea3a490136931053734f4572e0c8b1b065287f04117', 'sensei', 'Anggit Amirulloh', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(879, 'AlifianSaputra', NULL, NULL, 'pbkdf2:sha256:600000$vxvJRiqL7AtJ7mUd$fe83151b48110601f0d0ee692f818bbacfc72bf7431b9b9f157957e753a27c00', 'sensei', 'Alifian Ardianto Saputra', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(880, 'FajarMaulana', NULL, NULL, 'pbkdf2:sha256:600000$TagZjf9tpEUKt6sw$f496727aee2e4ee88a0a416e761f0a6ac1c6c865a6ca95810ac366d906000cba', 'sensei', 'Fajar Maulana', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(881, 'RikiSantoso', '', '', 'pbkdf2:sha256:600000$uL5qS3M17XJI7i4H$7165dee061273e9231b0e470333d85bbed4128eb6ba2ec32e7516502e9ce8bb9', 'sensei', 'Riki Santoso', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(892, 'brianfe25_1455', 'brianfe25@gmail.com', '08112618282', 'pbkdf2:sha256:600000$jSfaAJlCKIglmMZ7$af5c6fece71251d14e99aa17af3aca4f63dd7d86a4a4f18ad6521e00ef5a7243', 'student', 'Brian Farrel Evandhika', 'Purwokerto', '2005-07-25', 'Gunung Putri Regency B3', 'S1', 'Teknik Informatika', 'Ingin Kerja Ke Jepang', 'none', 'ktp_brianfe25_1455_20260524_170441.png', 'pas_brianfe25_1455_20260524_170441.png', 'ijazah_brianfe25_1455_20260524_170441.png', NULL, NULL, 1, 'Reguler', 'pending_verification', 0, '3302242507050002', 175, 75, 'A', 'Septo Adi Purwoko', 'Sariyani Sophia', 'Gunung Putri Regency B3', '08112609292', '2017', '2020', '2023', '2027');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `assignment_banks`
--
ALTER TABLE `assignment_banks`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_created_by` (`created_by`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- Indexes for table `assignment_from_bank`
--
ALTER TABLE `assignment_from_bank`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_task_id` (`task_id`),
  ADD KEY `idx_bank_assignment_id` (`bank_assignment_id`);

--
-- Indexes for table `attendance_records`
--
ALTER TABLE `attendance_records`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_session_student` (`session_id`,`student_id`),
  ADD KEY `idx_student` (`student_id`),
  ADD KEY `idx_timestamp` (`timestamp`);

--
-- Indexes for table `attendance_sessions`
--
ALTER TABLE `attendance_sessions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `token` (`token`),
  ADD KEY `class_id` (`class_id`),
  ADD KEY `idx_token` (`token`),
  ADD KEY `idx_date` (`date`),
  ADD KEY `idx_teacher` (`teacher_id`),
  ADD KEY `idx_expires_at` (`expires_at`);

--
-- Indexes for table `bank_questions`
--
ALTER TABLE `bank_questions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_bank_id` (`bank_id`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- Indexes for table `certificates`
--
ALTER TABLE `certificates`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `certificate_number` (`certificate_number`),
  ADD KEY `student_id` (`student_id`),
  ADD KEY `class_id` (`class_id`);

--
-- Indexes for table `classes`
--
ALTER TABLE `classes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_teacher_id` (`teacher_id`);

--
-- Indexes for table `education_installments`
--
ALTER TABLE `education_installments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_payment_id` (`payment_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_due_date` (`due_date`);

--
-- Indexes for table `enrollments`
--
ALTER TABLE `enrollments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `class_id` (`class_id`);

--
-- Indexes for table `finance_categories`
--
ALTER TABLE `finance_categories`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_name_type` (`name`,`type`),
  ADD KEY `idx_type` (`type`),
  ADD KEY `idx_is_active` (`is_active`);

--
-- Indexes for table `finance_transactions`
--
ALTER TABLE `finance_transactions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_type` (`type`),
  ADD KEY `idx_category` (`category`),
  ADD KEY `idx_transaction_date` (`transaction_date`),
  ADD KEY `idx_created_by` (`created_by`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- Indexes for table `forum_comments`
--
ALTER TABLE `forum_comments`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `forum_posts`
--
ALTER TABLE `forum_posts`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `forum_replies`
--
ALTER TABLE `forum_replies`
  ADD PRIMARY KEY (`id`),
  ADD KEY `post_id` (`post_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `jobs`
--
ALTER TABLE `jobs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_deadline` (`deadline`),
  ADD KEY `fk_jobs_created_by` (`created_by`);

--
-- Indexes for table `materials`
--
ALTER TABLE `materials`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `material_banks`
--
ALTER TABLE `material_banks`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_created_by` (`created_by`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- Indexes for table `material_from_bank`
--
ALTER TABLE `material_from_bank`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_material_id` (`material_id`),
  ADD KEY `idx_bank_material_id` (`bank_material_id`);

--
-- Indexes for table `payments`
--
ALTER TABLE `payments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_program_id` (`program_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_payment_type` (`payment_type`),
  ADD KEY `fk_payments_verified_by` (`verified_by`);

--
-- Indexes for table `programs`
--
ALTER TABLE `programs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `question_banks`
--
ALTER TABLE `question_banks`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_created_by` (`created_by`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- Indexes for table `quizzes`
--
ALTER TABLE `quizzes`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `quiz_answers`
--
ALTER TABLE `quiz_answers`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `quiz_from_bank`
--
ALTER TABLE `quiz_from_bank`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_quiz_bank_question` (`quiz_id`,`bank_question_id`),
  ADD KEY `source_bank_id` (`source_bank_id`),
  ADD KEY `idx_quiz_id` (`quiz_id`),
  ADD KEY `idx_bank_question_id` (`bank_question_id`);

--
-- Indexes for table `quiz_questions`
--
ALTER TABLE `quiz_questions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_quiz_questions_audio` (`audio_path`);

--
-- Indexes for table `quiz_scores`
--
ALTER TABLE `quiz_scores`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tasks`
--
ALTER TABLE `tasks`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `task_submissions`
--
ALTER TABLE `task_submissions`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `assignment_banks`
--
ALTER TABLE `assignment_banks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `assignment_from_bank`
--
ALTER TABLE `assignment_from_bank`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `attendance_records`
--
ALTER TABLE `attendance_records`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `attendance_sessions`
--
ALTER TABLE `attendance_sessions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `bank_questions`
--
ALTER TABLE `bank_questions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT for table `certificates`
--
ALTER TABLE `certificates`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=46;

--
-- AUTO_INCREMENT for table `classes`
--
ALTER TABLE `classes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=87;

--
-- AUTO_INCREMENT for table `education_installments`
--
ALTER TABLE `education_installments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `enrollments`
--
ALTER TABLE `enrollments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=59;

--
-- AUTO_INCREMENT for table `finance_categories`
--
ALTER TABLE `finance_categories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `finance_transactions`
--
ALTER TABLE `finance_transactions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `forum_comments`
--
ALTER TABLE `forum_comments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `forum_posts`
--
ALTER TABLE `forum_posts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `forum_replies`
--
ALTER TABLE `forum_replies`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `jobs`
--
ALTER TABLE `jobs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `materials`
--
ALTER TABLE `materials`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `material_banks`
--
ALTER TABLE `material_banks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `material_from_bank`
--
ALTER TABLE `material_from_bank`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `payments`
--
ALTER TABLE `payments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=46;

--
-- AUTO_INCREMENT for table `programs`
--
ALTER TABLE `programs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `question_banks`
--
ALTER TABLE `question_banks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `quizzes`
--
ALTER TABLE `quizzes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT for table `quiz_answers`
--
ALTER TABLE `quiz_answers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=595;

--
-- AUTO_INCREMENT for table `quiz_from_bank`
--
ALTER TABLE `quiz_from_bank`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=68;

--
-- AUTO_INCREMENT for table `quiz_questions`
--
ALTER TABLE `quiz_questions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=84;

--
-- AUTO_INCREMENT for table `quiz_scores`
--
ALTER TABLE `quiz_scores`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=38;

--
-- AUTO_INCREMENT for table `tasks`
--
ALTER TABLE `tasks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `task_submissions`
--
ALTER TABLE `task_submissions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=893;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `assignment_banks`
--
ALTER TABLE `assignment_banks`
  ADD CONSTRAINT `assignment_banks_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `assignment_from_bank`
--
ALTER TABLE `assignment_from_bank`
  ADD CONSTRAINT `assignment_from_bank_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `assignment_from_bank_ibfk_2` FOREIGN KEY (`bank_assignment_id`) REFERENCES `assignment_banks` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `attendance_records`
--
ALTER TABLE `attendance_records`
  ADD CONSTRAINT `attendance_records_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `attendance_sessions` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `attendance_records_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `attendance_sessions`
--
ALTER TABLE `attendance_sessions`
  ADD CONSTRAINT `attendance_sessions_ibfk_1` FOREIGN KEY (`class_id`) REFERENCES `classes` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `attendance_sessions_ibfk_2` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `bank_questions`
--
ALTER TABLE `bank_questions`
  ADD CONSTRAINT `bank_questions_ibfk_1` FOREIGN KEY (`bank_id`) REFERENCES `question_banks` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `certificates`
--
ALTER TABLE `certificates`
  ADD CONSTRAINT `certificates_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `certificates_ibfk_2` FOREIGN KEY (`class_id`) REFERENCES `classes` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `classes`
--
ALTER TABLE `classes`
  ADD CONSTRAINT `fk_classes_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `enrollments`
--
ALTER TABLE `enrollments`
  ADD CONSTRAINT `enrollments_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `enrollments_ibfk_2` FOREIGN KEY (`class_id`) REFERENCES `classes` (`id`);

--
-- Constraints for table `finance_transactions`
--
ALTER TABLE `finance_transactions`
  ADD CONSTRAINT `fk_finance_transactions_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `jobs`
--
ALTER TABLE `jobs`
  ADD CONSTRAINT `fk_jobs_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `material_banks`
--
ALTER TABLE `material_banks`
  ADD CONSTRAINT `material_banks_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `material_from_bank`
--
ALTER TABLE `material_from_bank`
  ADD CONSTRAINT `material_from_bank_ibfk_1` FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `material_from_bank_ibfk_2` FOREIGN KEY (`bank_material_id`) REFERENCES `material_banks` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `payments`
--
ALTER TABLE `payments`
  ADD CONSTRAINT `fk_payments_program` FOREIGN KEY (`program_id`) REFERENCES `programs` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_payments_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_payments_verified_by` FOREIGN KEY (`verified_by`) REFERENCES `users` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `question_banks`
--
ALTER TABLE `question_banks`
  ADD CONSTRAINT `question_banks_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `quiz_from_bank`
--
ALTER TABLE `quiz_from_bank`
  ADD CONSTRAINT `quiz_from_bank_ibfk_1` FOREIGN KEY (`quiz_id`) REFERENCES `quizzes` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `quiz_from_bank_ibfk_2` FOREIGN KEY (`bank_question_id`) REFERENCES `bank_questions` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `quiz_from_bank_ibfk_3` FOREIGN KEY (`source_bank_id`) REFERENCES `question_banks` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
