
from app.db.config import Config
from app.db.database import Database
from app.orders.dependencies import DeliveryData
from app.orders.dependencies import CustomerData
from app.orders.dependencies import RestaurantData
from test.orders.testdata import make_test_data


db = Database(Config())


def test_order_dependencies_customer_data():
    make_test_data(['--clear'])
    CustomerData.create_customers(db, count=5)

    db.open_connection()
    with db.conn.cursor() as curs:
        curs.execute('SELECT * FROM customer')
        custs = curs.fetchall()

        curs.execute('SELECT * FROM `user`')
        users = curs.fetchall()
    db.conn.close()
    db.conn = None

    assert len(custs) == 5
    assert len(users) == 5

    make_test_data(['--clear'])


def test_order_dependencies_restaurant_data():
    make_test_data(['--clear'])
    RestaurantData.create_restaurants(db, count=5)

    db.open_connection()
    with db.conn.cursor() as curs:
        curs.execute('SELECT * FROM restaurant')
        rests = curs.fetchall()

        curs.execute('SELECT * FROM address')
        addrs = curs.fetchall()
    db.conn.close()
    db.conn = None

    assert len(rests) == 5
    assert len(addrs) == 5

    make_test_data(['--clear'])


def test_order_dependencies_delivery_data():
    make_test_data(['--clear'])
    DeliveryData.create_deliveries(db, count=5)

    db.open_connection()
    with db.conn.cursor() as curs:
        curs.execute('SELECT * FROM delivery')
        delivs = curs.fetchall()

        curs.execute('SELECT * FROM address')
        addrs = curs.fetchall()

        curs.execute('SELECT * FROM driver')
        drivers = curs.fetchall()

        curs.execute('SELECT * FROM user')
        users = curs.fetchall()
    db.conn.close()
    db.conn = None

    assert len(delivs) == 5
    assert len(addrs) == 10
    assert len(drivers) == 5
    assert len(users) == 5

    make_test_data(['--clear'])

