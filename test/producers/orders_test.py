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
from test.helpers.testdata import make_test_data

from _pytest.monkeypatch import MonkeyPatch


def test_order_arg_parser():
    parser = OrdersArgParser(['--csv', 'file.csv', '--count', '10', '--active', '5'])
    args = parser.args
    assert args.csv == 'file.csv'
    assert args.count == 10
    assert args.active == 5


def test_order_properties():
    order_id = uuid.uuid4()
    cust_id = uuid.uuid4().hex
    deliv_id = uuid.uuid4().hex
    is_active = True
    conf_code = str(uuid.uuid4()).replace('-', '')[0:10]

    order = Order(order_id=order_id, cust_id=cust_id, deliv_id=deliv_id, is_active=is_active, conf_code=conf_code)
    assert order.order_id == order_id
    assert order.cust_id == cust_id
    assert order.deliv_id == deliv_id
    assert order.is_active == is_active
    assert order.conf_code == conf_code

    order = Order(order_id, cust_id, deliv_id, is_active, conf_code)
    assert order.order_id == order_id
    assert order.cust_id == cust_id
    assert order.deliv_id == deliv_id
    assert order.is_active == is_active
    assert order.conf_code == conf_code


def test_order_generator_generate_order():
    cust_id = uuid.uuid4().hex
    deliv_id = uuid.uuid4().hex
    is_active = True

    order = OrderGenerator.generate_order(cust_id, deliv_id, is_active)
    assert isinstance(order.order_id, uuid.UUID)
    assert order.cust_id == cust_id
    assert order.deliv_id == deliv_id
    assert order.is_active == is_active
    assert isinstance(order.conf_code, str)


database = Database(Config())


def delete_orders(db: Database):
    db.open_connection()
    with db.conn.cursor() as cursor:
        cursor.execute('DELETE FROM `order`')
    db.conn.close()
    db.conn = None


def test_order_producer_save_order():
    make_test_data(['--all', '2'])
    producer = OrderProducer(database)

    customer_id = get_customer_ids(database)[0]
    delivery_id = get_delivery_ids(database)[0]
    order = OrderGenerator.generate_order(customer_id, delivery_id, is_active=True)
    producer.save_order(order)

    database.open_connection()
    with database.conn.cursor() as cursor:
        cursor.execute("SELECT HEX(orderId),HEX(customerId),HEX(deliveryId),isActive,confirmationCode FROM `order` "
                       "WHERE orderId = UNHEX(?)", (order.order_id.hex,))
        result = cursor.fetchone()
    database.conn.close()
    database.conn = None

    assert order.order_id.hex == result[0].lower()
    assert order.cust_id == result[1].lower()
    assert order.deliv_id == result[2].lower()
    assert order.is_active == result[3]
    assert order.conf_code == result[4]

    delete_orders(database)
    make_test_data(['--clear'])


def test_order_producer_produce_random_empty_cust_delivery_ids():
    producer = OrderProducer(database)
    producer.produce_random(num_orders=10, cust_ids=[], deliv_ids=[], num_active=5)
    results = database.run_query('SELECT * FROM `order`')
    assert len(results) == 0


def test_order_producer_produce_random():
    monkeypatch = MonkeyPatch()
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    make_test_data(['--all', '2'])

    producer = OrderProducer(database)
    customer_ids = get_customer_ids(database)
    delivery_ids = get_delivery_ids(database)

    orders = 5
    producer.produce_random(num_orders=orders, cust_ids=customer_ids, deliv_ids=delivery_ids, num_active=2)

    results = database.run_query('SELECT * FROM `order`')
    assert len(results) == orders

    delete_orders(database)
    make_test_data(['--clear'])


def test_order_producer_produce_random_no_continue(capsys):
    monkeypatch = MonkeyPatch()
    monkeypatch.setattr('builtins.input', lambda _: 'n')
    make_test_data(['--all', '2'])

    producer = OrderProducer(database)
    customer_ids = get_customer_ids(database)
    delivery_ids = get_delivery_ids(database)

    with pytest.raises(SystemExit):
        producer.produce_random(num_orders=5, cust_ids=customer_ids, deliv_ids=delivery_ids, num_active=2)

    captured = capsys.readouterr()
    last_line = captured.out.split(os.linesep)[-2]
    assert last_line == 'No records will be inserted.'

    delete_orders(database)
    make_test_data(['--clear'])


def _create_csv_file(csv_file: str, count: int, bad_cust_id=False, bad_deliv_id=False):
    cust_ids = get_customer_ids(database)
    deliv_ids = get_delivery_ids(database)

    with open(csv_file, 'w') as f:
        for _ in range(count):
            cust_id = uuid.uuid4().hex if bad_cust_id else random.choice(cust_ids)
            deliv_id = uuid.uuid4().hex if bad_deliv_id else random.choice(deliv_ids)
            order = OrderGenerator.generate_order(cust_id, deliv_id, is_active=True)
            f.write(f"{order.order_id.hex},{order.cust_id.lower()},{order.deliv_id.lower()},"
                    f"{order.is_active},{order.conf_code}{os.linesep}")


def _read_csv_file(csv_file: str) -> list[Order]:
    orders = []
    with open(csv_file) as f:
        for line in f:
            fields = line.strip().split(',')
            order = Order(order_id=uuid.UUID(fields[0]),
                          cust_id=fields[1],
                          deliv_id=fields[2],
                          is_active=bool(fields[3]),
                          conf_code=fields[4])
            orders.append(order)
    return orders


TEST_CSV_DIR = './tmp/test-orders'


def test_order_producer_produce_from_csv():
    make_test_data(['--all', '2'])
    Path(TEST_CSV_DIR).mkdir(parents=True, exist_ok=True)
    _create_csv_file(f"{TEST_CSV_DIR}/orders-test.csv", 5)
    producer = OrderProducer(database)

    results = database.run_query('SELECT * FROM `order`')
    assert len(results) == 0

    producer.produce_from_csv(f"{TEST_CSV_DIR}/orders-test.csv")

    results = database.run_query('SELECT HEX(orderId),HEX(customerId),HEX(deliveryId),isActive,confirmationCode '
                                 'FROM `order` ORDER BY confirmationCode')
    assert len(results) == 5

    orders = _read_csv_file(f"{TEST_CSV_DIR}/orders-test.csv")
    orders.sort(key=lambda o: o.conf_code)
    assert len(orders) == 5

    for i in range(len(orders)):
        result = results[i]
        order = orders[i]
        assert order.order_id.hex == result[0].lower()
        assert order.cust_id == result[1].lower()
        assert order.deliv_id == result[2].lower()
        assert order.is_active == result[3]
        assert order.conf_code == result[4]

    shutil.rmtree(TEST_CSV_DIR)
    delete_orders(database)
    make_test_data(['--clear'])


def test_order_producer_produce_from_csv_no_cust_id(capsys):
    make_test_data(['--all', '2'])
    Path(TEST_CSV_DIR).mkdir(parents=True, exist_ok=True)
    _create_csv_file(f"{TEST_CSV_DIR}/orders-test.csv", count=5, bad_cust_id=True)
    producer = OrderProducer(database)

    results = database.run_query('SELECT * FROM `order`')
    assert len(results) == 0

    producer.produce_from_csv(f"{TEST_CSV_DIR}/orders-test.csv")
    out_lines = capsys.readouterr().out.split(os.linesep)[0:-1]
    for line in out_lines:
        assert 'Customer with id ' in line

    results = database.run_query('SELECT * FROM `order`')
    assert len(results) == 0

    shutil.rmtree(TEST_CSV_DIR)
    delete_orders(database)
    make_test_data(['--clear'])


def test_order_producer_produce_from_csv_no_delivery_id(capsys):
    make_test_data(['--all', '2'])
    Path(TEST_CSV_DIR).mkdir(parents=True, exist_ok=True)
    _create_csv_file(f"{TEST_CSV_DIR}/orders-test.csv", count=5, bad_deliv_id=True)
    producer = OrderProducer(database)

    results = database.run_query('SELECT * FROM `order`')
    assert len(results) == 0

    producer.produce_from_csv(f"{TEST_CSV_DIR}/orders-test.csv")

    out_lines = capsys.readouterr().out.split(os.linesep)[0:-1]
    for line in out_lines:
        assert 'Delivery with id ' in line

    results = database.run_query('SELECT * FROM `order`')
    assert len(results) == 0

    shutil.rmtree(TEST_CSV_DIR)
    delete_orders(database)
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


def test_main_active_greater_than_count(capsys):
    main(['--count', '5', '--active', '6'])
    output = capsys.readouterr().out
    assert 'Active orders must be less than or equal to the total count.' in output


def test_main_no_customers_in_database(capsys):
    main(['--count', '5'])
    output = capsys.readouterr().out
    assert 'There are no customers in the database. Please add some.' in output


def test_main_no_deliveries_in_database(capsys):
    make_test_data(['--customers', '1'])
    main(['--count', '5'])
    output = capsys.readouterr().out
    assert 'There are no deliveries in the database. Please add some.' in output
    make_test_data(['--clear'])
