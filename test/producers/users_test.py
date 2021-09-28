
import re
import uuid

from app.db.config import Config
from app.db.database import Database
from app.producers.users import User
from app.producers.users import UserGenerator
from app.producers.users import UsersProducer


def test_user_properties():
    user_id = uuid.uuid4()
    user_role = 'EMPLOYEE'
    username = 'scrumptious'
    password = 'secret'
    email = 'me@email.com'
    user = User(user_id, user_role, username, password, email)
    assert user.user_id == user_id
    assert user.user_role == user_role
    assert user.username == username
    assert user.password == password
    assert user.email == email


def test_user_generator_password():
    password = UserGenerator.generate_password(10)
    assert len(password) == 10


def test_user_generator_username():
    username = UserGenerator.generate_username(20, 25)
    assert len(username) >= 20
    assert len(username) <= 25
    assert username.islower() is True


def assert_is_email(email: str):
    assert '@' in email
    parts = email.split('@')
    assert re.match('^[a-z0-9]+$', parts[0])
    assert re.match('^[a-z]+\\.(com|net|org|gov)$', parts[1])


def test_user_generator_email():
    email = UserGenerator.generate_email(20, 25)
    assert_is_email(email)


def test_user_generator_user():
    user = UserGenerator.generate_user('ADMIN')
    assert len(user.user_id.bytes) == len(uuid.uuid4().bytes)
    assert user.user_role == 'ADMIN'
    assert user.username.islower() is True
    assert user.password is not None
    assert_is_email(user.email)


db = Database(Config())


def test_user_producer_save_user():
    producer = UsersProducer(db)
    user = UserGenerator.generate_user("ADMIN")
    producer.save_user(user)

    db.open_connection()
    with db.conn as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT userId,userRole,username,password,email FROM user WHERE userId = %s',
                           user.user_id.bytes)
            result = cursor.fetchone()
    db.conn = None

    assert result[0] == user.user_id.bytes
    assert result[1] == user.user_role
    assert result[2] == user.username
    assert result[3] == user.password
    assert result[4] == user.email

    db.open_connection()
    with db.conn as conn:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM user WHERE userId = %s', user.user_id.bytes)
        conn.commit()
    db.conn = None
