-- Medical Store DB Schema
-- Engine = InnoDB, Charset = utf8mb4

SET FOREIGN_KEY_CHECKS = 0;

-- ==========================
-- users
-- ==========================
CREATE TABLE `users` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(64) NOT NULL,
  `password` VARCHAR(128) NOT NULL,
  `full_name` VARCHAR(128) NOT NULL,
  `mobile_number` VARCHAR(15),
  `email` VARCHAR(254),
  `role` VARCHAR(20) NOT NULL DEFAULT 'OWNER',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `last_login` DATETIME NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_users_username` (`username`),
  KEY `idx_users_mobile` (`mobile_number`),
  KEY `idx_users_email` (`email`),
  KEY `idx_users_role` (`role`)
);

-- ==========================
-- store_profile
-- ==========================
CREATE TABLE `store_profile` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `store_name` VARCHAR(255) NOT NULL,
  `owner_name` VARCHAR(255) DEFAULT NULL,
  `gst_number` VARCHAR(20) DEFAULT NULL COMMENT 'Printed on invoice only. No GST calculations.',
  `drug_license_number` VARCHAR(64) DEFAULT NULL,
  `city` VARCHAR(128) DEFAULT NULL,
  `state` VARCHAR(128) DEFAULT NULL,
  `pincode` VARCHAR(10) DEFAULT NULL,
  `country` VARCHAR(64) NOT NULL DEFAULT 'India',
  `address_line` VARCHAR(255) DEFAULT NULL,
  `invoice_prefix` VARCHAR(20) NOT NULL DEFAULT 'PMS' COMMENT 'Used for invoice numbering, e.g., PMS-00001',
  `invoice_footer_note` TEXT DEFAULT NULL,
  `logo` VARCHAR(255) DEFAULT NULL,
  `created_at` DATETIME(6) NOT NULL,
  `updated_at` DATETIME(6) NOT NULL,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_store_profile_store_name` (`store_name`),
  KEY `idx_store_profile_store_name` (`store_name`)
);

-- ==========================
-- app_settings
-- ==========================
CREATE TABLE `app_settings` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `key` VARCHAR(64) NOT NULL,
  `value` TEXT,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_app_settings_key` (`key`)
);

-- ==========================
-- categories
-- ==========================
CREATE TABLE `categories` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(128) NOT NULL,
  `description` TEXT,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_categories_name` (`name`),
  KEY `idx_categories_name` (`name`)
);

INSERT INTO `categories` (`name`, `description`, `created_at`, `updated_at`) VALUES
('Medicines', 'All types of prescription and over-the-counter medicines', NOW(6), NOW(6)),
('Health Supplements', 'Vitamins, minerals, and daily health supplements', NOW(6), NOW(6)),
('Personal Care', 'Personal hygiene and daily care products', NOW(6), NOW(6)),
('Baby Care', 'Baby food, diapers, and baby health products', NOW(6), NOW(6)),
('Medical Devices', 'Healthcare devices like BP monitors and glucometers', NOW(6), NOW(6)),
('Ayurvedic', 'Ayurvedic and herbal healthcare products', NOW(6), NOW(6)),
('Homeopathy', 'Homeopathic medicines and remedies', NOW(6), NOW(6)),
('Skin Care', 'Skin treatment and dermatology products', NOW(6), NOW(6)),
('Hair Care', 'Hair treatment, oils, and hair growth solutions', NOW(6), NOW(6)),
('Oral Care', 'Dental and oral hygiene products', NOW(6), NOW(6)),
('Nutrition', 'Protein powders, energy drinks, and nutrition products', NOW(6), NOW(6)),
('Women Care', 'Healthcare products focused on women wellness', NOW(6), NOW(6)),
('Men Care', 'Healthcare and grooming products for men', NOW(6), NOW(6)),
('First Aid', 'Emergency and first aid medical supplies', NOW(6), NOW(6)),
('Elder Care', 'Healthcare and support products for senior citizens', NOW(6), NOW(6));


-- ==========================
-- manufacturers
-- ==========================
CREATE TABLE `manufacturers` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `contact_person` VARCHAR(255),
  `phone` VARCHAR(20),
  `email` VARCHAR(254),
  `address` TEXT,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_manufacturers_name` (`name`),
  KEY `idx_manufacturers_name` (`name`)
);

-- ==========================
-- rack_locations
-- ==========================
CREATE TABLE `rack_locations` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `code` VARCHAR(64) NOT NULL,
  `description` VARCHAR(255),
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_rack_locations_code` (`code`),
  KEY `idx_rack_locations_code` (`code`)
);

-- ==========================
-- medicines
-- ==========================
CREATE TABLE `medicines` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `generic_name` VARCHAR(255),
  `category_id` BIGINT,
  `manufacturer_id` BIGINT,
  `hsn_code` VARCHAR(20),
  `unit` VARCHAR(32) NOT NULL DEFAULT 'strip',
  `packing_details` VARCHAR(128),
  `low_stock_alert` INT NOT NULL DEFAULT 0,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_medicines_name` (`name`),
  KEY `idx_medicines_generic` (`generic_name`),
  KEY `idx_medicines_active` (`is_active`),
  CONSTRAINT `fk_medicines_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_medicines_manufacturer` FOREIGN KEY (`manufacturer_id`) REFERENCES `manufacturers` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
);

-- ==========================
-- medicine_batches
-- ==========================
CREATE TABLE `medicine_batches` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `medicine_id` BIGINT NOT NULL,
  `batch_number` VARCHAR(64) NOT NULL,
  `manufacturing_date` DATE,
  `expiry_date` DATE,
  `rack_location_id` BIGINT,
  `purchase_price` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `mrp` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `selling_price` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `current_stock` INT NOT NULL DEFAULT 0,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_med_batches_med_batch` (`medicine_id`, `batch_number`),
  KEY `idx_med_batches_med_batch` (`medicine_id`, `batch_number`),
  KEY `idx_med_batches_expiry` (`expiry_date`),
  KEY `idx_med_batches_stock` (`current_stock`),
  CONSTRAINT `fk_med_batches_medicine` FOREIGN KEY (`medicine_id`) REFERENCES `medicines` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_med_batches_rack` FOREIGN KEY (`rack_location_id`) REFERENCES `rack_locations` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
);

-- ==========================
-- suppliers
-- ==========================
CREATE TABLE `suppliers` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `company_name` VARCHAR(255),
  `phone` VARCHAR(20),
  `email` VARCHAR(254),
  `address` TEXT,
  `gst_number` VARCHAR(20),
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_suppliers_name` (`name`),
  KEY `idx_suppliers_phone` (`phone`),
  KEY `idx_suppliers_active` (`is_active`)
);

-- ==========================
-- customers
-- ==========================
CREATE TABLE `customers` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `phone` VARCHAR(20),
  `email` VARCHAR(254),
  `address` TEXT,
  `date_of_birth` DATE,
  `notes` TEXT,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_customers_name` (`name`),
  KEY `idx_customers_phone` (`phone`),
  KEY `idx_customers_active` (`is_active`)
);

-- ==========================
-- purchase_invoices
-- ==========================
CREATE TABLE `purchase_invoices` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `invoice_number` VARCHAR(64) NOT NULL,
  `supplier_id` BIGINT NOT NULL,
  `invoice_date` DATE NOT NULL,
  `payment_mode` VARCHAR(16) NOT NULL DEFAULT 'CASH',
  `total_amount` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `amount_paid` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `remarks` TEXT,
  `created_by_id` BIGINT,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_purchase_invoice_number` (`invoice_number`),
  KEY `idx_purchase_invoice_date` (`invoice_date`),
  KEY `idx_purchase_invoice_supplier` (`supplier_id`),
  CONSTRAINT `fk_purchase_supplier` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_purchase_created_by` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
);

-- ==========================
-- purchase_invoice_items
-- ==========================
CREATE TABLE `purchase_invoice_items` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `purchase_invoice_id` BIGINT NOT NULL,
  `medicine_batch_id` BIGINT NOT NULL,
  `quantity` INT NOT NULL DEFAULT 0,
  `purchase_price` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `mrp` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `selling_price` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `line_total` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`id`),
  KEY `idx_pii_purchase_invoice` (`purchase_invoice_id`),
  KEY `idx_pii_med_batch` (`medicine_batch_id`),
  CONSTRAINT `fk_pii_purchase_invoice` FOREIGN KEY (`purchase_invoice_id`) REFERENCES `purchase_invoices` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_pii_med_batch` FOREIGN KEY (`medicine_batch_id`) REFERENCES `medicine_batches` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ==========================
-- sales_invoices
-- ==========================
CREATE TABLE `sales_invoices` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `invoice_number` VARCHAR(64) NOT NULL,
  `invoice_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `customer_id` BIGINT,
  `status` VARCHAR(16) NOT NULL DEFAULT 'COMPLETED',
  `payment_mode` VARCHAR(16) NOT NULL DEFAULT 'CASH',
  `total_amount` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `discount_amount` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `net_amount` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `amount_paid` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `remarks` TEXT,
  `created_by_id` BIGINT,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_sales_invoice_number` (`invoice_number`),
  KEY `idx_sales_invoice_date` (`invoice_date`),
  KEY `idx_sales_invoice_customer` (`customer_id`),
  KEY `idx_sales_invoice_status` (`status`),
  KEY `idx_sales_invoice_payment_mode` (`payment_mode`),
  CONSTRAINT `fk_sales_customer` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_sales_created_by` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
);

-- ==========================
-- sales_invoice_items
-- ==========================
CREATE TABLE `sales_invoice_items` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `sales_invoice_id` BIGINT NOT NULL,
  `medicine_batch_id` BIGINT NOT NULL,
  `quantity` INT NOT NULL DEFAULT 0,
  `mrp` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `selling_price` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `line_total` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`id`),
  KEY `idx_sii_sales_invoice` (`sales_invoice_id`),
  KEY `idx_sii_med_batch` (`medicine_batch_id`),
  CONSTRAINT `fk_sii_sales_invoice` FOREIGN KEY (`sales_invoice_id`) REFERENCES `sales_invoices` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_sii_med_batch` FOREIGN KEY (`medicine_batch_id`) REFERENCES `medicine_batches` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ==========================
-- customer_ledger_entries
-- ==========================
CREATE TABLE `customer_ledger_entries` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `customer_id` BIGINT NOT NULL,
  `sales_invoice_id` BIGINT,
  `entry_type` VARCHAR(16) NOT NULL,
  `amount` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `remarks` TEXT,
  `created_by_id` BIGINT,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_cle_customer` (`customer_id`),
  KEY `idx_cle_entry_type` (`entry_type`),
  KEY `idx_cle_created_at` (`created_at`),
  CONSTRAINT `fk_cle_customer` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cle_sales_invoice` FOREIGN KEY (`sales_invoice_id`) REFERENCES `sales_invoices` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_cle_created_by` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
);

-- ==========================
-- stock_movements
-- ==========================
CREATE TABLE `stock_movements` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `medicine_batch_id` BIGINT NOT NULL,
  `movement_type` VARCHAR(32) NOT NULL,
  `quantity_change` INT NOT NULL,
  `reference_purchase_invoice_id` BIGINT,
  `reference_sales_invoice_id` BIGINT,
  `remarks` TEXT,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_sm_med_batch` (`medicine_batch_id`),
  KEY `idx_sm_movement_type` (`movement_type`),
  KEY `idx_sm_created_at` (`created_at`),
  CONSTRAINT `fk_sm_med_batch` FOREIGN KEY (`medicine_batch_id`) REFERENCES `medicine_batches` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_sm_ref_purchase` FOREIGN KEY (`reference_purchase_invoice_id`) REFERENCES `purchase_invoices` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_sm_ref_sales` FOREIGN KEY (`reference_sales_invoice_id`) REFERENCES `sales_invoices` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
);

-- ==========================
-- expiry_returns
-- ==========================
CREATE TABLE `expiry_returns` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `supplier_id` BIGINT NOT NULL,
  `return_number` VARCHAR(64) NOT NULL,
  `return_date` DATE NOT NULL,
  `total_amount` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `remarks` TEXT,
  `created_by_id` BIGINT,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_expiry_return_number` (`return_number`),
  KEY `idx_expiry_return_date` (`return_date`),
  CONSTRAINT `fk_expiry_supplier` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_expiry_created_by` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
);

-- ==========================
-- expiry_return_items
-- ==========================
CREATE TABLE `expiry_return_items` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `expiry_return_id` BIGINT NOT NULL,
  `medicine_batch_id` BIGINT NOT NULL,
  `quantity` INT NOT NULL DEFAULT 0,
  `rate` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `line_total` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`id`),
  KEY `idx_eri_expiry_return` (`expiry_return_id`),
  KEY `idx_eri_med_batch` (`medicine_batch_id`),
  CONSTRAINT `fk_eri_expiry_return` FOREIGN KEY (`expiry_return_id`) REFERENCES `expiry_returns` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_eri_med_batch` FOREIGN KEY (`medicine_batch_id`) REFERENCES `medicine_batches` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ==========================
-- database_backup_logs
-- ==========================
CREATE TABLE `database_backup_logs` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `backup_file_path` VARCHAR(512) NOT NULL,
  `is_successful` TINYINT(1) NOT NULL DEFAULT 1,
  `message` TEXT,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_db_backup_created_at` (`created_at`),
  KEY `idx_db_backup_success` (`is_successful`)
);

SET FOREIGN_KEY_CHECKS = 1;
