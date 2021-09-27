import json

from typing import Type
from app.orders.model import Order
from app.common.formatter import AbstractFormatter


class OrderFormatter(AbstractFormatter[Order]):

    class OrderJsonDecoder(json.JSONDecoder):
        def __init__(self, *args, **kwargs):
            json.JSONDecoder.__init__(self, object_hook=OrderFormatter.OrderJsonDecoder._object_hook, *args, **kwargs)

        @classmethod
        def _object_hook(cls, dct) -> Order:
            order_id = cls._get(dct, 'id')
            customer_id = cls._get(dct, 'customer_id')
            restaurant_id = cls._get(dct, 'restaurant_id')
            delivery_id = cls._get(dct, 'delivery_id')
            confirmation_code = cls._get(dct, 'confirmation_code')

            return Order(order_id=int(order_id), customer_id=customer_id, restaurant_id=int(restaurant_id),
                         delivery_id=int(delivery_id), confirmation_code=confirmation_code)

        @classmethod
        def _get(cls, dct, name):
            return AbstractFormatter.get_attr_or_throw(dct, name)

    class OrderJsonEncoder(json.JSONEncoder):
        def default(self, obj):
            return obj.__dict__

    def get_json_encoder(self) -> Type[OrderJsonEncoder]:
        return OrderFormatter.OrderJsonEncoder

    def get_json_decoder(self) -> Type[OrderJsonDecoder]:
        return OrderFormatter.OrderJsonDecoder

    def get_attr_list(self):
        return ['id', 'customer_id', 'restaurant_id', 'delivery_id', 'confirmation_code']

    def get_object_type(self) -> Type[Order]:
        return Order

    def create_object_from_string_fields(self, fields: list[str]):
        return Order(order_id=int(fields[0]),
                     customer_id=fields[1],
                     restaurant_id=int(fields[2]),
                     delivery_id=int(fields[3]),
                     confirmation_code=fields[4])

    def create_object_from_string_dict(self, _dict) -> Order:
        return Order(order_id=int(_dict['id']),
                     customer_id=_dict['customer_id'],
                     restaurant_id=int(_dict['restaurant_id']),
                     delivery_id=int(_dict['delivery_id']),
                     confirmation_code=_dict['confirmation_code'])
