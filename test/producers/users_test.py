import os
import re
import uuid
import json
import pytest
import shutil
import xml.etree.ElementTree as ET

from pathlib import Path
from app.db.config import Config
from app.db.database import Database
from app.producers.users import main
from app.producers.users import User
from app.producers.users import UserFormatter
from app.producers.users import UserGenerator
from app.producers.users import UsersProducer
from app.producers.users import UsersArgParser
from app.producers.helpers import string_to_bool


def test_user_arg_parser():
    parser = UsersArgParser(['--csv', 'file.csv', '--json', 'file.json', '--xml', 'file.xml',
                             '--csv-format', '--json-format', '--xml-format', '--convert', 'file.csv', 'file.json',
                             '--custs', '1', '--admins', '2', '--emps', '3', '--drivers', '4',
                             '--short', '--pretty', '--limit', '5'])
    args = parser.args
    assert args.csv == 'file.csv'
    assert args.json == 'file.json'
    assert args.xml == 'file.xml'
    assert args.csv_format
    assert args.json_format
    assert args.xml_format
    assert args.convert == ['file.csv', 'file.json']
    assert args.custs == 1
    assert args.admins == 2
    assert args.emps == 3
    assert args.drivers == 4
    assert args.short
    assert args.pretty
    assert args.limit == 5


# def _assert_user_defaults(user: User):
#     assert user.enabled
#     assert user.confirmed
#     assert user.account_non_expired
#     assert user.account_non_locked
#     assert user.credentials_non_expired
#
#
# def test_user_properties_default_values():
#     user_id = uuid.uuid4()
#     user_role = User.Role.EMPLOYEE
#     password = 'secret'
#     email = 'me@email.com'
#
#     user = User(user_id=user_id, user_role=user_role, password=password, email=email)
#     _assert_user_defaults(user)
#
#
# def test_user_properties_by_name():
#     user_id = uuid.uuid4()
#     user_role = User.Role.EMPLOYEE
#     password = 'secret'
#     email = 'me@email.com'
#     enabled = False
#
#     user = User(user_id=user_id, user_role=user_role, password=password, email=email, enabled=enabled)
#     assert user.id == user_id
#     assert user.user_role == user_role
#     assert user.password == password
#     assert user.email == email
#
#     user = User(user_id=user_id, user_role=user_role, password=password, email=email, enabled=False)
#     assert not user.enabled
#
#     user = User(user_id=user_id, user_role=user_role, password=password, email=email, confirmed=False)
#     assert not user.confirmed
#
#     user = User(user_id=user_id, user_role=user_role, password=password, email=email, account_non_expired=False)
#     assert not user.account_non_expired
#
#     user = User(user_id=user_id, user_role=user_role, password=password, email=email, account_non_locked=False)
#     assert not user.account_non_locked
#
#     user = User(user_id=user_id, user_role=user_role, password=password, email=email, credentials_non_expired=False)
#     assert not user.credentials_non_expired


# def _assert_password_len(password: str):
#     assert len(password) == 60
#
#
# def test_user_generator_password():
#     # hash result is 60 characters
#     password = UserGenerator.generate_password(10)
#     _assert_password_len(password)
#     password = UserGenerator.generate_password(20)
#     _assert_password_len(password)
#
#
# def _assert_is_email(email: str):
#     assert '@' in email
#     parts = email.split('@')
#     assert re.match('^[a-z0-9]+$', parts[0])
#     assert re.match('^[a-z]+\\.(com|net|org|gov)$', parts[1])
#
#
# def test_user_generator_email():
#     email = UserGenerator.generate_email(20, 25)
#     _assert_is_email(email)
#
#
# def test_user_generator_user():
#     user = UserGenerator.generate_user(User.Role.ADMIN)
#     assert isinstance(user.id, uuid.UUID)
#     assert len(user.id.bytes) == len(uuid.uuid4().bytes)
#     assert user.user_role == User.Role.ADMIN
#     _assert_password_len(user.password)
#     _assert_is_email(user.email)
#     _assert_user_defaults(user)


# def _assert_user_properties_in_formatted_string(formatted_string: str):
#     assert 'id' in formatted_string
#     assert 'user_role' in formatted_string
#     assert 'password' in formatted_string
#     assert 'email' in formatted_string
#     assert 'enabled' in formatted_string
#     assert 'confirmed' in formatted_string
#     assert 'account_non_expired' in formatted_string
#     assert 'account_non_locked' in formatted_string
#     assert 'credentials_non_expired' in formatted_string
#
#
# def test_user_formatter_pretty():
#     user = UserGenerator.generate_user(User.Role.ADMIN)
#     pretty_str = UserFormatter.pretty(user)
#
#     _assert_user_properties_in_formatted_string(pretty_str)
#
#
# def test_user_formatter_to_json():
#     users = [UserGenerator.generate_user(User.Role.ADMIN)]
#     json_str = UserFormatter.to_json(users)
#
#     _assert_user_properties_in_formatted_string(json_str)
#
#
# def test_user_formatter_from_json():
#     class UUIDEncoder(json.JSONEncoder):
#         def default(self, obj):
#             if isinstance(obj, uuid.UUID):
#                 return obj.hex
#             return json.JSONEncoder.default(self, obj)
#
#     user = UserGenerator.generate_user(User.Role.EMPLOYEE)
#     json_str = json.dumps([user.__dict__], cls=UUIDEncoder)
#     users = UserFormatter.from_json(json_str)
#
#     assert len(users) == 1
#     u = users[0]
#
#     assert user.id == u.id
#     assert user.user_role == u.user_role
#     assert user.password == u.password
#     assert user.email == u.email
#     assert user.enabled == u.enabled
#     assert user.confirmed == u.confirmed
#     assert user.account_non_expired == u.account_non_expired
#     assert user.account_non_locked == u.account_non_locked
#     assert user.credentials_non_expired == u.credentials_non_expired
#
#
# def test_user_formatter_from_json_missing_property():
#     json_str = '''
#     [
#         {
#             "id": "698bb0dd-ef09-4f47-adf0-0cfa08a485bb",
#             "user_role": "ROLE_CUSTOMER"
#         }
#     ]
#     '''
#     with pytest.raises(KeyError) as ex:
#         UserFormatter.from_json(json_str)
#
#     assert 'password' in str(ex)
#
#
# def test_user_formatter_from_csv():
#     csv_str = "698bb0dd-ef09-4f47-adf0-0cfa08a485bb,ROLE_CUSTOMER," \
#               "$2a$10$9Kc914m7c1yQ2iP6mzmz3.rjKsJhjA.fQL83rIM86ehmUrfl3lXXa," \
#               "u5acm8rlmnif@yahoo.org,True,False,True,False,True"
#     users = UserFormatter.from_csv(csv_str)
#
#     assert len(users) == 1
#     user = users[0]
#
#     assert str(user.id) == "698bb0dd-ef09-4f47-adf0-0cfa08a485bb"
#     assert user.user_role == "ROLE_CUSTOMER"
#     assert user.password == "$2a$10$9Kc914m7c1yQ2iP6mzmz3.rjKsJhjA.fQL83rIM86ehmUrfl3lXXa"
#     assert user.email == "u5acm8rlmnif@yahoo.org"
#     assert user.enabled is True
#     assert user.confirmed is False
#     assert user.account_non_expired is True
#     assert user.account_non_locked is False
#     assert user.credentials_non_expired is True
#
#
# def test_user_formatter_from_csv_wrong_row_size():
#     csv_str = "698bb0dd-ef09-4f47-adf0-0cfa08a485bb,ROLE_CUSTOMER," \
#               "$2a$10$9Kc914m7c1yQ2iP6mzmz3.rjKsJhjA.fQL83rIM86ehmUrfl3lXXa," \
#               "u5acm8rlmnif@yahoo.org,True,False,True"
#
#     with pytest.raises(IndexError) as ex:
#         UserFormatter.from_csv(csv_str)
#
#     assert 'not enough fields' in str(ex)
#
#
# def test_user_formatter_to_csv():
#     user = UserGenerator.generate_user(User.Role.CUSTOMER)
#     user.confirmed = False
#     user.account_non_locked = False
#
#     csv_str = UserFormatter.to_csv([user])
#     fields = csv_str.split(',')
#
#     assert fields[0] == str(user.id)
#     assert fields[1] == user.user_role
#     assert fields[2] == user.password
#     assert fields[3] == user.email
#     assert string_to_bool(fields[4]) == user.enabled
#     assert string_to_bool(fields[5]) == user.confirmed
#     assert string_to_bool(fields[6]) == user.account_non_expired
#     assert string_to_bool(fields[7]) == user.account_non_locked
#     assert string_to_bool(fields[8]) == user.credentials_non_expired
#
#
# def test_user_formatter_to_xml():
#     user = UserGenerator.generate_user(User.Role.ADMIN)
#     xml_str = UserFormatter.to_xml([user])
#
#     root = ET.fromstring(xml_str)
#     nodes = root.findall('./user')
#
#     assert len(nodes) == 1
#
#     node = nodes[0]
#     assert node.find('id').text == str(user.id)
#     assert node.find('user_role').text == user.user_role
#     assert node.find('password').text == user.password
#     assert node.find('email').text == user.email
#     assert node.find('enabled').text == str(user.enabled)
#     assert node.find('confirmed').text == str(user.confirmed)
#     assert node.find('account_non_expired').text == str(user.account_non_expired)
#     assert node.find('account_non_locked').text == str(user.account_non_locked)
#     assert node.find('credentials_non_expired').text == str(user.credentials_non_expired)
#
#
# def test_user_formatter_from_xml():
#     xml_str = """<?xml version="1.0" ?>
# <users>
#     <user>
#         <id>698bb0dd-ef09-4f47-adf0-0cfa08a485bb</id>
#         <user_role>ROLE_ADMIN</user_role>
#         <password>$2a$10$9Kc914m7c1yQ2iP6mzmz3.rjKsJhjA.fQL83rIM86ehmUrfl3lXXa</password>
#         <email>u5acm8rlmnif@yahoo.org</email>
#         <enabled>True</enabled>
#         <confirmed>False</confirmed>
#         <account_non_expired>True</account_non_expired>
#         <account_non_locked>False</account_non_locked>
#         <credentials_non_expired>True</credentials_non_expired>
#     </user>
# </users>
#     """
#     users = UserFormatter.from_xml(xml_str)
#     assert len(users) == 1
#
#     user = users[0]
#     assert str(user.id) == '698bb0dd-ef09-4f47-adf0-0cfa08a485bb'
#     assert user.user_role == 'ROLE_ADMIN'
#     assert user.password == '$2a$10$9Kc914m7c1yQ2iP6mzmz3.rjKsJhjA.fQL83rIM86ehmUrfl3lXXa'
#     assert user.email == 'u5acm8rlmnif@yahoo.org'
#     assert user.enabled is True
#     assert user.confirmed is False
#     assert user.account_non_expired is True
#     assert user.account_non_locked is False
#     assert user.credentials_non_expired is True
#
#
# def test_user_formatter_from_xml_missing_property():
#     xml_str = """<?xml version="1.0" ?>
# <users>
#     <user>
#         <id>698bb0dd-ef09-4f47-adf0-0cfa08a485bb</id>
#     </user>
# </users>
#         """
#     with pytest.raises(KeyError) as ex:
#         UserFormatter.from_xml(xml_str)
#
#     assert 'user_role' in str(ex)


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
        f.write(UserFormatter.to_csv(users))


def _read_csv_file(csv_file: str) -> list[User]:
    users = []
    with open(csv_file) as f:
        users += UserFormatter.from_csv(f.read())
    return users


TEST_DATA_DIR = './tmp/test-users'


def test_user_producer_produce_from_csv_correct_fields(monkeypatch):
    _delete_users()
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_csv_file(f"{TEST_DATA_DIR}/users-test.csv", custs=1)

    producer = UsersProducer(db)
    producer.produce_from_csv(f"{TEST_DATA_DIR}/users-test.csv")

    user = _read_csv_file(f"{TEST_DATA_DIR}/users-test.csv")[0]
    result = db.run_query('SELECT HEX(id),user_role,password,email,enabled,confirmed,account_non_expired,'
                          'account_non_locked,credentials_non_expired FROM `user`')[0]
    _assert_user_properties_from_result(user, result)

    shutil.rmtree(TEST_DATA_DIR)
    _delete_users()


def test_user_producer_produce_from_csv_multiple(monkeypatch):
    _delete_users()
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_csv_file(f"{TEST_DATA_DIR}/users-test.csv", custs=1, drivers=2, admins=3, emps=4)

    producer = UsersProducer(db)
    producer.produce_from_csv(f"{TEST_DATA_DIR}/users-test.csv")

    results = db.run_query('SELECT HEX(id),user_role FROM `user`')
    _assert_num_users_by_role(results, num_custs=1, num_drivers=2, num_admins=3, num_emps=4)

    shutil.rmtree(TEST_DATA_DIR)
    _delete_users()


def _create_json_file(json_file: str, custs: int = 0, drivers: int = 0, admins: int = 0, emps: int = 0):
    users = _generate_test_users(custs, drivers, admins, emps)
    with open(json_file, 'w') as f:
        f.write(UserFormatter.to_json(users))


def _read_json_file(json_file: str) -> list[User]:
    users = []
    with open(json_file) as f:
        users += UserFormatter.from_json(f.read())
    return users


def test_user_producer_produce_from_json_correct_fields(monkeypatch):
    _delete_users()
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_json_file(f"{TEST_DATA_DIR}/users-test.json", custs=1)

    producer = UsersProducer(db)
    producer.produce_from_json(f"{TEST_DATA_DIR}/users-test.json")

    user = _read_json_file(f"{TEST_DATA_DIR}/users-test.json")[0]
    result = db.run_query('SELECT HEX(id),user_role,password,email,enabled,confirmed,account_non_expired,'
                          'account_non_locked,credentials_non_expired FROM `user`')[0]
    _assert_user_properties_from_result(user, result)

    shutil.rmtree(TEST_DATA_DIR)
    _delete_users()


def test_user_producer_produce_from_json_multiple(monkeypatch):
    _delete_users()
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_json_file(f"{TEST_DATA_DIR}/users-test.json", custs=1, drivers=2, admins=3, emps=4)

    producer = UsersProducer(db)
    producer.produce_from_json(f"{TEST_DATA_DIR}/users-test.json")

    results = db.run_query('SELECT HEX(id),user_role FROM `user`')
    _assert_num_users_by_role(results, num_custs=1, num_drivers=2, num_admins=3, num_emps=4)

    shutil.rmtree(TEST_DATA_DIR)
    _delete_users()


def test_user_producer_produce_from_json_missing_field(capsys):
    producer = UsersProducer(Database(Config()))
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
    with open(f"{TEST_DATA_DIR}/users-test.json", 'w') as f:
        f.write(json.dumps(data))

    with pytest.raises(SystemExit):
        producer.produce_from_json(f"{TEST_DATA_DIR}/users-test.json")

    captured = capsys.readouterr()
    output = captured.out
    assert "User missing 'account_non_locked'" in output

    shutil.rmtree(TEST_DATA_DIR)


def test_user_producer_produce_from_json_bad_format(capsys):
    json_str = '{"bad":json}'
    producer = UsersProducer(Database(Config()))

    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    with open(f"{TEST_DATA_DIR}/users-test.json", 'w') as f:
        f.write(json_str)

    with pytest.raises(SystemExit):
        producer.produce_from_json(f"{TEST_DATA_DIR}/users-test.json")

    captured = capsys.readouterr()
    output = captured.out
    assert "JSON is not valid format" in output

    shutil.rmtree(TEST_DATA_DIR)


def _create_xml_file(xml_file: str, custs: int = 0, drivers: int = 0, admins: int = 0, emps: int = 0):
    users = _generate_test_users(custs, drivers, admins, emps)
    with open(xml_file, 'w') as f:
        f.write(UserFormatter.to_xml(users))


def _read_xml_file(xml_file: str):
    users = []
    with open(xml_file) as f:
        users += UserFormatter.from_xml(f.read())
    return users


def test_user_producer_produce_from_xml(monkeypatch):
    _delete_users()
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_xml_file(f"{TEST_DATA_DIR}/users-test.xml", custs=1)

    producer = UsersProducer(db)
    producer.produce_from_xml(f"{TEST_DATA_DIR}/users-test.xml")

    user = _read_xml_file(f"{TEST_DATA_DIR}/users-test.xml")[0]
    result = db.run_query('SELECT HEX(id),user_role,password,email,enabled,confirmed,account_non_expired,'
                          'account_non_locked,credentials_non_expired FROM `user`')[0]
    _assert_user_properties_from_result(user, result)

    shutil.rmtree(TEST_DATA_DIR)
    _delete_users()


def test_user_producer_produce_from_xml_multiple(monkeypatch):
    _delete_users()
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_xml_file(f"{TEST_DATA_DIR}/users-test.xml", custs=1, drivers=2, admins=3, emps=4)

    producer = UsersProducer(db)
    producer.produce_from_xml(f"{TEST_DATA_DIR}/users-test.xml")

    results = db.run_query('SELECT HEX(id),user_role FROM `user`')
    _assert_num_users_by_role(results, num_custs=1, num_drivers=2, num_admins=3, num_emps=4)

    shutil.rmtree(TEST_DATA_DIR)
    _delete_users()


def test_user_producer_produce_from_xml_bad_format(capsys):
    xml_str = '<users><user><id>98bb0dd-ef09-4f47-adf0-0cfa08a485bb</id></user></users'
    producer = UsersProducer(Database(Config()))

    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    with open(f"{TEST_DATA_DIR}/users-test.xml", 'w') as f:
        f.write(xml_str)

    with pytest.raises(SystemExit):
        producer.produce_from_xml(f"{TEST_DATA_DIR}/users-test.xml")

    captured = capsys.readouterr()
    output = captured.out
    assert "Malformed XML" in output

    shutil.rmtree(TEST_DATA_DIR)


def test_user_producer_convert_unsupported_format(capsys):
    producer = UsersProducer(Database(Config()))

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
    producer = UsersProducer(Database(Config()))
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    _create_json_file(f"{TEST_DATA_DIR}/users-test.json", custs=1)

    producer.convert_files(f"{TEST_DATA_DIR}/users-test.json", f"{TEST_DATA_DIR}/users-test.csv")

    user = _read_csv_file(f"{TEST_DATA_DIR}/users-test.csv")[0]

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


def test_main_csv_file_doesnt_exist(capsys):
    main(['--csv', 'nonexistent_file.csv'])
    output = capsys.readouterr().out
    assert 'nonexistent_file.csv does not exist.' in output


@pytest.fixture
def test_kwargs():
    class TestKwargs(object):
        def __call__(self, **kwargs):
            self.args = kwargs
    return TestKwargs()


def test_main_produce_random_called_with_correct_arguments(monkeypatch, test_kwargs):
    monkeypatch.setattr('app.producers.users.UsersProducer.produce_random', test_kwargs)
    main(['--custs', '1', '--drivers', '2', '--admins', '3', '--emps', '4'])
    assert test_kwargs.args == {'num_custs': 1, 'num_drivers':  2, 'num_admins': 3, 'num_emps': 4}
