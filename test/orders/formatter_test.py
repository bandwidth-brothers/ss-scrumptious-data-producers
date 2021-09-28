import json

from app.orders.formatter import OrderFormatter


def test_order_formatter_create_object_from_string_fields():
    fields = ['1', 'cust-id', '2', '3', 'conf-code']
    order = OrderFormatter().create_object_from_string_fields(fields)

    assert order.id == 1
    assert order.customer_id == 'cust-id'
    assert order.restaurant_id == 2
    assert order.delivery_id == 3
    assert order.confirmation_code == 'conf-code'


def test_order_formatter_create_object_from_string_dict():
    _dict = {'id': '1',
             'customer_id': 'cust-id',
             'restaurant_id': '2',
             'delivery_id': '3',
             'confirmation_code': 'conf-code'}
    order = OrderFormatter().create_object_from_string_dict(_dict)

    assert order.id == 1
    assert order.customer_id == 'cust-id'
    assert order.restaurant_id == 2
    assert order.delivery_id == 3
    assert order.confirmation_code == 'conf-code'


def test_order_formatter_json_decoder():
    json_str = """
    [
        {
            "id": 1,
            "customer_id": "cust-id",
            "restaurant_id": 2,
            "delivery_id": 3,
            "confirmation_code": "conf-code"
        }
    ]
    """
    order = json.loads(json_str, cls=OrderFormatter.OrderJsonDecoder)[0]

    assert order.id == 1
    assert order.customer_id == 'cust-id'
    assert order.restaurant_id == 2
    assert order.delivery_id == 3
    assert order.confirmation_code == 'conf-code'
