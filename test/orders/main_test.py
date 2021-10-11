import pytest
import shutil

from pathlib import Path
from app.orders.main import main


def test_main_produce_random_called_with_correct_arguments(monkeypatch, test_kwargs):
    monkeypatch.setattr('app.orders.producer.OrderProducer.produce_random', test_kwargs)
    monkeypatch.setattr('app.orders.main.get_customer_ids', lambda _: ['1', '2'])
    monkeypatch.setattr('app.orders.main.get_restaurant_ids', lambda _: [3, 4])
    monkeypatch.setattr('app.orders.main.get_delivery_ids', lambda _: [5, 6])

    main(['produce', '--count', '5'])
    assert test_kwargs.args == {'num_orders': 5, 'cust_ids': ['1', '2'], 'rest_ids': [3, 4], 'deliv_ids': [5, 6]}


def test_main_count_is_negative(capsys):
    main(['produce', '--count', '-1'])
    output = capsys.readouterr().out
    assert 'A count greater than 0 must be provided' in output


def test_main_no_customers(monkeypatch, capsys):
    monkeypatch.setattr('app.orders.main.get_restaurant_ids', lambda _: [3, 4])
    monkeypatch.setattr('app.orders.main.get_delivery_ids', lambda _: [5, 6])
    # monkeypatch.setattr('app.orders.producer.get_restaurant_ids', lambda _: [3, 4])
    # monkeypatch.setattr('app.orders.producer.get_delivery_ids', lambda _: [5, 6])

    main(['produce', '--count', '5'])
    output = capsys.readouterr().out
    assert 'There are no customers in the database' in output


def test_main_no_restaurants(monkeypatch, capsys):
    monkeypatch.setattr('app.orders.main.get_customer_ids', lambda _: ['1', '2'])
    monkeypatch.setattr('app.orders.main.get_delivery_ids', lambda _: [5, 6])

    main(['produce', '--count', '5'])
    output = capsys.readouterr().out
    assert 'There are no restaurants in the database' in output


def test_main_no_deliveries(monkeypatch, capsys):
    monkeypatch.setattr('app.orders.main.get_customer_ids', lambda _: ['1', '2'])
    monkeypatch.setattr('app.orders.main.get_restaurant_ids', lambda _: [3, 4])

    main(['produce', '--count', '5'])
    output = capsys.readouterr().out
    assert 'There are no deliveries in the database' in output


def test_main_convert_file_does_not_exist(capsys):
    with pytest.raises(SystemExit):
        main(['ingest', '--convert', 'nonexistent_file.csv', 'output.json'])

    output = capsys.readouterr().out
    assert 'nonexistent_file.csv does not exist.' in output


TEST_DATA_DIR = './tmp/test-items'


def test_main_convert_called_with_correct_arguments(monkeypatch, test_kwargs):
    monkeypatch.setattr('app.orders.producer.OrderProducer.convert_files', test_kwargs)
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    test_file = f"{TEST_DATA_DIR}/users-test.csv"
    with open(test_file, 'w') as f:
        pass

    main(['ingest', '--convert', test_file, 'output.json'])
    assert test_kwargs.args == {'in_file': test_file, 'out_file': 'output.json'}

    shutil.rmtree(TEST_DATA_DIR)


def test_main_ingest_files_do_not_exist(capsys):
    with pytest.raises(SystemExit):
        main(['ingest', '--csv', 'nonexistent_file.csv'])

    output = capsys.readouterr().out
    assert 'nonexistent_file.csv does not exist.' in output

    with pytest.raises(SystemExit):
        main(['ingest', '--json', 'nonexistent_file.json'])

    output = capsys.readouterr().out
    assert 'nonexistent_file.json does not exist.' in output

    with pytest.raises(SystemExit):
        main(['ingest', '--xml', 'nonexistent_file.xml'])

    output = capsys.readouterr().out
    assert 'nonexistent_file.xml does not exist.' in output