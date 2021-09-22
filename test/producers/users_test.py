import os
import re
import uuid
import pytest
import shutil

from pathlib import Path
from app.db.config import Config
from app.db.database import Database
from app.producers.users import main
from app.producers.users import User
from app.producers.users import UserGenerator
from app.producers.users import UsersProducer
from app.producers.users import UsersArgParser


def test_user_arg_parser():
    parser = UsersArgParser(['--csv', 'file.csv', '--custs', '1', '--admins', '2',
                             '--emps', '3', '--drivers', '4'])
    args = parser.args
    assert args.csv == 'file.csv'
    assert args.custs == 1
    assert args.admins == 2
    assert args.emps == 3
    assert args.drivers == 4


def _assert_user_defaults(user: User):
    assert user.enabled
    assert user.confirmed
    assert user.account_non_expired
    assert user.account_non_locked
    assert user.credentials_non_expired


def test_user_properties_default_values():
    user_id = uuid.uuid4()
    user_role = User.Role.EMPLOYEE
    password = 'secret'
    email = 'me@email.com'

    user = User(user_id=user_id, user_role=user_role, password=password, email=email)
    _assert_user_defaults(user)


def test_user_properties_by_name():
    user_id = uuid.uuid4()
    user_role = User.Role.EMPLOYEE
    password = 'secret'
    email = 'me@email.com'
    enabled = False

    user = User(user_id=user_id, user_role=user_role, password=password, email=email, enabled=enabled)
    assert user.user_id == user_id
    assert user.user_role == user_role
    assert user.password == password
    assert user.email == email

    user = User(user_id=user_id, user_role=user_role, password=password, email=email, enabled=False)
    assert not user.enabled

    user = User(user_id=user_id, user_role=user_role, password=password, email=email, confirmed=False)
    assert not user.confirmed

    user = User(user_id=user_id, user_role=user_role, password=password, email=email, account_non_expired=False)
    assert not user.account_non_expired

    user = User(user_id=user_id, user_role=user_role, password=password, email=email, account_non_locked=False)
    assert not user.account_non_locked

    user = User(user_id=user_id, user_role=user_role, password=password, email=email, credentials_non_expired=False)
    assert not user.credentials_non_expired


def _assert_password_len(password: str):
    assert len(password) == 60


def test_user_generator_password():
    # hash result is 60 characters
    password = UserGenerator.generate_password(10)
    _assert_password_len(password)
    password = UserGenerator.generate_password(20)
    _assert_password_len(password)


def _assert_is_email(email: str):
    assert '@' in email
    parts = email.split('@')
    assert re.match('^[a-z0-9]+$', parts[0])
    assert re.match('^[a-z]+\\.(com|net|org|gov)$', parts[1])


def test_user_generator_email():
    email = UserGenerator.generate_email(20, 25)
    _assert_is_email(email)


def test_user_generator_user():
    user = UserGenerator.generate_user(User.Role.ADMIN)
    assert isinstance(user.user_id, uuid.UUID)
    assert len(user.user_id.bytes) == len(uuid.uuid4().bytes)
    assert user.user_role == User.Role.ADMIN
    _assert_password_len(user.password)
    _assert_is_email(user.email)
    _assert_user_defaults(user)


db = Database(Config())


def delete_users():
    db.open_connection()
    with db.conn as conn:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM `user`')
    db.conn = None


def _assert_user_properties_from_result(user: User, result):
    assert result[0].lower() == user.user_id.hex
    assert result[1] == user.user_role
    assert result[2] == user.password
    assert result[3] == user.email
    assert result[4] == user.enabled
    assert result[5] == user.confirmed
    assert result[6] == user.account_non_expired
    assert result[7] == user.account_non_locked
    assert result[8] == user.credentials_non_expired


def test_user_producer_save_user():
    delete_users()
    producer = UsersProducer(db)
    user = UserGenerator.generate_user(User.Role.ADMIN)
    producer.save_user(user)

    db.open_connection()
    with db.conn as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT HEX(id),user_role,password,email,enabled,confirmed,account_non_expired,'
                           'account_non_locked,credentials_non_expired FROM user WHERE id = UNHEX(?)',
                           (user.user_id.hex,))
            result = cursor.fetchone()
    db.conn = None

    _assert_user_properties_from_result(user, result)

    delete_users()


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
    delete_users()
    monkeypatch.setattr('builtins.input', lambda _: 'y')

    producer = UsersProducer(db)
    producer.produce_random(num_custs=1, num_drivers=2, num_admins=3, num_emps=4)

    results = db.run_query('SELECT id,user_role FROM `user`')
    assert len(results) == 10
    _assert_num_users_by_role(results, num_custs=1, num_drivers=2, num_admins=3, num_emps=4)

    delete_users()


def test_user_producer_produce_random_no_continue(capsys, monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'n')

    producer = UsersProducer(db)
    with pytest.raises(SystemExit):
        producer.produce_random(num_custs=1, num_drivers=2, num_admins=3, num_emps=4)

    captured = capsys.readouterr()
    last_line = captured.out.split(os.linesep)[-2]
    assert last_line == 'No records will be inserted.'


def _create_csv_file(csv_file: str, custs: int = 0, drivers: int = 0, admins: int = 0, emps: int = 0):
    users = []

    def create_users(count: int, role: str):
        for _ in range(count):
            users.append(UserGenerator.generate_user(role))

    create_users(custs, User.Role.CUSTOMER)
    create_users(drivers, User.Role.DRIVER)
    create_users(admins, User.Role.ADMIN)
    create_users(emps, User.Role.EMPLOYEE)

    with open(csv_file, 'w') as f:
        for user in users:
            f.write(f"{user.user_id.hex},{user.user_role},{user.password.replace(',', '!')},{user.email},"
                    f"{user.enabled},{user.confirmed},{user.account_non_expired},{user.account_non_locked},"
                    f"{user.credentials_non_expired}{os.linesep}")


def _read_csv_file(csv_file: str) -> list[User]:
    users = []
    with open(csv_file) as f:
        for line in f:
            if not line.strip():
                continue
            fields = line.strip().split(',')
            user = User(user_id=uuid.UUID(fields[0]),
                        user_role=fields[1],
                        password=fields[2],
                        email=fields[3],
                        enabled=bool(fields[4]),
                        confirmed=bool(fields[5]),
                        account_non_expired=bool(fields[6]),
                        account_non_locked=bool(fields[7]),
                        credentials_non_expired=bool(fields[8]))
            users.append(user)
    return users


TEST_CSV_DIR = './tmp/test-users'


def test_user_producer_producer_from_csv_correct_fields(monkeypatch):
    delete_users()
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    Path(TEST_CSV_DIR).mkdir(parents=True, exist_ok=True)
    _create_csv_file(f"{TEST_CSV_DIR}/users-test.csv", custs=1)

    producer = UsersProducer(db)
    producer.produce_from_csv(f"{TEST_CSV_DIR}/users-test.csv")

    user = _read_csv_file(f"{TEST_CSV_DIR}/users-test.csv")[0]
    result = db.run_query('SELECT HEX(id),user_role,password,email,enabled,confirmed,account_non_expired,'
                          'account_non_locked,credentials_non_expired FROM `user`')[0]

    _assert_user_properties_from_result(user, result)

    shutil.rmtree(TEST_CSV_DIR)
    delete_users()


def test_user_producer_producer_from_csv_multiple(monkeypatch):
    delete_users()
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    Path(TEST_CSV_DIR).mkdir(parents=True, exist_ok=True)
    _create_csv_file(f"{TEST_CSV_DIR}/users-test.csv", custs=1, drivers=2, admins=3, emps=4)

    producer = UsersProducer(db)
    producer.produce_from_csv(f"{TEST_CSV_DIR}/users-test.csv")

    results = db.run_query('SELECT HEX(id),user_role FROM `user`')
    _assert_num_users_by_role(results, num_custs=1, num_drivers=2, num_admins=3, num_emps=4)

    shutil.rmtree(TEST_CSV_DIR)
    delete_users()


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
