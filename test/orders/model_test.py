import uuid

from app.orders.model import Order


def test_order_properties_by_name():
    order_id = 1
    cust_id = uuid.uuid4().hex
    rest_id = 2
    deliv_id = 3
    conf_code = 'code'
    order = Order(order_id=order_id, customer_id=cust_id, restaurant_id=rest_id,
                  delivery_id=deliv_id, confirmation_code=conf_code)

    assert order.id == order_id
    assert order.customer_id == cust_id
    assert order.restaurant_id == rest_id
    assert order.delivery_id == deliv_id
    assert order.confirmation_code == conf_code


def test_order_properties_by_position():
    order_id = 1
    cust_id = uuid.uuid4().hex
    rest_id = 2
    deliv_id = 3
    conf_code = 'code'
    order = Order(order_id, cust_id, rest_id, deliv_id, conf_code)

    assert order.id == order_id
    assert order.customer_id == cust_id
    assert order.restaurant_id == rest_id
    assert order.delivery_id == deliv_id
    assert order.confirmation_code == conf_code
