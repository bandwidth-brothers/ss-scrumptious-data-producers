
DROP TABLE IF EXISTS `restaurant_cuisine` ;
DROP TABLE IF EXISTS `menuitem_order` ;
DROP TABLE IF EXISTS `menuitem_category` ;
DROP TABLE IF EXISTS `menuitem_tag` ;
DROP TABLE IF EXISTS `admin` ;
DROP TABLE IF EXISTS `customer_address` ;
DROP TABLE IF EXISTS `payment` ;
DROP TABLE IF EXISTS `tag` ;
DROP TABLE IF EXISTS `order` ;
DROP TABLE IF EXISTS `customer` ;
DROP TABLE IF EXISTS `delivery` ;
DROP TABLE IF EXISTS `driver` ;
DROP TABLE IF EXISTS `category` ;
DROP TABLE IF EXISTS `menuitem` ;
DROP TABLE IF EXISTS `cuisine` ;
DROP TABLE IF EXISTS `restaurant` ;
DROP TABLE IF EXISTS `owner` ;
DROP TABLE IF EXISTS `address` ;
DROP TABLE IF EXISTS `user` ;


CREATE TABLE IF NOT EXISTS `user` (
  `id` BINARY(16) NOT NULL,
  `user_role` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `enabled` TINYINT NOT NULL,
  `confirmed` TINYINT NOT NULL,
  `account_non_expired` TINYINT NOT NULL,
  `account_non_locked` TINYINT NOT NULL,
  `credentials_non_expired` TINYINT NOT NULL,
  UNIQUE INDEX `email_UNIQUE` (`email` ASC),
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `address` (
  `id` BIGINT(8) NOT NULL AUTO_INCREMENT,
  `line1` VARCHAR(255) NOT NULL,
  `line2` VARCHAR(255) NULL,
  `city` VARCHAR(255) NOT NULL,
  `state` CHAR(2) NOT NULL,
  `zip` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `addressId_UNIQUE` (`id` ASC))
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `owner` (
  `id` BINARY(16) NOT NULL,
  `first_name` VARCHAR(255) NULL,
  `last_name` VARCHAR(255) NULL,
  `phone` VARCHAR(255) NULL,
  `email` VARCHAR(255) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `customerId_UNIQUE` (`id` ASC),
  CONSTRAINT `fk_customer_user10`
    FOREIGN KEY (`id`)
    REFERENCES `user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `restaurant` (
  `id` BIGINT(8) NOT NULL AUTO_INCREMENT,
  `address_id` BIGINT(8) NOT NULL,
  `owner_id` BINARY(16) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `rating` FLOAT NOT NULL DEFAULT 0,
  `price_category` VARCHAR(3) NULL,
  `phone` VARCHAR(255) NULL,
  `is_active` TINYINT NULL,
  `picture` VARCHAR(255) NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_restaurant_address1_idx` (`address_id` ASC),
  UNIQUE INDEX `restaurantId_UNIQUE` (`id` ASC),
  INDEX `fk_restaurant_restaurant_owner1_idx` (`owner_id` ASC),
  CONSTRAINT `fk_restaurant_address1`
    FOREIGN KEY (`address_id`)
    REFERENCES `address` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_restaurant_restaurant_owner1`
    FOREIGN KEY (`owner_id`)
    REFERENCES `owner` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `cuisine` (
  `id` BIGINT(8) NOT NULL AUTO_INCREMENT,
  `type` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `cuisineId_UNIQUE` (`id` ASC))
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `menuitem` (
  `id` BIGINT(8) NOT NULL AUTO_INCREMENT,
  `restaurant_id` BIGINT(8) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `price` FLOAT NOT NULL,
  `picture` VARCHAR(255) NULL,
  `description` VARCHAR(255) NULL,
  `is_available` TINYINT NOT NULL DEFAULT 0,
  `size` VARCHAR(255) NULL,
  `discount` FLOAT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_food_restaurant1_idx` (`restaurant_id` ASC),
  UNIQUE INDEX `consumableItemId_UNIQUE` (`id` ASC),
  CONSTRAINT `fk_food_restaurant1`
    FOREIGN KEY (`restaurant_id`)
    REFERENCES `restaurant` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `category` (
  `id` BIGINT(8) NOT NULL AUTO_INCREMENT,
  `type` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `categoryId_UNIQUE` (`id` ASC))
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `driver` (
  `id` BINARY(16) NOT NULL,
  `address_id` BIGINT(8) NOT NULL,
  `first_name` VARCHAR(255) NOT NULL,
  `last_name` VARCHAR(255) NOT NULL,
  `phone` VARCHAR(255) NOT NULL,
  `dob` VARCHAR(255) NULL,
  `license_num` VARCHAR(255) NOT NULL,
  `rating` FLOAT NULL,
  `picture` VARCHAR(255) NULL,
  `status` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_driver_address1_idx` (`address_id` ASC),
  UNIQUE INDEX `driverId_UNIQUE` (`id` ASC),
  INDEX `fk_driver_user1_idx` (`id` ASC),
  CONSTRAINT `fk_driver_address1`
    FOREIGN KEY (`address_id`)
    REFERENCES `address` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_driver_user1`
    FOREIGN KEY (`id`)
    REFERENCES `user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `delivery` (
  `id` BIGINT(8) NOT NULL AUTO_INCREMENT,
  `address_id` BIGINT(8) NOT NULL,
  `driver_id` BINARY(16) NOT NULL,
  `estimated_delivery_time` TIMESTAMP NULL,
  `delivery_status` VARCHAR(255) NULL,
  `actual_delivery_time` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_delivery_address1_idx` (`address_id` ASC),
  INDEX `fk_delivery_driver1_idx` (`driver_id` ASC),
  UNIQUE INDEX `deliveryId_UNIQUE` (`id` ASC),
  CONSTRAINT `fk_delivery_address1`
    FOREIGN KEY (`address_id`)
    REFERENCES `address` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_delivery_driver1`
    FOREIGN KEY (`driver_id`)
    REFERENCES `driver` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `customer` (
  `id` BINARY(16) NOT NULL,
  `first_name` VARCHAR(255) NOT NULL,
  `last_name` VARCHAR(255) NOT NULL,
  `phone` VARCHAR(255) NOT NULL,
  `dob` DATE NULL,
  `loyalty_points` INT NOT NULL DEFAULT 0,
  `picture` VARCHAR(255) NULL,
  `veteranary_status` TINYINT NULL,
  `email` VARCHAR(255) NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_customer_user1_idx` (`id` ASC),
  CONSTRAINT `fk_customer_user1`
    FOREIGN KEY (`id`)
    REFERENCES `user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `order` (
  `id` BIGINT(8) NOT NULL AUTO_INCREMENT,
  `customer_id` BINARY(16) NOT NULL,
  `restaurant_id` BIGINT(8) NOT NULL,
  `delivery_id` BIGINT(8) NOT NULL,
  `confirmation_code` VARCHAR(255) NULL,
  `requested_delivery_time` TIMESTAMP NULL,
  `order_discount` FLOAT NULL,
  `submited_at` TIMESTAMP NULL,
  `preparation_status` VARCHAR(255) NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_order_delivery1_idx` (`delivery_id` ASC),
  UNIQUE INDEX `orderId_UNIQUE` (`id` ASC),
  INDEX `fk_order_customer1_idx` (`customer_id` ASC),
  INDEX `fk_order_restaurant1_idx` (`restaurant_id` ASC),
  CONSTRAINT `fk_order_delivery1`
    FOREIGN KEY (`delivery_id`)
    REFERENCES `delivery` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_order_customer1`
    FOREIGN KEY (`customer_id`)
    REFERENCES `customer` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_order_restaurant1`
    FOREIGN KEY (`restaurant_id`)
    REFERENCES `restaurant` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tag` (
  `id` BIGINT(8) NOT NULL AUTO_INCREMENT,
  `type` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `tagId_UNIQUE` (`id` ASC))
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `payment` (
  `id` BIGINT(8) NOT NULL AUTO_INCREMENT,
  `customer_id` BINARY(16) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `stripe_id` VARCHAR(255) NULL,
  `refunded` TINYINT NULL,
  `payment_status` VARCHAR(255) NULL,
  INDEX `fk_payment_customer1_idx` (`customer_id` ASC),
  PRIMARY KEY (`id`),
  UNIQUE INDEX `paymentId_UNIQUE` (`id` ASC),
  CONSTRAINT `fk_payment_customer1`
    FOREIGN KEY (`customer_id`)
    REFERENCES `customer` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `customer_address` (
  `customer_id` BINARY(16) NOT NULL,
  `address_id` BIGINT(8) NOT NULL,
  PRIMARY KEY (`customer_id`, `address_id`),
  INDEX `fk_customer_has_address_address1_idx` (`address_id` ASC),
  INDEX `fk_customer_has_address_customer1_idx` (`customer_id` ASC),
  CONSTRAINT `fk_customer_has_address_customer1`
    FOREIGN KEY (`customer_id`)
    REFERENCES `customer` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_customer_has_address_address1`
    FOREIGN KEY (`address_id`)
    REFERENCES `address` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `admin` (
  `id` BINARY(16) NOT NULL,
  `first_name` VARCHAR(255) NULL,
  `last_name` VARCHAR(255) NULL,
  `phone` VARCHAR(255) NULL,
  `email` VARCHAR(255) NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_customer_user100`
    FOREIGN KEY (`id`)
    REFERENCES `user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `menuitem_tag` (
  `menuitem_id` BIGINT(8) NOT NULL,
  `tag_id` BIGINT(8) NOT NULL,
  PRIMARY KEY (`menuitem_id`, `tag_id`),
  INDEX `fk_menuitem_has_tag_tag1_idx` (`tag_id` ASC),
  INDEX `fk_menuitem_has_tag_menuitem1_idx` (`menuitem_id` ASC),
  CONSTRAINT `fk_menuitem_has_tag_menuitem1`
    FOREIGN KEY (`menuitem_id`)
    REFERENCES `menuitem` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_menuitem_has_tag_tag1`
    FOREIGN KEY (`tag_id`)
    REFERENCES `tag` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `menuitem_category` (
  `menuitem_id` BIGINT(8) NOT NULL,
  `category_id` BIGINT(8) NOT NULL,
  PRIMARY KEY (`menuitem_id`, `category_id`),
  INDEX `fk_menuitem_has_category_category1_idx` (`category_id` ASC),
  INDEX `fk_menuitem_has_category_menuitem1_idx` (`menuitem_id` ASC),
  CONSTRAINT `fk_menuitem_has_category_menuitem1`
    FOREIGN KEY (`menuitem_id`)
    REFERENCES `menuitem` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_menuitem_has_category_category1`
    FOREIGN KEY (`category_id`)
    REFERENCES `category` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `menuitem_order` (
  `menuitem_id` BIGINT(8) NOT NULL,
  `order_id` BIGINT(8) NOT NULL,
  `quantity` BIGINT(8) NOT NULL DEFAULT 1,
  PRIMARY KEY (`menuitem_id`, `order_id`),
  INDEX `fk_menuitem_has_order_order1_idx` (`order_id` ASC),
  INDEX `fk_menuitem_has_order_menuitem1_idx` (`menuitem_id` ASC),
  CONSTRAINT `fk_menuitem_has_order_menuitem1`
    FOREIGN KEY (`menuitem_id`)
    REFERENCES `menuitem` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_menuitem_has_order_order1`
    FOREIGN KEY (`order_id`)
    REFERENCES `order` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `restaurant_cuisine` (
  `restaurant_id` BIGINT(8) NOT NULL,
  `cuisine_id` BIGINT(8) NOT NULL,
  PRIMARY KEY (`restaurant_id`, `cuisine_id`),
  INDEX `fk_restaurant_has_cuisine_cuisine1_idx` (`cuisine_id` ASC),
  INDEX `fk_restaurant_has_cuisine_restaurant1_idx` (`restaurant_id` ASC),
  CONSTRAINT `fk_restaurant_has_cuisine_restaurant1`
    FOREIGN KEY (`restaurant_id`)
    REFERENCES `restaurant` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_restaurant_has_cuisine_cuisine1`
    FOREIGN KEY (`cuisine_id`)
    REFERENCES `cuisine` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;