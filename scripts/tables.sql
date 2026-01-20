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

CREATE TABLE `medicine_inventory` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

  `name` VARCHAR(255) NOT NULL,
  `medicine_uses` TEXT NULL,
  `hsn_code` VARCHAR(20) NULL,

  `unit` VARCHAR(32) NOT NULL DEFAULT 'strip',
  `packing_details` VARCHAR(128) NULL,
  `low_stock_alert` INT NOT NULL DEFAULT 0,

  `batch_number` VARCHAR(128) NOT NULL,
  `manufacturing_date` DATE NULL,
  `expiry_date` DATE NULL,

  `rack_location` VARCHAR(64) NULL,

  `purchase_price` DECIMAL(10,2) NOT NULL,
  `mrp` DECIMAL(10,2) NOT NULL,

  `current_stock` INT NOT NULL DEFAULT 0,

  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `is_expired` BOOLEAN NOT NULL DEFAULT FALSE,

  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),

  KEY `idx_med_inv_name` (`name`),
  KEY `idx_med_inv_name_batch` (`name`, `batch_number`),
  KEY `idx_med_inv_expiry` (`expiry_date`),
  KEY `idx_med_inv_stock` (`current_stock`),
  KEY `idx_med_inv_active` (`is_active`),
  KEY `idx_med_inv_active_expiry` (`is_active`, `expiry_date`),
  KEY `idx_med_inv_active_stock` (`is_active`, `current_stock`),
  KEY `idx_med_inv_rack` (`rack_location`),
  KEY `idx_med_expiry` (`expiry_date`),
  KEY `idx_med_created_at` (`created_at`)
);

CREATE TABLE `suppliers` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

  `name` VARCHAR(255) NOT NULL,
  `company_name` VARCHAR(255) NULL,
  `phone` VARCHAR(20) NULL,
  `email` VARCHAR(254) NULL,
  `address` TEXT NULL,
  `gst_number` VARCHAR(20) NULL,

  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,

  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),

  KEY `idx_supplier_name` (`name`),
  KEY `idx_supplier_phone` (`phone`),
  KEY `idx_supplier_active` (`is_active`),
  KEY `idx_supplier_created_at` (`created_at`)
);

CREATE TABLE `purchase_invoices` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

  `supplier_id` BIGINT NOT NULL,
  `invoice_number` VARCHAR(64) NOT NULL,
  `invoice_date` DATE NOT NULL,

  `payment_mode` VARCHAR(16) NOT NULL DEFAULT 'Cash',

  `total_amount` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `amount_paid` DECIMAL(12,2) NOT NULL DEFAULT 0.00,

  `remarks` TEXT NULL,

  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),

  KEY `idx_purchase_invoice_supplier` (`supplier_id`),
  KEY `idx_purchase_invoice_number` (`invoice_number`),
  KEY `idx_purchase_invoice_date` (`invoice_date`)
);

CREATE TABLE `purchase_invoice_items` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

  `purchase_invoice_id` BIGINT NOT NULL,
  `medicine_id` BIGINT NOT NULL,

  `quantity` INT NOT NULL,

  `purchase_price` DECIMAL(10,2) NULL,
  `mrp` DECIMAL(10,2) NULL,

  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),

  KEY `idx_pi_item_pi` (`purchase_invoice_id`),
  KEY `idx_pi_item_med` (`medicine_id`)
);

CREATE TABLE `sales_invoices` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

  `invoice_id` VARCHAR(64) NOT NULL,
  `invoice_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  `payment_mode` VARCHAR(16) NOT NULL,
  `customer_name` VARCHAR(255) NULL,
  `doctor_name` VARCHAR(255) NULL,

  `total_medicines` INT NOT NULL DEFAULT 0,
  `total_price` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `total_discount_price` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `final_selling_price` DECIMAL(12,2) NOT NULL DEFAULT 0.00,

  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),

  UNIQUE KEY `uq_si_invoice_id` (`invoice_id`),

  KEY `idx_si_id` (`invoice_id`),
  KEY `idx_si_date` (`invoice_date`),
  KEY `idx_si_id_date` (`invoice_id`, `invoice_date`)
);

CREATE TABLE `sales_invoice_items` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

  `sales_invoice_id` BIGINT NOT NULL,
  `medicine_id` BIGINT NOT NULL,

  `quantity` INT NOT NULL DEFAULT 1,

  `mrp` DECIMAL(10,2) NOT NULL,
  `discount` INT NOT NULL DEFAULT 10,
  `discount_price` DECIMAL(10,2) NOT NULL,
  `selling_price` DECIMAL(10,2) NOT NULL,

  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),

  KEY `idx_sii_si` (`sales_invoice_id`),
  KEY `idx_sii_med` (`medicine_id`)
);

CREATE TABLE `expiry_returns` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

  `supplier_id` BIGINT NOT NULL,

  `return_number` VARCHAR(64) NOT NULL,
  `return_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  `total_amount` DECIMAL(12,2) NOT NULL DEFAULT 0.00,

  `remarks` TEXT NULL,

  `is_returned` BOOLEAN NOT NULL DEFAULT FALSE,

  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),

  UNIQUE KEY `uk_er_return_number` (`return_number`),

  KEY `idx_er_supplier` (`supplier_id`),
  KEY `idx_er_number` (`return_number`),
  KEY `idx_er_returned` (`is_returned`)
);

CREATE TABLE `expiry_return_items` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

  `expiry_return_id` BIGINT NOT NULL,
  `medicine_id` BIGINT NOT NULL,

  `batch_number` VARCHAR(128) NULL,

  `quantity` INT NOT NULL,

  `rate` DECIMAL(10,2) NOT NULL,

  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),

  KEY `idx_er_item_er` (`expiry_return_id`),
  KEY `idx_er_item_med` (`medicine_id`)
);
