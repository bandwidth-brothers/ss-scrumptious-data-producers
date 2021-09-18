-- MySQL Workbench Forward Engineering
\
-- -----------------------------------------------------
-- Schema scrumptious
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema scrumptious
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Table `scrumptious`.`user`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `user` ;

CREATE TABLE IF NOT EXISTS `user` (
  `userId` BINARY(16) NOT NULL,
  `userRole` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `createdAt` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updatedAt` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE INDEX `email_UNIQUE` (`email` ASC),
  PRIMARY KEY (`userId`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`address`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `address` ;

CREATE TABLE IF NOT EXISTS `address` (
  `addressId` BIGINT(8) NOT NULL AUTO_INCREMENT,
  `line1` VARCHAR(255) NOT NULL,
  `line2` VARCHAR(255) NULL,
  `city` VARCHAR(255) NOT NULL,
  `state` CHAR(2) NOT NULL,
  `zip` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`addressId`),
  UNIQUE INDEX `addressId_UNIQUE` (`addressId` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`restaurant_owner`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `restaurant_owner` ;

CREATE TABLE IF NOT EXISTS `restaurant_owner` (
  `restaurantOwnerId` BINARY(16) NOT NULL,
  `firstName` VARCHAR(255) NULL,
  `lastName` VARCHAR(255) NULL,
  `phone` VARCHAR(255) NULL,
  PRIMARY KEY (`restaurantOwnerId`),
  UNIQUE INDEX `customerId_UNIQUE` (`restaurantOwnerId` ASC),
  CONSTRAINT `fk_customer_user10`
    FOREIGN KEY (`restaurantOwnerId`)
    REFERENCES `user` (`userId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`restaurant`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `restaurant` ;

CREATE TABLE IF NOT EXISTS `restaurant` (
  `restaurantId` BIGINT(8) NOT NULL AUTO_INCREMENT,
  `addressId` BIGINT(8) NOT NULL,
  `restaurantOwnerId` BINARY(16) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `rating` FLOAT NOT NULL DEFAULT 0,
  `priceCategory` VARCHAR(3) NULL,
  `phone` VARCHAR(255) NULL,
  `isActive` TINYINT NULL,
  `restaurantLogo` VARCHAR(255) NULL,
  PRIMARY KEY (`restaurantId`, `addressId`),
  INDEX `fk_restaurant_address1_idx` (`addressId` ASC),
  UNIQUE INDEX `restaurantId_UNIQUE` (`restaurantId` ASC),
  INDEX `fk_restaurant_restaurant_owner1_idx` (`restaurantOwnerId` ASC),
  CONSTRAINT `fk_restaurant_address1`
    FOREIGN KEY (`addressId`)
    REFERENCES `address` (`addressId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_restaurant_restaurant_owner1`
    FOREIGN KEY (`restaurantOwnerId`)
    REFERENCES `restaurant_owner` (`restaurantOwnerId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`category`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `category` ;

CREATE TABLE IF NOT EXISTS `category` (
  `categoryId` BIGINT(8) NOT NULL AUTO_INCREMENT,
  `type` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`categoryId`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`restaurant_category`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `restaurant_category` ;

CREATE TABLE IF NOT EXISTS `restaurant_category` (
  `restaurantId` BIGINT(8) NOT NULL,
  `categoryId` BIGINT(8) NOT NULL,
  INDEX `fk_restaurant_category_restaurant1_idx` (`restaurantId` ASC),
  INDEX `fk_restaurant_category_category1_idx` (`categoryId` ASC),
  PRIMARY KEY (`restaurantId`, `categoryId`),
  CONSTRAINT `fk_restaurant_category_restaurant1`
    FOREIGN KEY (`restaurantId`)
    REFERENCES `restaurant` (`restaurantId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_restaurant_category_category1`
    FOREIGN KEY (`categoryId`)
    REFERENCES `category` (`categoryId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`menuItem`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `menuItem` ;

CREATE TABLE IF NOT EXISTS `menuItem` (
  `restaurantId` BIGINT(8) NOT NULL,
  `menuItemId` BIGINT(8) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `price` FLOAT NOT NULL,
  `itemPicture` VARCHAR(255) NULL,
  `description` VARCHAR(255) NULL,
  `isAvailable` TINYINT NOT NULL DEFAULT 0,
  `size` VARCHAR(255) NULL,
  `itemDiscount` FLOAT NULL,
  PRIMARY KEY (`menuItemId`),
  INDEX `fk_food_restaurant1_idx` (`restaurantId` ASC),
  UNIQUE INDEX `consumableItemId_UNIQUE` (`menuItemId` ASC),
  CONSTRAINT `fk_food_restaurant1`
    FOREIGN KEY (`restaurantId`)
    REFERENCES `restaurant` (`restaurantId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`menu_category`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `menu_category` ;

CREATE TABLE IF NOT EXISTS `menu_category` (
  `categoryId` BIGINT(8) NOT NULL AUTO_INCREMENT,
  `type` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`categoryId`),
  UNIQUE INDEX `categoryId_UNIQUE` (`categoryId` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`category_menuItem`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `category_menuItem` ;

CREATE TABLE IF NOT EXISTS `category_menuItem` (
  `categoryId` BIGINT(8) NOT NULL,
  `menuItemId` BIGINT(8) NOT NULL,
  INDEX `fk_food_category_food1_idx` (`menuItemId` ASC),
  PRIMARY KEY (`categoryId`, `menuItemId`),
  INDEX `fk_food_category_menu_category1_idx` (`categoryId` ASC),
  CONSTRAINT `fk_food_category_food1`
    FOREIGN KEY (`menuItemId`)
    REFERENCES `menuItem` (`menuItemId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_food_category_menu_category1`
    FOREIGN KEY (`categoryId`)
    REFERENCES `menu_category` (`categoryId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`driver`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `driver` ;

CREATE TABLE IF NOT EXISTS `driver` (
  `driverId` BINARY(16) NOT NULL,
  `addressId` BIGINT(8) NOT NULL,
  `firstName` VARCHAR(255) NOT NULL,
  `lastName` VARCHAR(255) NOT NULL,
  `phone` VARCHAR(255) NOT NULL,
  `dob` VARCHAR(255) NULL,
  `licenseNum` VARCHAR(255) NOT NULL,
  `rating` FLOAT NULL,
  `picture` VARCHAR(255) NULL,
  `status` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`driverId`),
  INDEX `fk_driver_address1_idx` (`addressId` ASC),
  UNIQUE INDEX `driverId_UNIQUE` (`driverId` ASC),
  INDEX `fk_driver_user1_idx` (`driverId` ASC),
  CONSTRAINT `fk_driver_address1`
    FOREIGN KEY (`addressId`)
    REFERENCES `address` (`addressId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_driver_user1`
    FOREIGN KEY (`driverId`)
    REFERENCES `user` (`userId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`delivery`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `delivery` ;

CREATE TABLE IF NOT EXISTS `delivery` (
  `deliveryId` BIGINT(8) NOT NULL AUTO_INCREMENT,
  `destinationId` BIGINT(8) NOT NULL,
  `driverId` BINARY(16) NOT NULL,
  `estimatedDeliveryTime` TIMESTAMP NULL,
  `deliveryStatus` VARCHAR(255) NULL,
  `actualDeliveryTime` TIMESTAMP NULL,
  PRIMARY KEY (`deliveryId`),
  INDEX `fk_delivery_address1_idx` (`destinationId` ASC),
  INDEX `fk_delivery_driver1_idx` (`driverId` ASC),
  UNIQUE INDEX `deliveryId_UNIQUE` (`deliveryId` ASC),
  CONSTRAINT `fk_delivery_address1`
    FOREIGN KEY (`destinationId`)
    REFERENCES `address` (`addressId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_delivery_driver1`
    FOREIGN KEY (`driverId`)
    REFERENCES `driver` (`driverId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`customer`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `customer` ;

CREATE TABLE IF NOT EXISTS `customer` (
  `customerId` BINARY(16) NOT NULL,
  `firstName` VARCHAR(255) NOT NULL,
  `lastName` VARCHAR(255) NOT NULL,
  `phone` VARCHAR(255) NOT NULL,
  `dob` DATE NULL,
  `loyaltyPoints` INT NOT NULL DEFAULT 0,
  `picture` VARCHAR(255) NULL,
  `veteranaryStatus` TINYINT NULL,
  PRIMARY KEY (`customerId`),
  INDEX `fk_customer_user1_idx` (`customerId` ASC),
  UNIQUE INDEX `userId_UNIQUE` (`customerId` ASC),
  CONSTRAINT `fk_customer_user1`
    FOREIGN KEY (`customerId`)
    REFERENCES `user` (`userId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`order`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `order` ;

CREATE TABLE IF NOT EXISTS `order` (
  `orderId` BIGINT(8) NOT NULL AUTO_INCREMENT,
  `customerId` BINARY(16) NOT NULL,
  `deliveryId` BIGINT(8) NOT NULL,
  `restaurantId` BIGINT(8) NOT NULL,
  `restaurantAddressId` BIGINT(8) NOT NULL,
  `confirmationCode` VARCHAR(255) NULL,
  `requestedDeliveryTime` TIMESTAMP NULL,
  `orderDiscount` FLOAT NULL,
  `submitedAt` TIMESTAMP NULL,
  PRIMARY KEY (`orderId`),
  INDEX `fk_order_delivery1_idx` (`deliveryId` ASC),
  INDEX `fk_order_customer1_idx` (`customerId` ASC),
  INDEX `fk_order_restaurant1_idx` (`restaurantId` ASC, `restaurantAddressId` ASC),
  CONSTRAINT `fk_order_delivery1`
    FOREIGN KEY (`deliveryId`)
    REFERENCES `delivery` (`deliveryId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_order_customer1`
    FOREIGN KEY (`customerId`)
    REFERENCES `customer` (`customerId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_order_restaurant1`
    FOREIGN KEY (`restaurantId` , `restaurantAddressId`)
    REFERENCES `restaurant` (`restaurantId` , `addressId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`menuItem_order`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `menuItem_order` ;

CREATE TABLE IF NOT EXISTS `menuItem_order` (
  `menuItemId` BIGINT(8) NOT NULL,
  `orderId` BIGINT(8) NOT NULL,
  `quantity` BIGINT(8) NOT NULL DEFAULT 1,
  PRIMARY KEY (`menuItemId`, `orderId`),
  INDEX `fk_consumableItem_has_order_order1_idx` (`orderId` ASC),
  INDEX `fk_consumableItem_has_order_consumableItem1_idx` (`menuItemId` ASC),
  CONSTRAINT `fk_consumableItem_has_order_consumableItem1`
    FOREIGN KEY (`menuItemId`)
    REFERENCES `menuItem` (`menuItemId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_consumableItem_has_order_order1`
    FOREIGN KEY (`orderId`)
    REFERENCES `order` (`orderId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`order_restaurant`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `order_restaurant` ;

CREATE TABLE IF NOT EXISTS `order_restaurant` (
  `orderId` BIGINT(8) NOT NULL,
  `restaurantId` BIGINT(8) NOT NULL,
  `preparationStatus` VARCHAR(255) NULL,
  PRIMARY KEY (`orderId`, `restaurantId`),
  INDEX `fk_order_has_restaurant_restaurant1_idx` (`restaurantId` ASC),
  INDEX `fk_order_has_restaurant_order1_idx` (`orderId` ASC),
  CONSTRAINT `fk_order_has_restaurant_order1`
    FOREIGN KEY (`orderId`)
    REFERENCES `order` (`orderId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_order_has_restaurant_restaurant1`
    FOREIGN KEY (`restaurantId`)
    REFERENCES `restaurant` (`restaurantId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`tag`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `tag` ;

CREATE TABLE IF NOT EXISTS `tag` (
  `tagId` BIGINT(8) NOT NULL AUTO_INCREMENT,
  `tagType` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`tagId`),
  UNIQUE INDEX `tagId_UNIQUE` (`tagId` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`tag_menuItem`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `tag_menuItem` ;

CREATE TABLE IF NOT EXISTS `tag_menuItem` (
  `tagId` BIGINT(8) NOT NULL,
  `menuItemId` BIGINT(8) NOT NULL,
  PRIMARY KEY (`tagId`, `menuItemId`),
  INDEX `fk_tag_has_consumableItem_consumableItem1_idx` (`menuItemId` ASC),
  INDEX `fk_tag_has_consumableItem_tag1_idx` (`tagId` ASC),
  CONSTRAINT `fk_tag_has_consumableItem_tag1`
    FOREIGN KEY (`tagId`)
    REFERENCES `tag` (`tagId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_tag_has_consumableItem_consumableItem1`
    FOREIGN KEY (`menuItemId`)
    REFERENCES `menuItem` (`menuItemId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`orderPayment`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `orderPayment` ;

CREATE TABLE IF NOT EXISTS `orderPayment` (
  `orderId` BIGINT(8) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `stripeId` VARCHAR(255) NULL,
  `refunded` TINYINT NULL,
  `paymentStatus` VARCHAR(255) NULL,
  INDEX `fk_orderPayment_order1_idx` (`orderId` ASC),
  PRIMARY KEY (`orderId`),
  CONSTRAINT `fk_orderPayment_order1`
    FOREIGN KEY (`orderId`)
    REFERENCES `order` (`orderId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`customer_address`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `customer_address` ;

CREATE TABLE IF NOT EXISTS `customer_address` (
  `customerId` BINARY(16) NOT NULL,
  `addressId` BIGINT(8) NOT NULL,
  PRIMARY KEY (`customerId`, `addressId`),
  INDEX `fk_customer_has_address_address1_idx` (`addressId` ASC),
  INDEX `fk_customer_has_address_customer1_idx` (`customerId` ASC),
  CONSTRAINT `fk_customer_has_address_customer1`
    FOREIGN KEY (`customerId`)
    REFERENCES `customer` (`customerId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_customer_has_address_address1`
    FOREIGN KEY (`addressId`)
    REFERENCES `address` (`addressId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;
