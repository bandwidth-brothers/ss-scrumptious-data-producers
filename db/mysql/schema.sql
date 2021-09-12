-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema scrumptious
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema scrumptious
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `scrumptious` DEFAULT CHARACTER SET utf8 ;
USE `scrumptious` ;

-- -----------------------------------------------------
-- Table `scrumptious`.`user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`user` (
  `userId` BINARY(16) NOT NULL,
  `userRole` VARCHAR(255) NOT NULL,
  `username` VARCHAR(16) NOT NULL,
  `password` VARCHAR(32) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `profilePic` VARCHAR(255) NULL,
  `createdAt` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updatedAt` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE INDEX `username_UNIQUE` (`username` ASC),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC),
  PRIMARY KEY (`userId`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`address`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`address` (
  `addressId` BINARY(16) NOT NULL,
  `line1` VARCHAR(255) NOT NULL,
  `line2` VARCHAR(45) NULL,
  `city` VARCHAR(45) NOT NULL,
  `state` VARCHAR(45) NOT NULL,
  `zip` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`addressId`),
  UNIQUE INDEX `addressId_UNIQUE` (`addressId` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`restaurant_owner`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`restaurant_owner` (
  `restaurantOwnerId` BINARY(16) NOT NULL,
  `userId` BINARY(16) NOT NULL,
  `firstName` VARCHAR(45) NULL,
  `lastName` VARCHAR(45) NULL,
  `phone` VARCHAR(45) NULL,
  `email` VARCHAR(45) NULL,
  PRIMARY KEY (`restaurantOwnerId`),
  UNIQUE INDEX `customerId_UNIQUE` (`restaurantOwnerId` ASC),
  INDEX `fk_customer_user1_idx` (`userId` ASC),
  CONSTRAINT `fk_customer_user10`
    FOREIGN KEY (`userId`)
    REFERENCES `scrumptious`.`user` (`userId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`restaurant`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`restaurant` (
  `restaurantId` BINARY(16) NOT NULL,
  `addressId` BINARY(16) NOT NULL,
  `restaurantOwnerId` BINARY(16) NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `rating` FLOAT NOT NULL DEFAULT 0,
  `priceCategory` INT NULL,
  `phone` VARCHAR(45) NULL,
  `isActive` TINYINT NULL,
  `restaurantLogo` VARCHAR(255) NULL,
  PRIMARY KEY (`restaurantId`, `addressId`),
  INDEX `fk_restaurant_address1_idx` (`addressId` ASC),
  UNIQUE INDEX `restaurantId_UNIQUE` (`restaurantId` ASC),
  INDEX `fk_restaurant_restaurant_owner1_idx` (`restaurantOwnerId` ASC),
  CONSTRAINT `fk_restaurant_address1`
    FOREIGN KEY (`addressId`)
    REFERENCES `scrumptious`.`address` (`addressId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_restaurant_restaurant_owner1`
    FOREIGN KEY (`restaurantOwnerId`)
    REFERENCES `scrumptious`.`restaurant_owner` (`restaurantOwnerId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`category`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`category` (
  `categoryId` BINARY(16) NOT NULL,
  `type` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`categoryId`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`restaurant_category`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`restaurant_category` (
  `restaurantId` BINARY(16) NOT NULL,
  `categoryId` BINARY(16) NOT NULL,
  INDEX `fk_restaurant_category_restaurant1_idx` (`restaurantId` ASC),
  INDEX `fk_restaurant_category_category1_idx` (`categoryId` ASC),
  PRIMARY KEY (`restaurantId`, `categoryId`),
  CONSTRAINT `fk_restaurant_category_restaurant1`
    FOREIGN KEY (`restaurantId`)
    REFERENCES `scrumptious`.`restaurant` (`restaurantId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_restaurant_category_category1`
    FOREIGN KEY (`categoryId`)
    REFERENCES `scrumptious`.`category` (`categoryId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`menuItem`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`menuItem` (
  `menuItemId` BINARY(16) NOT NULL,
  `restaurantId` BINARY(16) NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `rating` FLOAT NOT NULL DEFAULT 0,
  `price` FLOAT NOT NULL,
  `itemPicture` VARCHAR(255) NULL,
  `description` VARCHAR(255) NULL,
  `isAvailable` TINYINT NOT NULL DEFAULT 0,
  `tag` VARCHAR(45) NULL,
  `size` VARCHAR(45) NULL,
  PRIMARY KEY (`menuItemId`),
  INDEX `fk_food_restaurant1_idx` (`restaurantId` ASC),
  UNIQUE INDEX `consumableItemId_UNIQUE` (`menuItemId` ASC),
  CONSTRAINT `fk_food_restaurant1`
    FOREIGN KEY (`restaurantId`)
    REFERENCES `scrumptious`.`restaurant` (`restaurantId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`menu_category`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`menu_category` (
  `categoryId` BINARY(16) NOT NULL,
  `type` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`categoryId`),
  UNIQUE INDEX `categoryId_UNIQUE` (`categoryId` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`category_menuItem`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`category_menuItem` (
  `categoryId` BINARY(16) NOT NULL,
  `menuItemId` BINARY(16) NOT NULL,
  INDEX `fk_food_category_food1_idx` (`menuItemId` ASC),
  PRIMARY KEY (`categoryId`, `menuItemId`),
  INDEX `fk_food_category_menu_category1_idx` (`categoryId` ASC),
  CONSTRAINT `fk_food_category_food1`
    FOREIGN KEY (`menuItemId`)
    REFERENCES `scrumptious`.`menuItem` (`menuItemId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_food_category_menu_category1`
    FOREIGN KEY (`categoryId`)
    REFERENCES `scrumptious`.`menu_category` (`categoryId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`driver`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`driver` (
  `driverId` BINARY(16) NOT NULL,
  `userId` BINARY(16) NOT NULL,
  `locationId` BINARY(16) NOT NULL,
  `firstName` VARCHAR(45) NULL,
  `lastName` VARCHAR(45) NULL,
  `phone` VARCHAR(45) NULL,
  `email` VARCHAR(45) NULL,
  `dob` VARCHAR(45) NULL,
  `licenseNum` VARCHAR(45) NULL,
  `rating` FLOAT NULL,
  PRIMARY KEY (`driverId`),
  INDEX `fk_driver_address1_idx` (`locationId` ASC),
  UNIQUE INDEX `driverId_UNIQUE` (`driverId` ASC),
  INDEX `fk_driver_user1_idx` (`userId` ASC),
  CONSTRAINT `fk_driver_address1`
    FOREIGN KEY (`locationId`)
    REFERENCES `scrumptious`.`address` (`addressId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_driver_user1`
    FOREIGN KEY (`userId`)
    REFERENCES `scrumptious`.`user` (`userId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`delivery`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`delivery` (
  `deliveryId` BINARY(16) NOT NULL,
  `destinationId` BINARY(16) NOT NULL,
  `driverId` BINARY(16) NOT NULL,
  `estimatedDel` TIMESTAMP NULL,
  PRIMARY KEY (`deliveryId`),
  INDEX `fk_delivery_address1_idx` (`destinationId` ASC),
  INDEX `fk_delivery_driver1_idx` (`driverId` ASC),
  UNIQUE INDEX `deliveryId_UNIQUE` (`deliveryId` ASC),
  CONSTRAINT `fk_delivery_address1`
    FOREIGN KEY (`destinationId`)
    REFERENCES `scrumptious`.`address` (`addressId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_delivery_driver1`
    FOREIGN KEY (`driverId`)
    REFERENCES `scrumptious`.`driver` (`driverId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`customer`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`customer` (
  `customerId` BINARY(16) NOT NULL,
  `userId` BINARY(16) NOT NULL,
  `firstName` VARCHAR(45) NULL,
  `lastName` VARCHAR(45) NULL,
  `phone` VARCHAR(45) NULL,
  `email` VARCHAR(45) NULL,
  `dob` DATE NULL,
  `loyaltyPoints` VARCHAR(45) NULL,
  PRIMARY KEY (`customerId`),
  UNIQUE INDEX `customerId_UNIQUE` (`customerId` ASC),
  INDEX `fk_customer_user1_idx` (`userId` ASC),
  CONSTRAINT `fk_customer_user1`
    FOREIGN KEY (`userId`)
    REFERENCES `scrumptious`.`user` (`userId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`order`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`order` (
  `orderId` BINARY(16) NOT NULL,
  `customerId` BINARY(16) NOT NULL,
  `deliveryId` BINARY(16) NOT NULL,
  `isActive` TINYINT NOT NULL DEFAULT 0,
  `confirmationCode` VARCHAR(45) NULL,
  `createdAt` TIMESTAMP NULL,
  `updatedAt` TIMESTAMP NULL,
  PRIMARY KEY (`orderId`),
  INDEX `fk_order_delivery1_idx` (`deliveryId` ASC),
  UNIQUE INDEX `orderId_UNIQUE` (`orderId` ASC),
  INDEX `fk_order_customer1_idx` (`customerId` ASC),
  CONSTRAINT `fk_order_delivery1`
    FOREIGN KEY (`deliveryId`)
    REFERENCES `scrumptious`.`delivery` (`deliveryId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_order_customer1`
    FOREIGN KEY (`customerId`)
    REFERENCES `scrumptious`.`customer` (`customerId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`menuItem_order`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`menuItem_order` (
  `menuItemId` BINARY(16) NOT NULL,
  `orderId` BINARY(16) NOT NULL,
  `quantity` INT NOT NULL DEFAULT 1,
  PRIMARY KEY (`menuItemId`, `orderId`),
  INDEX `fk_consumableItem_has_order_order1_idx` (`orderId` ASC),
  INDEX `fk_consumableItem_has_order_consumableItem1_idx` (`menuItemId` ASC),
  CONSTRAINT `fk_consumableItem_has_order_consumableItem1`
    FOREIGN KEY (`menuItemId`)
    REFERENCES `scrumptious`.`menuItem` (`menuItemId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_consumableItem_has_order_order1`
    FOREIGN KEY (`orderId`)
    REFERENCES `scrumptious`.`order` (`orderId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`order_restaurant`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`order_restaurant` (
  `orderId` BINARY(16) NOT NULL,
  `restaurantId` BINARY(16) NOT NULL,
  `orderStatus` VARCHAR(32) NULL,
  PRIMARY KEY (`orderId`, `restaurantId`),
  INDEX `fk_order_has_restaurant_restaurant1_idx` (`restaurantId` ASC),
  INDEX `fk_order_has_restaurant_order1_idx` (`orderId` ASC),
  CONSTRAINT `fk_order_has_restaurant_order1`
    FOREIGN KEY (`orderId`)
    REFERENCES `scrumptious`.`order` (`orderId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_order_has_restaurant_restaurant1`
    FOREIGN KEY (`restaurantId`)
    REFERENCES `scrumptious`.`restaurant` (`restaurantId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`customer_address`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`customer_address` (
  `customerId` BINARY(16) NOT NULL,
  `addressId` BINARY(16) NOT NULL,
  PRIMARY KEY (`customerId`, `addressId`),
  INDEX `fk_customer_has_address_address1_idx` (`addressId` ASC),
  INDEX `fk_customer_has_address_customer1_idx` (`customerId` ASC),
  CONSTRAINT `fk_customer_has_address_customer1`
    FOREIGN KEY (`customerId`)
    REFERENCES `scrumptious`.`customer` (`customerId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_customer_has_address_address1`
    FOREIGN KEY (`addressId`)
    REFERENCES `scrumptious`.`address` (`addressId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`tag`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`tag` (
  `tagId` BINARY(16) NOT NULL,
  `tagType` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`tagId`),
  UNIQUE INDEX `tagId_UNIQUE` (`tagId` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`tag_menuItem`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`tag_menuItem` (
  `tagId` BINARY(16) NOT NULL,
  `menuItemId` BINARY(16) NOT NULL,
  PRIMARY KEY (`tagId`, `menuItemId`),
  INDEX `fk_tag_has_consumableItem_consumableItem1_idx` (`menuItemId` ASC),
  INDEX `fk_tag_has_consumableItem_tag1_idx` (`tagId` ASC),
  CONSTRAINT `fk_tag_has_consumableItem_tag1`
    FOREIGN KEY (`tagId`)
    REFERENCES `scrumptious`.`tag` (`tagId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_tag_has_consumableItem_consumableItem1`
    FOREIGN KEY (`menuItemId`)
    REFERENCES `scrumptious`.`menuItem` (`menuItemId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scrumptious`.`orderPayment`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrumptious`.`orderPayment` (
  `orderId` BINARY(16) NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `stripeId` VARCHAR(45) NULL,
  `refunded` TINYINT NULL,
  INDEX `fk_orderPayment_order1_idx` (`orderId` ASC),
  PRIMARY KEY (`orderId`),
  UNIQUE INDEX `order_orderId_UNIQUE` (`orderId` ASC),
  CONSTRAINT `fk_orderPayment_order1`
    FOREIGN KEY (`orderId`)
    REFERENCES `scrumptious`.`order` (`orderId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
