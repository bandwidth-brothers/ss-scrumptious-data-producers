import os
import uuid
import json
import random
import shutil
import pytest

from pathlib import Path
from app.db.config import Config
from app.db.database import Database
from app.orders.model import Order
from app.orders.producer import OrderProducer
from app.orders.producer import get_delivery_ids
from app.orders.producer import get_customer_ids
from app.orders.producer import get_restaurant_ids
from app.orders.formatter import OrderFormatter
from app.orders.generator import OrderGenerator
from test.orders.testdata import make_test_data


db = Database(Config())


def _delete_orders():
    db.open_connection()
    with db.conn.cursor() as cursor:
        cursor.execute('DELETE FROM `order`')
    db.conn.close()
    db.conn = None


def test_order_producer_save_order():
    _delete_orders()
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
    assert order.customer_id == results[0][1].lower()
    assert order.delivery_id == results[0][2]
    assert order.restaurant_id == results[0][3]
    assert order.confirmation_code == results[0][4]

    _delete_orders()
    make_test_data(['--clear'])


def test_order_producer_produce_random_empty_cust_delivery_ids():
    _delete_orders()
    producer = OrderProducer(db)
    producer.produce_random(num_orders=10, cust_ids=[], deliv_ids=[], rest_ids=[])
    results = db.run_query('SELECT * FROM `order`')
    assert len(results) == 0


def test_order_producer_produce_random(monkeypatch):
    _delete_orders()
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

    _delete_orders()
    make_test_data(['--clear'])


def test_order_producer_produce_random_no_continue(capsys, monkeypatch):
    _delete_orders()
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

    _delete_orders()
    make_test_data(['--clear'])


def _generate_test_orders(count: int, id_start=1, bad_cust_id=False, bad_deliv_id=False,
                          bad_rest_ids=False) -> list[Order]:
    cust_ids = get_customer_ids(db)
    deliv_ids = get_delivery_ids(db)
    rest_ids = get_restaurant_ids(db)

    orders = []
    for order_id in range(id_start, id_start + count):
        cust_id = uuid.uuid4().hex if bad_cust_id else random.choice(cust_ids)
        rest_id = 99999999 if bad_rest_ids else random.choice(rest_ids)
        deliv_id = 99999999 if bad_deliv_id else random.choice(deliv_ids)
        order = OrderGenerator.generate_order(cust_id=cust_id, restaurant_id=rest_id, deliv_id=deliv_id)
        order.id = order_id
        orders.append(order)
    return orders


TEST_DATA_DIR = './tmp/test-items'
TEST_FILE_NAME = f"{TEST_DATA_DIR}/items-test"
CSV_TEST_FILE = f"{TEST_FILE_NAME}.csv"
JSON_TEST_FILE = f"{TEST_FILE_NAME}.json"
XML_TEST_FILE = f"{TEST_FILE_NAME}.xml"


def _assert_order_properties_from_result(order: Order, result):
    assert order.id == result[0]
    assert order.customer_id.lower() == result[1].lower()
    assert order.restaurant_id == result[2]
    assert order.delivery_id == result[3]
    assert order.confirmation_code == result[4]


def _create_csv_file(csv_file: str, count: int, id_start=1, bad_cust_id=False, bad_deliv_id=False, bad_rest_ids=False):
    orders = _generate_test_orders(count, id_start, bad_cust_id, bad_deliv_id, bad_rest_ids)
    with open(csv_file, 'w') as f:
        csv_str = OrderFormatter().to_csv(orders)
        f.write(csv_str)
    return orders


def _read_csv_file(csv_file: str) -> list[Order]:
    orders = []
    with open(csv_file) as f:
        orders += OrderFormatter().from_csv(f.read())
    return orders


def test_order_producer_produce_from_csv(monkeypatch):
    _delete_orders()
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    make_test_data(['--clear'])
    make_test_data(['--all', '2'])
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_csv_file(CSV_TEST_FILE, count=5)
    producer = OrderProducer(db)

    results = db.run_query('SELECT * FROM `order`')
    assert len(results) == 0

    producer.produce_from_csv(CSV_TEST_FILE)

    results = db.run_query('SELECT id,HEX(customer_id),restaurant_id,delivery_id,confirmation_code'
                           ' FROM `order` ORDER BY id')
    assert len(results) == 5

    orders = _read_csv_file(CSV_TEST_FILE)
    orders.sort(key=lambda o: o.id)
    assert len(orders) == 5

    for i in range(len(orders)):
        result = results[i]
        order = orders[i]
        _assert_order_properties_from_result(order, result)

    shutil.rmtree(TEST_DATA_DIR)
    _delete_orders()
    make_test_data(['--clear'])


def test_order_producer_produce_from_csv_no_cust_id(capsys):
    _delete_orders()
    make_test_data(['--clear'])
    make_test_data(['--all', '1'])
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_csv_file(CSV_TEST_FILE, count=1, bad_cust_id=True)
    producer = OrderProducer(db)

    results = db.run_query('SELECT * FROM `order`')
    assert len(results) == 0

    with pytest.raises(SystemExit):
        producer.produce_from_csv(CSV_TEST_FILE)

    output = capsys.readouterr().out
    assert 'Customer with id ' in output

    results = db.run_query('SELECT * FROM `order`')
    assert len(results) == 0

    shutil.rmtree(TEST_DATA_DIR)
    _delete_orders()
    make_test_data(['--clear'])


def test_order_producer_produce_from_csv_no_delivery_id(capsys):
    _delete_orders()
    make_test_data(['--clear'])
    make_test_data(['--all', '2'])
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_csv_file(CSV_TEST_FILE, count=1, bad_deliv_id=True)
    producer = OrderProducer(db)

    results = db.run_query('SELECT * FROM `order`')
    assert len(results) == 0

    with pytest.raises(SystemExit):
        producer.produce_from_csv(CSV_TEST_FILE)

    output = capsys.readouterr().out
    assert 'Delivery with id ' in output

    results = db.run_query('SELECT * FROM `order`')
    assert len(results) == 0

    shutil.rmtree(TEST_DATA_DIR)
    _delete_orders()
    make_test_data(['--clear'])


def test_order_producer_produce_from_csv_no_restaurant_id(capsys):
    _delete_orders()
    make_test_data(['--clear'])
    make_test_data(['--all', '2'])
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_csv_file(CSV_TEST_FILE, count=1, bad_rest_ids=True)
    producer = OrderProducer(db)

    results = db.run_query('SELECT * FROM `order`')
    assert len(results) == 0

    with pytest.raises(SystemExit):
        producer.produce_from_csv(CSV_TEST_FILE)

    output = capsys.readouterr().out
    assert 'Restaurant with id ' in output

    results = db.run_query('SELECT * FROM `order`')
    assert len(results) == 0

    shutil.rmtree(TEST_DATA_DIR)
    _delete_orders()
    make_test_data(['--clear'])


def _create_json_file(json_file: str, count: int, id_start=1,
                      bad_cust_id=False, bad_deliv_id=False, bad_rest_ids=False) -> list[Order]:
    orders = _generate_test_orders(count, id_start, bad_cust_id, bad_deliv_id, bad_rest_ids)
    with open(json_file, 'w') as f:
        f.write(OrderFormatter().to_json(orders))
    return orders


def _read_json_file(csv_file: str) -> list[Order]:
    orders = []
    with open(csv_file) as f:
        orders += OrderFormatter().from_json(f.read())
    return orders


def test_order_producer_produce_from_json_correct_fields(monkeypatch):
    _delete_orders()
    make_test_data(['--clear'])
    make_test_data(['--all', '1'])
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_json_file(JSON_TEST_FILE, count=1)

    producer = OrderProducer(db)
    producer.produce_from_json(JSON_TEST_FILE)

    order = _read_json_file(JSON_TEST_FILE)[0]
    result = db.run_query('SELECT id,HEX(customer_id),restaurant_id,delivery_id,confirmation_code '
                          'FROM `order`')[0]
    _assert_order_properties_from_result(order, result)

    shutil.rmtree(TEST_DATA_DIR)
    _delete_orders()
    make_test_data(['--clear'])


def test_order_producer_produce_from_json_multiple(monkeypatch):
    _delete_orders()
    make_test_data(['--clear'])
    make_test_data(['--all', '5'])
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_json_file(JSON_TEST_FILE, count=5)

    producer = OrderProducer(db)
    producer.produce_from_json(JSON_TEST_FILE)

    results = db.run_query('SELECT id,HEX(customer_id),restaurant_id,delivery_id,confirmation_code '
                           'FROM `order` ORDER BY id')
    orders = sorted(_read_json_file(JSON_TEST_FILE), key=lambda o: o.id)

    for i in range(len(orders)):
        order = orders[i]
        result = results[i]
        _assert_order_properties_from_result(order, result)

    shutil.rmtree(TEST_DATA_DIR)
    _delete_orders()
    make_test_data(['--clear'])


def test_order_producer_produce_from_json_missing_field(capsys):
    producer = OrderProducer(db)
    data = {
        'id': 1,
        'customer_id': uuid.uuid4().hex,
        'restaurant_id': 2,
        'confirmation_code': 'some-conf-code'
    }
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    with open(JSON_TEST_FILE, 'w') as f:
        f.write(json.dumps(data))

    with pytest.raises(SystemExit):
        producer.produce_from_json(JSON_TEST_FILE)

    captured = capsys.readouterr()
    output = captured.out
    assert "Order missing 'delivery_id'" in output

    shutil.rmtree(TEST_DATA_DIR)


def test_order_producer_produce_from_json_bad_format(capsys):
    json_str = '{"bad":json}'
    producer = OrderProducer(db)

    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    with open(JSON_TEST_FILE, 'w') as f:
        f.write(json_str)

    with pytest.raises(SystemExit):
        producer.produce_from_json(JSON_TEST_FILE)

    captured = capsys.readouterr()
    output = captured.out
    assert "JSON is not valid format" in output

    shutil.rmtree(TEST_DATA_DIR)


def _create_xml_file(xml_file: str, count: int, id_start=1, bad_cust_id=False,
                     bad_deliv_id=False, bad_rest_ids=False) -> list[Order]:
    orders = _generate_test_orders(count, id_start, bad_cust_id, bad_deliv_id, bad_rest_ids)
    with open(xml_file, 'w') as f:
        f.write(OrderFormatter().to_xml(orders))
    return orders


def _read_xml_file(xml_file: str):
    orders = []
    with open(xml_file) as f:
        orders += OrderFormatter().from_xml(f.read())
    return orders


def test_order_producer_produce_from_xml(monkeypatch):
    _delete_orders()
    make_test_data(['--clear'])
    make_test_data(['--all', '1'])
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_xml_file(XML_TEST_FILE, count=1)

    producer = OrderProducer(db)
    producer.produce_from_xml(XML_TEST_FILE)

    order = _read_xml_file(XML_TEST_FILE)[0]
    result = db.run_query('SELECT id,HEX(customer_id),restaurant_id,delivery_id,confirmation_code FROM `order`')[0]
    _assert_order_properties_from_result(order, result)

    shutil.rmtree(TEST_DATA_DIR)
    _delete_orders()
    make_test_data(['--clear'])


def test_order_producer_produce_from_xml_multiple(monkeypatch):
    _delete_orders()
    make_test_data(['--clear'])
    make_test_data(['--all', '5'])
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_xml_file(XML_TEST_FILE, count=5)

    producer = OrderProducer(db)
    producer.produce_from_xml(XML_TEST_FILE)

    orders = sorted(_read_xml_file(XML_TEST_FILE), key=lambda o: o.id)
    results = db.run_query('SELECT id,HEX(customer_id),restaurant_id,delivery_id,confirmation_code '
                           'FROM `order` ORDER BY id')

    for i in range(len(orders)):
        order = orders[i]
        result = results[i]
        _assert_order_properties_from_result(order, result)

    shutil.rmtree(TEST_DATA_DIR)
    _delete_orders()
    make_test_data(['--clear'])


def test_order_producer_produce_from_xml_bad_format(capsys):
    xml_str = '<items><order><id>1234</id></order></items'
    producer = OrderProducer(db)

    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    with open(XML_TEST_FILE, 'w') as f:
        f.write(xml_str)

    with pytest.raises(SystemExit):
        producer.produce_from_xml(XML_TEST_FILE)

    captured = capsys.readouterr()
    output = captured.out
    assert "Malformed XML" in output

    shutil.rmtree(TEST_DATA_DIR)


def test_order_producer_convert_unsupported_format(capsys):
    producer = OrderProducer(db)

    with pytest.raises(SystemExit):
        producer.convert_files('file.txt', 'file.json')

    captured = capsys.readouterr()
    output = captured.out
    assert "txt input format not supported" in output

    with pytest.raises(SystemExit):
        producer.convert_files('file.json', 'file.txt')

    captured = capsys.readouterr()
    output = captured.out
    assert "txt output format not supported" in output


def test_user_producer_convert():
    producer = OrderProducer(db)
    make_test_data(['--all', '1'])
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_json_file(JSON_TEST_FILE, id_start=1, count=1)

    producer.convert_files(JSON_TEST_FILE, CSV_TEST_FILE)

    order = _read_csv_file(CSV_TEST_FILE)[0]

    assert order.id == 1
    assert order.customer_id is not None
    assert order.restaurant_id is not None
    assert order.delivery_id is not None
    assert order.confirmation_code is not None

    shutil.rmtree(TEST_DATA_DIR)
    make_test_data(['--clear'])
