

class Order:
    id = None
    customer_id = None
    restaurant_id = None
    delivery_id = None
    confirmation_code = None

    def __init__(self, order_id, customer_id: str, restaurant_id: int, delivery_id: int, confirmation_code: str):
        """
        Constructor for creating an Order.

        :param order_id: int id of order
        :param customer_id: Hex string of UUID
        :param restaurant_id: int id of restaurant
        :param delivery_id: int id of delivery
        :param confirmation_code: string confirmation code
        """
        self.id = order_id
        self.customer_id = customer_id
        self.restaurant_id = restaurant_id
        self.delivery_id = delivery_id
        self.confirmation_code = confirmation_code

    def __str__(self):
        return f"id: {self.id}, customer_id: {self.customer_id}, restaurant_id: {self.restaurant_id}, " \
               f"delivery_id: {self.delivery_id}, confirmation_code: {self.confirmation_code}"
