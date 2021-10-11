import uuid

from app.orders.model import Order


class OrderGenerator:
    @classmethod
    def generate_order(cls, cust_id: str, restaurant_id: int, deliv_id: int) -> Order:
        """
        Generate an Order object.

        :param cust_id: a uuid hex string of customer id
        :param deliv_id: a uuid hex string of deliver id
        :param restaurant_id: int id of restaurant
        :return: the Order
        """
        conf_code = str(uuid.uuid4()).replace('-', '')[0:10]
        return Order(order_id=None, customer_id=cust_id, restaurant_id=restaurant_id, delivery_id=deliv_id,
                     confirmation_code=conf_code)
