-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3307
-- Generation Time: Jan 16, 2026 at 04:42 PM
-- Server version: 8.0.30
-- PHP Version: 8.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `medicine_store_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `expiry_returns`
--

CREATE TABLE `expiry_returns` (
  `id` bigint UNSIGNED NOT NULL,
  `supplier_id` bigint NOT NULL,
  `return_number` varchar(64) NOT NULL,
  `return_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `total_amount` decimal(12,2) NOT NULL DEFAULT '0.00',
  `remarks` text,
  `is_returned` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `expiry_return_items`
--

CREATE TABLE `expiry_return_items` (
  `id` bigint UNSIGNED NOT NULL,
  `expiry_return_id` bigint NOT NULL,
  `medicine_id` bigint NOT NULL,
  `batch_number` varchar(128) DEFAULT NULL,
  `quantity` int NOT NULL,
  `rate` decimal(10,2) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `medicine_inventory`
--

CREATE TABLE `medicine_inventory` (
  `id` bigint UNSIGNED NOT NULL,
  `name` varchar(255) NOT NULL,
  `medicine_uses` text,
  `hsn_code` varchar(20) DEFAULT NULL,
  `unit` varchar(32) NOT NULL DEFAULT 'strip',
  `packing_details` varchar(128) DEFAULT NULL,
  `low_stock_alert` int NOT NULL DEFAULT '0',
  `batch_number` varchar(128) NOT NULL,
  `manufacturing_date` date DEFAULT NULL,
  `expiry_date` date DEFAULT NULL,
  `rack_location` varchar(64) DEFAULT NULL,
  `purchase_price` decimal(10,2) NOT NULL,
  `mrp` decimal(10,2) NOT NULL,
  `current_stock` int NOT NULL DEFAULT '0',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `is_expired` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `medicine_inventory`
--

INSERT INTO `medicine_inventory` (`id`, `name`, `medicine_uses`, `hsn_code`, `unit`, `packing_details`, `low_stock_alert`, `batch_number`, `manufacturing_date`, `expiry_date`, `rack_location`, `purchase_price`, `mrp`, `current_stock`, `is_active`, `is_expired`, `created_at`, `updated_at`) VALUES
(1, 'Paracetamol updated 500mg', 'Pain relief and fever reduction', '300450', 'strip', '10 tablets per strip', 20, 'BATCH-PARA-001', '2025-01-01', '2027-01-01', 'RACK-A1', 25.00, 40.00, 100, 1, 0, '2026-01-16 20:01:37', '2026-01-16 20:02:51'),
(2, 'Paracetamol updated 100mg', 'Pain relief and fever reduction', '300450', 'strip', '10 tablets per strip', 0, 'BATCH-PARA-002', '2026-01-16', '2026-02-28', 'RACK-A1', 25.00, 40.00, 0, 1, 0, '2026-01-16 20:15:34', '2026-01-16 20:15:34'),
(3, 'Paracetamol 500mg', 'Pain relief and fever reduction', '30045010', 'strip', '10 tablets per strip', 20, 'PCM500-A1', '2024-01-15', '2026-01-14', 'RACK-A1', 18.50, 25.00, 120, 1, 0, '2026-01-16 20:38:11', '2026-01-16 20:38:11'),
(4, 'Paracetamol 500mg', 'Pain relief and fever reduction', '30045010', 'strip', '10 tablets per strip', 20, 'PCM500-B2', '2023-12-10', '2025-12-09', 'RACK-A1', 18.00, 25.00, 60, 1, 0, '2026-01-16 20:38:11', '2026-01-16 20:38:11'),
(5, 'Amoxicillin 250mg', 'Bacterial infection treatment', '30042019', 'strip', '10 capsules per strip', 10, 'AMX250-X9', '2024-02-01', '2026-01-31', 'RACK-B2', 55.00, 72.00, 40, 1, 0, '2026-01-16 20:38:11', '2026-01-16 20:38:11'),
(6, 'Amoxicillin 500mg', 'Bacterial infection treatment', '30042019', 'strip', '10 capsules per strip', 10, 'AMX500-Y1', '2023-11-20', '2025-11-19', 'RACK-B2', 85.00, 110.00, 25, 1, 0, '2026-01-16 20:38:11', '2026-01-16 20:38:11'),
(7, 'Cetirizine 10mg', 'Allergy relief', '30049099', 'strip', '10 tablets per strip', 15, 'CTZ10-C3', '2024-03-05', '2027-03-04', 'RACK-C1', 12.00, 20.00, 200, 1, 0, '2026-01-16 20:38:11', '2026-01-16 20:38:11'),
(8, 'Azithromycin 500mg', 'Respiratory and bacterial infections', '30042015', 'strip', '3 tablets per strip', 5, 'AZM500-Z7', '2024-01-01', '2026-12-31', 'RACK-B3', 95.00, 130.00, 18, 1, 0, '2026-01-16 20:38:11', '2026-01-16 20:38:11'),
(9, 'Pantoprazole 40mg', 'Acid reflux and GERD', '30049099', 'strip', '10 tablets per strip', 20, 'PAN40-P5', '2023-10-15', '2025-10-14', 'RACK-D1', 22.00, 35.00, 90, 1, 0, '2026-01-16 20:38:11', '2026-01-16 20:38:11'),
(10, 'Vitamin C Tablets', 'Immunity booster', '21069099', 'bottle', '60 tablets per bottle', 5, 'VITC-60-01', '2024-04-01', '2026-03-31', 'RACK-E1', 110.00, 180.00, 35, 1, 0, '2026-01-16 20:38:11', '2026-01-16 20:38:11'),
(11, 'Cough Syrup', 'Relief from cough and cold', '30049099', 'bottle', '100 ml bottle', 10, 'CS-100-09', '2023-08-01', '2025-07-31', 'RACK-F2', 48.00, 75.00, 22, 1, 0, '2026-01-16 20:38:11', '2026-01-16 20:38:11'),
(12, 'Ibuprofen 400mg', 'Pain and inflammation relief', '30045020', 'strip', '10 tablets per strip', 15, 'IBU400-I4', '2024-02-20', '2026-02-19', 'RACK-A2', 30.00, 45.00, 70, 1, 0, '2026-01-16 20:38:11', '2026-01-16 20:38:11'),
(13, 'Insulin Injection', 'Diabetes management', '30043100', 'vial', '10 ml vial', 1, 'INS-10ML-77', '2024-06-01', '2025-05-31', 'COLD-RACK-1', 420.00, 550.00, 8, 1, 0, '2026-01-16 20:38:11', '2026-01-16 21:05:11'),
(14, 'Metformin 500mg', 'Diabetes management', '30049099', 'strip', '10 tablets per strip', 20, 'MET500-OLD', '2022-01-01', '2024-01-01', 'RACK-D2', 10.00, 28.00, 0, 0, 1, '2026-01-16 20:38:11', '2026-01-16 20:41:36');

-- --------------------------------------------------------

--
-- Table structure for table `purchase_invoices`
--

CREATE TABLE `purchase_invoices` (
  `id` bigint UNSIGNED NOT NULL,
  `supplier_id` bigint NOT NULL,
  `invoice_number` varchar(64) NOT NULL,
  `invoice_date` date NOT NULL,
  `payment_mode` varchar(16) NOT NULL DEFAULT 'Cash',
  `total_amount` decimal(12,2) NOT NULL DEFAULT '0.00',
  `amount_paid` decimal(12,2) NOT NULL DEFAULT '0.00',
  `remarks` text,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `purchase_invoice_items`
--

CREATE TABLE `purchase_invoice_items` (
  `id` bigint UNSIGNED NOT NULL,
  `purchase_invoice_id` bigint NOT NULL,
  `medicine_id` bigint NOT NULL,
  `quantity` int NOT NULL,
  `purchase_price` decimal(10,2) DEFAULT NULL,
  `mrp` decimal(10,2) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sales_invoices`
--

CREATE TABLE `sales_invoices` (
  `id` bigint UNSIGNED NOT NULL,
  `invoice_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `payment_mode` varchar(16) NOT NULL,
  `customer_name` varchar(255) DEFAULT NULL,
  `doctor_name` varchar(255) DEFAULT NULL,
  `total_medicines` int NOT NULL DEFAULT '0',
  `total_price` decimal(12,2) NOT NULL DEFAULT '0.00',
  `discount` int NOT NULL DEFAULT '10',
  `discount_price` decimal(12,2) NOT NULL DEFAULT '0.00',
  `final_selling_price` decimal(12,2) NOT NULL DEFAULT '0.00',
  `remarks` text,
  `mark_as_paid` tinyint(1) NOT NULL DEFAULT '0',
  `is_applied_item_level_discount` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sales_invoice_items`
--

CREATE TABLE `sales_invoice_items` (
  `id` bigint UNSIGNED NOT NULL,
  `sales_invoice_id` bigint NOT NULL,
  `medicine_id` bigint NOT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  `mrp` decimal(10,2) NOT NULL,
  `discount` int NOT NULL DEFAULT '10',
  `discount_price` decimal(10,2) NOT NULL,
  `selling_price` decimal(10,2) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `store_profile`
--

CREATE TABLE `store_profile` (
  `id` bigint UNSIGNED NOT NULL,
  `store_name` varchar(255) NOT NULL,
  `owner_name` varchar(255) DEFAULT NULL,
  `gst_number` varchar(20) DEFAULT NULL COMMENT 'Printed on invoice only. No GST calculations.',
  `drug_license_number` varchar(64) DEFAULT NULL,
  `city` varchar(128) DEFAULT NULL,
  `state` varchar(128) DEFAULT NULL,
  `pincode` varchar(10) DEFAULT NULL,
  `country` varchar(64) NOT NULL DEFAULT 'India',
  `address_line` varchar(255) DEFAULT NULL,
  `invoice_prefix` varchar(20) NOT NULL DEFAULT 'PMS' COMMENT 'Used for invoice numbering, e.g., PMS-00001',
  `invoice_footer_note` text,
  `logo` varchar(255) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `store_profile`
--

INSERT INTO `store_profile` (`id`, `store_name`, `owner_name`, `gst_number`, `drug_license_number`, `city`, `state`, `pincode`, `country`, `address_line`, `invoice_prefix`, `invoice_footer_note`, `logo`, `created_at`, `updated_at`) VALUES
(1, 'Panda Medicine Store', 'Pratik Kumar Pradhan', '08ABCDE9999F1Z8', '21/001/12345678', 'Angul', 'Odisha', '759125', 'India', 'Angul, Boinda', 'PMS', 'Thank You For Shopping. ', 'store_logo/Chicken_Hyderabadi.jpg', '2026-01-16 18:58:56.619196', '2026-01-16 18:58:56.619292');

-- --------------------------------------------------------

--
-- Table structure for table `suppliers`
--

CREATE TABLE `suppliers` (
  `id` bigint UNSIGNED NOT NULL,
  `name` varchar(255) NOT NULL,
  `company_name` varchar(255) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  `address` text,
  `gst_number` varchar(20) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `suppliers`
--

INSERT INTO `suppliers` (`id`, `name`, `company_name`, `phone`, `email`, `address`, `gst_number`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 'Rakesh Sharma', 'Sharma Medical Distributors', '9876543210', 'rakesh@sharmamedical.com', 'Shop No. 12, Gandhi Market, Delhi', '07AABCS1234F1Z1', 1, '2026-01-16 21:46:23', '2026-01-16 21:46:23'),
(2, 'Amit Verma', 'Verma Pharma Supplies', '9812345678', 'amit@vermapharma.in', 'Plot 45, Industrial Area, Noida, UP', '09AAACV4567G1Z2', 1, '2026-01-16 21:46:23', '2026-01-16 21:46:23'),
(3, 'Sunita Patel', 'Patel Healthcare', '9823456789', 'sunita@patelhealthcare.in', 'Near Civil Hospital, Ahmedabad, Gujarat', '24AABCP7890H1Z3', 1, '2026-01-16 21:46:23', '2026-01-16 21:46:23'),
(4, 'Mahesh Iyer ok', 'Iyer Medico Agencies ok', '9845012345', 'mahesh@iyermedico.com', 'MG Road, Bengaluru, Karnataka', '29AACCI2345J1Z4', 1, '2026-01-16 21:46:23', '2026-01-16 22:08:17'),
(5, 'Suresh Rao', 'Rao Pharmaceuticals', '9900123456', 'suresh@raopharma.in', 'Station Road, Vijayawada, Andhra Pradesh', '37AABCR3456K1Z5', 1, '2026-01-16 21:46:23', '2026-01-16 21:46:23'),
(6, 'Neha Gupta', 'Gupta Medical Stores', '9898989898', 'neha@guptamedical.co', 'Sector 18, Chandigarh', '04AABCG4567L1Z6', 1, '2026-01-16 21:46:23', '2026-01-16 21:46:23'),
(7, 'Anil Mehta', 'Mehta Drug House', '9765432109', 'anil@mehtadrugs.in', 'Ring Road, Surat, Gujarat', '24AABCM5678M1Z7', 1, '2026-01-16 21:46:23', '2026-01-16 21:46:23'),
(8, 'Pankaj Singh', 'Singh Pharma World', '9700011122', 'pankaj@singhpharma.com', 'Kankarbagh, Patna, Bihar', '10AABCS6789N1Z8', 1, '2026-01-16 21:46:23', '2026-01-16 21:46:23'),
(9, 'Kavita Nair', 'Nair Medical Agencies', '9944556677', 'kavita@nairmedical.in', 'Kaloor, Kochi, Kerala', '32AABCN7890P1Z9', 1, '2026-01-16 21:46:23', '2026-01-16 21:46:23'),
(10, 'Rajesh Khanna', 'Khanna Healthcare Pvt Ltd', '9887766554', 'rajesh@khannahealthcare.com', 'Model Town, Ludhiana, Punjab', '03AABCK8901Q1Z0', 1, '2026-01-16 21:46:23', '2026-01-16 21:46:23'),
(11, 'Deepak Joshi', 'Joshi Pharma Link', '9955443322', 'deepak@jospharma.in', 'Ashok Nagar, Jaipur, Rajasthan', '08AABCJ9012R1Z1', 1, '2026-01-16 21:46:23', '2026-01-16 21:46:23'),
(12, 'Farhan Khan', 'Khan Medical Suppliers', '9911223344', 'farhan@khanmedical.in', 'Banjara Hills, Hyderabad, Telangana', '36AABCK0123S1Z2', 1, '2026-01-16 21:46:23', '2026-01-16 21:46:23'),
(13, 'Vikram Malhotra', 'Malhotra Pharma Distributors', '9000012345', 'vikram@malhotrapharma.in', 'Civil Lines, Nagpur, Maharashtra', '27AABCM1234T1Z3', 1, '2026-01-16 21:46:23', '2026-01-16 21:46:34'),
(14, 'adcadc', 'cacac', 'cadccacacac', 'cacacac@gm.com', 'cacacac', 'cacacac', 1, '2026-01-16 22:08:47', '2026-01-16 22:08:47');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` bigint NOT NULL,
  `username` varchar(64) NOT NULL,
  `password` varchar(128) NOT NULL,
  `full_name` varchar(128) NOT NULL,
  `mobile_number` varchar(15) DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  `role` varchar(20) NOT NULL DEFAULT 'OWNER',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `last_login` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `expiry_returns`
--
ALTER TABLE `expiry_returns`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uk_er_return_number` (`return_number`),
  ADD KEY `idx_er_supplier` (`supplier_id`),
  ADD KEY `idx_er_number` (`return_number`),
  ADD KEY `idx_er_returned` (`is_returned`);

--
-- Indexes for table `expiry_return_items`
--
ALTER TABLE `expiry_return_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_er_item_er` (`expiry_return_id`),
  ADD KEY `idx_er_item_med` (`medicine_id`);

--
-- Indexes for table `medicine_inventory`
--
ALTER TABLE `medicine_inventory`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_med_inv_name` (`name`),
  ADD KEY `idx_med_inv_name_batch` (`name`,`batch_number`),
  ADD KEY `idx_med_inv_expiry` (`expiry_date`),
  ADD KEY `idx_med_inv_stock` (`current_stock`),
  ADD KEY `idx_med_inv_active` (`is_active`),
  ADD KEY `idx_med_inv_active_expiry` (`is_active`,`expiry_date`),
  ADD KEY `idx_med_inv_active_stock` (`is_active`,`current_stock`),
  ADD KEY `idx_med_inv_rack` (`rack_location`),
  ADD KEY `idx_med_expiry` (`expiry_date`),
  ADD KEY `idx_med_created_at` (`created_at`);

--
-- Indexes for table `purchase_invoices`
--
ALTER TABLE `purchase_invoices`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_purchase_invoice_supplier` (`supplier_id`),
  ADD KEY `idx_purchase_invoice_number` (`invoice_number`),
  ADD KEY `idx_purchase_invoice_date` (`invoice_date`);

--
-- Indexes for table `purchase_invoice_items`
--
ALTER TABLE `purchase_invoice_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_pi_item_pi` (`purchase_invoice_id`),
  ADD KEY `idx_pi_item_med` (`medicine_id`);

--
-- Indexes for table `sales_invoices`
--
ALTER TABLE `sales_invoices`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_si_date` (`invoice_date`),
  ADD KEY `idx_si_ild` (`is_applied_item_level_discount`);

--
-- Indexes for table `sales_invoice_items`
--
ALTER TABLE `sales_invoice_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_sii_si` (`sales_invoice_id`),
  ADD KEY `idx_sii_med` (`medicine_id`);

--
-- Indexes for table `store_profile`
--
ALTER TABLE `store_profile`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uniq_store_profile_store_name` (`store_name`),
  ADD KEY `idx_store_profile_store_name` (`store_name`);

--
-- Indexes for table `suppliers`
--
ALTER TABLE `suppliers`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_supplier_name` (`name`),
  ADD KEY `idx_supplier_phone` (`phone`),
  ADD KEY `idx_supplier_active` (`is_active`),
  ADD KEY `idx_supplier_created_at` (`created_at`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ux_users_username` (`username`),
  ADD KEY `idx_users_mobile` (`mobile_number`),
  ADD KEY `idx_users_email` (`email`),
  ADD KEY `idx_users_role` (`role`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `expiry_returns`
--
ALTER TABLE `expiry_returns`
  MODIFY `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `expiry_return_items`
--
ALTER TABLE `expiry_return_items`
  MODIFY `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `medicine_inventory`
--
ALTER TABLE `medicine_inventory`
  MODIFY `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `purchase_invoices`
--
ALTER TABLE `purchase_invoices`
  MODIFY `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `purchase_invoice_items`
--
ALTER TABLE `purchase_invoice_items`
  MODIFY `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `sales_invoices`
--
ALTER TABLE `sales_invoices`
  MODIFY `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `sales_invoice_items`
--
ALTER TABLE `sales_invoice_items`
  MODIFY `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `store_profile`
--
ALTER TABLE `store_profile`
  MODIFY `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `suppliers`
--
ALTER TABLE `suppliers`
  MODIFY `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
