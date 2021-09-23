import os
import uuid
import random
import shutil
import pytest

from pathlib import Path
from app.db.config import Config
from app.db.database import Database
from app.producers.orders import main
from app.producers.orders import Order
from app.producers.orders import OrderGenerator
from app.producers.orders import OrderProducer
from app.producers.orders import OrdersArgParser
from app.producers.orders import get_delivery_ids
from app.producers.orders import get_customer_ids
from app.producers.orders import get_restaurant_ids
from test.helpers.testdata import make_test_data


def test_order_arg_parser():
    parser = OrdersArgParser(['--csv', 'file.csv', '--count', '10'])
    args = parser.args
    assert args.csv == 'file.csv'
    assert args.count == 10


def test_order_properties():
    order_id = 1
    cust_id = uuid.uuid4().hex
    deliv_id = 2
    rest_id = 3
    conf_code = 'abc'

    order = Order(order_id=order_id, cust_id=cust_id,  restaurant_id=rest_id, deliv_id=deliv_id, conf_code=conf_code)
    assert order.order_id == order_id
    assert order.cust_id == cust_id
    assert order.deliv_id == deliv_id
    assert order.restaurant_id == rest_id
    assert order.conf_code == conf_code

    order = Order(order_id, cust_id, rest_id, deliv_id, conf_code)
    assert order.order_id == order_id
    assert order.cust_id == cust_id
    assert order.deliv_id == deliv_id
    assert order.restaurant_id == rest_id
    assert order.conf_code == conf_code


def test_order_generator_generate_order():
    cust_id = uuid.uuid4().hex
    deliv_id = 1
    rest_id = 2

    order = OrderGenerator.generate_order(cust_id=cust_id, restaurant_id=rest_id,deliv_id=deliv_id)
    assert order.order_id is None
    assert order.cust_id == cust_id
    assert order.deliv_id == deliv_id
    assert order.restaurant_id == rest_id
    assert isinstance(order.conf_code, str)


db = Database(Config())


def _delete_orders(database: Database):
    database.open_connection()
    with database.conn.cursor() as cursor:
        cursor.execute('DELETE FROM `order`')
    database.conn.close()
    database.conn = None


def test_order_producer_save_order():
    _delete_orders(db)
    make_test_data(['--clear'])
    make_test_data(['--all', '2'])
    producer = OrderProducer(db)

    customer_id = get_customer_ids(db)[0].lower()
    delivery_id = get_delivery_ids(db)[0]
    rest_id = get_restaurant_ids(db)[0]
    order = OrderGenerator.generate_order(cust_id=customer_id, restaurant_id=rest_id, deliv_id=delivery_id)
    producer.save_order(order)

    db.open_connection()
    with db.conn.cursor() as cursor:
        cursor.execute("SELECT id,HEX(customer_id),delivery_id,restaurant_id,confirmation_code FROM `order`")
        results = cursor.fetchall()
    db.conn.close()
    db.conn = None

    assert len(results) == 1
    assert order.cust_id == results[0][1].lower()
    assert order.deliv_id == results[0][2]
    assert order.restaurant_id == results[0][3]
    assert order.conf_code == results[0][4]

    _delete_orders(db)
    make_test_data(['--clear'])


def test_order_producer_produce_random_empty_cust_delivery_ids():
    _delete_orders(db)
    producer = OrderProducer(db)
    producer.produce_random(num_orders=10, cust_ids=[], deliv_ids=[], rest_ids=[])
    results = db.run_query('SELECT * FROM `order`')
    assert len(results) == 0


def test_order_producer_produce_random(monkeypatch):
    _delete_orders(db)
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    make_test_data(['--clear'])
    make_test_data(['--all', '2'])

    producer = OrderProducer(db)
    customer_ids = get_customer_ids(db)
    delivery_ids = get_delivery_ids(db)
    rest_ids = get_restaurant_ids(db)

    orders = 5
    producer.produce_random(num_orders=orders, cust_ids=customer_ids,
                            deliv_ids=delivery_ids, rest_ids=rest_ids)

    results = db.run_query('SELECT * FROM `order`')
    assert len(results) == orders

    _delete_orders(db)
    make_test_data(['--clear'])


def test_order_producer_produce_random_no_continue(capsys, monkeypatch):
    _delete_orders(db)
    monkeypatch.setattr('builtins.input', lambda _: 'n')
    make_test_data(['--clear'])
    make_test_data(['--all', '2'])

    producer = OrderProducer(db)
    customer_ids = get_customer_ids(db)
    delivery_ids = get_delivery_ids(db)
    rest_ids = get_restaurant_ids(db)

    with pytest.raises(SystemExit):
        producer.produce_random(num_orders=5, cust_ids=customer_ids, deliv_ids=delivery_ids, rest_ids=rest_ids)

    captured = capsys.readouterr()
    last_line = captured.out.split(os.linesep)[-2]
    assert last_line == 'No records will be inserted.'

    _delete_orders(db)
    make_test_data(['--clear'])


def _create_csv_file(csv_file: str, count: int, id_start=1, bad_cust_id=False, bad_deliv_id=False, bad_rest_ids=False):
    cust_ids = get_customer_ids(db)
    deliv_ids = get_delivery_ids(db)
    rest_ids = get_restaurant_ids(db)

    with open(csv_file, 'w') as f:
        for order_id in range(id_start, id_start + count):
            cust_id = uuid.uuid4().hex if bad_cust_id else random.choice(cust_ids)
            deliv_id = 99999999 if bad_deliv_id else random.choice(deliv_ids)
            rest_id = 99999999 if bad_rest_ids else random.choice(rest_ids)
            order = OrderGenerator.generate_order(cust_id=cust_id, restaurant_id=rest_id, deliv_id=deliv_id)
            f.write(f"{order_id},{order.cust_id.lower()},{order.restaurant_id},"
                    f"{order.deliv_id},{order.conf_code}{os.linesep}")


def _read_csv_file(csv_file: str) -> list[Order]:
    orders = []
    with open(csv_file) as f:
        for line in f:
            fields = line.strip().split(',')
            order = Order(order_id=int(fields[0]),
                          cust_id=fields[1],
                          restaurant_id=int(fields[2]),
                          deliv_id=int(fields[3]),
                          conf_code=fields[4])
            orders.append(order)
    return orders


TEST_CSV_DIR = './tmp/test-orders'


def test_order_producer_produce_from_csv():
    _delete_orders(db)
    make_test_data(['--clear'])
    make_test_data(['--all', '2'])
    Path(TEST_CSV_DIR).mkdir(parents=True, exist_ok=True)
    _create_csv_file(f"{TEST_CSV_DIR}/orders-test.csv", count=5)
    producer = OrderProducer(db)

    results = db.run_query('SELECT * FROM `order`')
    assert len(results) == 0

    producer.produce_from_csv(f"{TEST_CSV_DIR}/orders-test.csv")

    results = db.run_query('SELECT id,HEX(customer_id),delivery_id,restaurant_id,confirmation_code'
                           ' FROM `order` ORDER BY id')
    assert len(results) == 5

    orders = _read_csv_file(f"{TEST_CSV_DIR}/orders-test.csv")
    orders.sort(key=lambda o: o.order_id)
    assert len(orders) == 5

    print(results)
    print(orders)

    for i in range(len(orders)):
        result = results[i]
        order = orders[i]
        assert order.order_id == result[0]
        assert order.cust_id == result[1].lower()
        assert order.deliv_id == result[2]
        assert order.restaurant_id == result[3]
        assert order.conf_code == result[4]

    shutil.rmtree(TEST_CSV_DIR)
    _delete_orders(db)
    make_test_data(['--clear'])


def test_order_producer_produce_from_csv_no_cust_id(capsys):
    _delete_orders(db)
    make_test_data(['--all', '2'])
    Path(TEST_CSV_DIR).mkdir(parents=True, exist_ok=True)
    _create_csv_file(f"{TEST_CSV_DIR}/orders-test.csv", count=5, bad_cust_id=True)
    producer = OrderProducer(db)

    results = db.run_query('SELECT * FROM `order`')
    assert len(results) == 0

    producer.produce_from_csv(f"{TEST_CSV_DIR}/orders-test.csv")
    out_lines = capsys.readouterr().out.split(os.linesep)[0:-1]
    for line in out_lines:
        assert 'Customer with id ' in line

    results = db.run_query('SELECT * FROM `order`')
    assert len(results) == 0

    shutil.rmtree(TEST_CSV_DIR)
    _delete_orders(db)
    make_test_data(['--clear'])


def test_order_producer_produce_from_csv_no_delivery_id(capsys):
    _delete_orders(db)
    make_test_data(['--all', '2'])
    Path(TEST_CSV_DIR).mkdir(parents=True, exist_ok=True)
    _create_csv_file(f"{TEST_CSV_DIR}/orders-test.csv", count=5, bad_deliv_id=True)
    producer = OrderProducer(db)

    results = db.run_query('SELECT * FROM `order`')
    assert len(results) == 0

    producer.produce_from_csv(f"{TEST_CSV_DIR}/orders-test.csv")

    out_lines = capsys.readouterr().out.split(os.linesep)[0:-1]
    for line in out_lines:
        assert 'Delivery with id ' in line

    results = db.run_query('SELECT * FROM `order`')
    assert len(results) == 0

    shutil.rmtree(TEST_CSV_DIR)
    _delete_orders(db)
    make_test_data(['--clear'])


def test_main_no_args(capsys):
    main([])
    output = capsys.readouterr().out
    assert '--csv or --count option must be provided.' in output


def test_main_csv_file_doesnt_exist(capsys):
    main(['--csv', 'nonexistent_file.csv'])
    output = capsys.readouterr().out
    assert 'nonexistent_file.csv does not exist.' in output


def test_main_negative_count(capsys):
    main(['--count', '-1'])
    output = capsys.readouterr().out
    assert 'A count greater than 0 must be provided.' in output


def test_main_no_customers_in_database(capsys):
    make_test_data(['--clear'])
    main(['--count', '5'])
    output = capsys.readouterr().out
    assert 'There are no customers in the database. Please add some.' in output


def test_main_no_deliveries_in_database(capsys):
    make_test_data(['--clear'])
    make_test_data(['--customers', '1'])
    main(['--count', '5'])
    output = capsys.readouterr().out
    assert 'There are no deliveries in the database. Please add some.' in output
    make_test_data(['--clear'])
