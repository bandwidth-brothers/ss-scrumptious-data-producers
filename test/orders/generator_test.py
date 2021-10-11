
from app.orders.generator import OrderGenerator


def test_user_generator_generate_order():
    cust_id = 'some-id'
    rest_id = 1
    deliv_id = 2
    order = OrderGenerator.generate_order(cust_id=cust_id, restaurant_id=rest_id, deliv_id=deliv_id)

    assert order.customer_id == cust_id
    assert order.restaurant_id == rest_id
    assert order.delivery_id == deliv_id
    assert order.confirmation_code is not None
