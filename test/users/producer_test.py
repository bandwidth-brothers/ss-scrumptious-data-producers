import os
import uuid
import json
import pytest
import shutil

from pathlib import Path
from app.db.config import Config
from app.db.database import Database
from app.users.model import User
from app.users.formatter import UserFormatter
from app.users.generator import UserGenerator
from app.users.producer import UsersProducer


db = Database(Config())


def _delete_users():
    db.open_connection()
    with db.conn as conn:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM `user`')
    db.conn = None


def _assert_user_properties_from_result(user: User, result):
    assert result[0].lower() == user.id.hex
    assert result[1] == user.user_role
    assert result[2] == user.password
    assert result[3] == user.email
    assert result[4] == user.enabled
    assert result[5] == user.confirmed
    assert result[6] == user.account_non_expired
    assert result[7] == user.account_non_locked
    assert result[8] == user.credentials_non_expired


def test_user_producer_save_user():
    _delete_users()
    producer = UsersProducer(db)
    user = UserGenerator.generate_user(User.Role.ADMIN)
    producer.save_user(user)

    db.open_connection()
    with db.conn as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT HEX(id),user_role,password,email,enabled,confirmed,account_non_expired,'
                           'account_non_locked,credentials_non_expired FROM user WHERE id = UNHEX(?)',
                           (user.id.hex,))
            result = cursor.fetchone()
    db.conn = None

    _assert_user_properties_from_result(user, result)

    _delete_users()


def _assert_num_users_by_role(db_results, num_custs: int, num_drivers: int, num_admins: int, num_emps: int):
    customers = list(filter(lambda result: result[1] == User.Role.CUSTOMER, db_results))
    assert len(customers) == num_custs
    drivers = list(filter(lambda result: result[1] == User.Role.DRIVER, db_results))
    assert len(drivers) == num_drivers
    admins = list(filter(lambda result: result[1] == User.Role.ADMIN, db_results))
    assert len(admins) == num_admins
    employees = list(filter(lambda result: result[1] == User.Role.EMPLOYEE, db_results))
    assert len(employees) == num_emps


def test_user_producer_produce_random(monkeypatch):
    _delete_users()
    monkeypatch.setattr('builtins.input', lambda _: 'y')

    producer = UsersProducer(db)
    producer.produce_random(num_custs=1, num_drivers=2, num_admins=3, num_emps=4)

    results = db.run_query('SELECT id,user_role FROM `user`')
    assert len(results) == 10
    _assert_num_users_by_role(results, num_custs=1, num_drivers=2, num_admins=3, num_emps=4)

    _delete_users()


def test_user_producer_produce_random_no_continue(capsys, monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'n')

    producer = UsersProducer(db)
    with pytest.raises(SystemExit):
        producer.produce_random(num_custs=1, num_drivers=2, num_admins=3, num_emps=4)

    captured = capsys.readouterr()
    last_line = captured.out.split(os.linesep)[-2]
    assert last_line == 'No records will be inserted.'


def _generate_test_users(custs: int = 0, drivers: int = 0, admins: int = 0, emps: int = 0):
    users = []

    def _create_users(count: int, role: str):
        for _ in range(count):
            users.append(UserGenerator.generate_user(role))

    _create_users(custs, User.Role.CUSTOMER)
    _create_users(drivers, User.Role.DRIVER)
    _create_users(admins, User.Role.ADMIN)
    _create_users(emps, User.Role.EMPLOYEE)
    return users


def _create_csv_file(csv_file: str, custs: int = 0, drivers: int = 0, admins: int = 0, emps: int = 0):
    users = _generate_test_users(custs, drivers, admins, emps)
    with open(csv_file, 'w') as f:
        f.write(UserFormatter().to_csv(users))


def _read_csv_file(csv_file: str) -> list[User]:
    users = []
    with open(csv_file) as f:
        users += UserFormatter().from_csv(f.read())
    return users


TEST_DATA_DIR = './tmp/test-users'
CSV_TEST_FILE = f"{TEST_DATA_DIR}/users-test.csv"
JSON_TEST_FILE = f"{TEST_DATA_DIR}/users-test.json"
XML_TEST_FILE = f"{TEST_DATA_DIR}/users-test.xml"


def test_user_producer_produce_from_csv_correct_fields(monkeypatch):
    _delete_users()
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_csv_file(CSV_TEST_FILE, custs=1)

    producer = UsersProducer(db)
    producer.produce_from_csv(CSV_TEST_FILE)

    user = _read_csv_file(CSV_TEST_FILE)[0]
    result = db.run_query('SELECT HEX(id),user_role,password,email,enabled,confirmed,account_non_expired,'
                          'account_non_locked,credentials_non_expired FROM `user`')[0]
    _assert_user_properties_from_result(user, result)

    shutil.rmtree(TEST_DATA_DIR)
    _delete_users()


def test_user_producer_produce_from_csv_multiple(monkeypatch):
    _delete_users()
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_csv_file(CSV_TEST_FILE, custs=1, drivers=2, admins=3, emps=4)

    producer = UsersProducer(db)
    producer.produce_from_csv(CSV_TEST_FILE)

    results = db.run_query('SELECT HEX(id),user_role FROM `user`')
    _assert_num_users_by_role(results, num_custs=1, num_drivers=2, num_admins=3, num_emps=4)

    shutil.rmtree(TEST_DATA_DIR)
    _delete_users()


def _create_json_file(json_file: str, custs: int = 0, drivers: int = 0, admins: int = 0, emps: int = 0):
    users = _generate_test_users(custs, drivers, admins, emps)
    with open(json_file, 'w') as f:
        f.write(UserFormatter().to_json(users))


def _read_json_file(json_file: str) -> list[User]:
    users = []
    with open(json_file) as f:
        users += UserFormatter().from_json(f.read())
    return users


def test_user_producer_produce_from_json_correct_fields(monkeypatch):
    _delete_users()
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_json_file(JSON_TEST_FILE, custs=1)

    producer = UsersProducer(db)
    producer.produce_from_json(JSON_TEST_FILE)

    user = _read_json_file(JSON_TEST_FILE)[0]
    result = db.run_query('SELECT HEX(id),user_role,password,email,enabled,confirmed,account_non_expired,'
                          'account_non_locked,credentials_non_expired FROM `user`')[0]
    _assert_user_properties_from_result(user, result)

    shutil.rmtree(TEST_DATA_DIR)
    _delete_users()


def test_user_producer_produce_from_json_multiple(monkeypatch):
    _delete_users()
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_json_file(JSON_TEST_FILE, custs=1, drivers=2, admins=3, emps=4)

    producer = UsersProducer(db)
    producer.produce_from_json(JSON_TEST_FILE)

    results = db.run_query('SELECT HEX(id),user_role FROM `user`')
    _assert_num_users_by_role(results, num_custs=1, num_drivers=2, num_admins=3, num_emps=4)

    shutil.rmtree(TEST_DATA_DIR)
    _delete_users()


def test_user_producer_produce_from_json_missing_field(capsys):
    producer = UsersProducer(db)
    data = {
        'id': str(uuid.uuid4()),
        'user_role': 'role',
        'password': 'secret',
        'email': 'me@me.com',
        'enabled': True,
        'confirmed': False,
        'account_non_expired': False,
        'credentials_non_expired': True
    }
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    with open(JSON_TEST_FILE, 'w') as f:
        f.write(json.dumps(data))

    with pytest.raises(SystemExit):
        producer.produce_from_json(JSON_TEST_FILE)

    captured = capsys.readouterr()
    output = captured.out
    assert "User missing 'account_non_locked'" in output

    shutil.rmtree(TEST_DATA_DIR)


def test_user_producer_produce_from_json_bad_format(capsys):
    json_str = '{"bad":json}'
    producer = UsersProducer(db)

    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    with open(JSON_TEST_FILE, 'w') as f:
        f.write(json_str)

    with pytest.raises(SystemExit):
        producer.produce_from_json(JSON_TEST_FILE)

    captured = capsys.readouterr()
    output = captured.out
    assert "JSON is not valid format" in output

    shutil.rmtree(TEST_DATA_DIR)


def _create_xml_file(xml_file: str, custs: int = 0, drivers: int = 0, admins: int = 0, emps: int = 0):
    users = _generate_test_users(custs, drivers, admins, emps)
    with open(xml_file, 'w') as f:
        f.write(UserFormatter().to_xml(users))


def _read_xml_file(xml_file: str):
    users = []
    with open(xml_file) as f:
        users += UserFormatter().from_xml(f.read())
    return users


def test_user_producer_produce_from_xml(monkeypatch):
    _delete_users()
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_xml_file(XML_TEST_FILE, custs=1)

    producer = UsersProducer(db)
    producer.produce_from_xml(XML_TEST_FILE)

    user = _read_xml_file(XML_TEST_FILE)[0]
    result = db.run_query('SELECT HEX(id),user_role,password,email,enabled,confirmed,account_non_expired,'
                          'account_non_locked,credentials_non_expired FROM `user`')[0]
    _assert_user_properties_from_result(user, result)

    shutil.rmtree(TEST_DATA_DIR)
    _delete_users()


def test_user_producer_produce_from_xml_multiple(monkeypatch):
    _delete_users()
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_xml_file(XML_TEST_FILE, custs=1, drivers=2, admins=3, emps=4)

    producer = UsersProducer(db)
    producer.produce_from_xml(XML_TEST_FILE)

    results = db.run_query('SELECT HEX(id),user_role FROM `user`')
    _assert_num_users_by_role(results, num_custs=1, num_drivers=2, num_admins=3, num_emps=4)

    shutil.rmtree(TEST_DATA_DIR)
    _delete_users()


def test_user_producer_produce_from_xml_bad_format(capsys):
    xml_str = '<users><user><id>98bb0dd-ef09-4f47-adf0-0cfa08a485bb</id></user></users'
    producer = UsersProducer(db)

    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    with open(XML_TEST_FILE, 'w') as f:
        f.write(xml_str)

    with pytest.raises(SystemExit):
        producer.produce_from_xml(XML_TEST_FILE)

    captured = capsys.readouterr()
    output = captured.out
    assert "Malformed XML" in output

    shutil.rmtree(TEST_DATA_DIR)


def test_user_producer_convert_unsupported_format(capsys):
    producer = UsersProducer(db)

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
    producer = UsersProducer(db)
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_json_file(JSON_TEST_FILE, custs=1)

    producer.convert_files(JSON_TEST_FILE, CSV_TEST_FILE)

    user = _read_csv_file(CSV_TEST_FILE)[0]

    assert user.id is not None
    assert user.user_role is not None
    assert user.password is not None
    assert user.email is not None
    assert user.enabled is True
    assert user.confirmed is True
    assert user.account_non_expired is True
    assert user.account_non_locked is True
    assert user.credentials_non_expired is True

    shutil.rmtree(TEST_DATA_DIR)
