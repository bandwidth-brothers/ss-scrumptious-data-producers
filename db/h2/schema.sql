
CREATE TABLE IF NOT EXISTS `user` (
	`userId` BINARY(16) NOT NULL,
	`userRole` VARCHAR(255) NOT NULL,
	`username` VARCHAR(16) NOT NULL,
	`password` VARCHAR(32) NOT NULL,
	`email` VARCHAR(255) NOT NULL,
	`profilePic` VARCHAR(255) NULL,
	`createdAt` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`updatedAt` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `address` (
	`addressId` BINARY(16) NOT NULL,
	`line1` VARCHAR(255) NOT NULL,
	`line2` VARCHAR(45) NULL,
	`city` VARCHAR(45) NOT NULL,
	`state` VARCHAR(45) NOT NULL,
	`zip` VARCHAR(45) NOT NULL
);

CREATE TABLE IF NOT EXISTS `restaurant_owner` (
	`restaurantOwnerId` BINARY(16) NOT NULL,
	`userId` BINARY(16) NOT NULL,
	`firstName` VARCHAR(45) NULL,
	`lastName` VARCHAR(45) NULL,
	`phone` VARCHAR(45) NULL,
	`email` VARCHAR(45) NULL,
	INDEX fk_customer_user1_idx25(`userId` ASC)
);

CREATE TABLE IF NOT EXISTS `restaurant` (
	`restaurantId` BINARY(16) NOT NULL,
	`addressId` BINARY(16) NOT NULL,
	`restaurantOwnerId` BINARY(16) NOT NULL,
	`name` VARCHAR(45) NOT NULL,
	`rating` FLOAT NOT NULL DEFAULT 0,
	`priceCategory` INT NULL,
	`phone` VARCHAR(45) NULL,
	`isActive` TINYINT NULL,
	`restaurantLogo` VARCHAR(255) NULL,
	INDEX fk_restaurant_address1_idx26(`addressId` ASC),
	INDEX fk_restaurant_restaurant_owner1_idx27(`restaurantOwnerId` ASC)
);

CREATE TABLE IF NOT EXISTS `category` (
	`categoryId` BINARY(16) NOT NULL,
	`type` VARCHAR(45) NOT NULL
);

CREATE TABLE IF NOT EXISTS `restaurant_category` (
	`restaurantId` BINARY(16) NOT NULL,
	`categoryId` BINARY(16) NOT NULL,
	INDEX fk_restaurant_category_restaurant1_idx28(`restaurantId` ASC),
	INDEX fk_restaurant_category_category1_idx29(`categoryId` ASC)
);

CREATE TABLE IF NOT EXISTS `menuItem` (
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
	INDEX fk_food_restaurant1_idx30(`restaurantId` ASC)
);

CREATE TABLE IF NOT EXISTS `menu_category` (
	`categoryId` BINARY(16) NOT NULL,
	`type` VARCHAR(45) NOT NULL
);

CREATE TABLE IF NOT EXISTS `category_menuItem` (
	`categoryId` BINARY(16) NOT NULL,
	`menuItemId` BINARY(16) NOT NULL,
	INDEX fk_food_category_food1_idx31(`menuItemId` ASC),
	INDEX fk_food_category_menu_category1_idx32(`categoryId` ASC)
);

CREATE TABLE IF NOT EXISTS `driver` (
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
	INDEX fk_driver_address1_idx33(`locationId` ASC),
	INDEX fk_driver_user1_idx34(`userId` ASC)
);

CREATE TABLE IF NOT EXISTS `delivery` (
	`deliveryId` BINARY(16) NOT NULL,
	`destinationId` BINARY(16) NOT NULL,
	`driverId` BINARY(16) NOT NULL,
	`estimatedDel` TIMESTAMP NULL,
	INDEX fk_delivery_address1_idx35(`destinationId` ASC),
	INDEX fk_delivery_driver1_idx36(`driverId` ASC)
);

CREATE TABLE IF NOT EXISTS `customer` (
	`customerId` BINARY(16) NOT NULL,
	`userId` BINARY(16) NOT NULL,
	`firstName` VARCHAR(45) NULL,
	`lastName` VARCHAR(45) NULL,
	`phone` VARCHAR(45) NULL,
	`email` VARCHAR(45) NULL,
	`dob` DATE NULL,
	`loyaltyPoints` VARCHAR(45) NULL,
	INDEX fk_customer_user1_idx37(`userId` ASC)
);

CREATE TABLE IF NOT EXISTS `order` (
	`orderId` BINARY(16) NOT NULL,
	`customerId` BINARY(16) NOT NULL,
	`deliveryId` BINARY(16) NOT NULL,
	`isActive` TINYINT NOT NULL DEFAULT 0,
	`confirmationCode` VARCHAR(45) NULL,
	`createdAt` TIMESTAMP NULL,
	`updatedAt` TIMESTAMP NULL,
	INDEX fk_order_delivery1_idx38(`deliveryId` ASC),
	INDEX fk_order_customer1_idx39(`customerId` ASC)
);

CREATE TABLE IF NOT EXISTS `menuItem_order` (
	`menuItemId` BINARY(16) NOT NULL,
	`orderId` BINARY(16) NOT NULL,
	`quantity` INT NOT NULL DEFAULT 1,
	INDEX fk_consumableItem_has_order_order1_idx40(`orderId` ASC),
	INDEX fk_consumableItem_has_order_consumableItem1_idx41(`menuItemId` ASC)
);

CREATE TABLE IF NOT EXISTS `order_restaurant` (
	`orderId` BINARY(16) NOT NULL,
	`restaurantId` BINARY(16) NOT NULL,
	`orderStatus` VARCHAR(32) NULL,
	INDEX fk_order_has_restaurant_restaurant1_idx42(`restaurantId` ASC),
	INDEX fk_order_has_restaurant_order1_idx43(`orderId` ASC)
);

CREATE TABLE IF NOT EXISTS `customer_address` (
	`customerId` BINARY(16) NOT NULL,
	`addressId` BINARY(16) NOT NULL,
	INDEX fk_customer_has_address_address1_idx44(`addressId` ASC),
	INDEX fk_customer_has_address_customer1_idx45(`customerId` ASC)
);

CREATE TABLE IF NOT EXISTS `tag` (
	`tagId` BINARY(16) NOT NULL,
	`tagType` VARCHAR(45) NOT NULL
);

CREATE TABLE IF NOT EXISTS `tag_menuItem` (
	`tagId` BINARY(16) NOT NULL,
	`menuItemId` BINARY(16) NOT NULL,
	INDEX fk_tag_has_consumableItem_consumableItem1_idx46(`menuItemId` ASC),
	INDEX fk_tag_has_consumableItem_tag1_idx47(`tagId` ASC)
);

CREATE TABLE IF NOT EXISTS `orderPayment` (
	`orderId` BINARY(16) NOT NULL,
	`name` VARCHAR(45) NOT NULL,
	`stripeId` VARCHAR(45) NULL,
	`refunded` TINYINT NULL,
	INDEX fk_orderPayment_order1_idx48(`orderId` ASC)
);
