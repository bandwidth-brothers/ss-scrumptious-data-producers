import re
import uuid

from app.users.model import User
from app.users.generator import UserGenerator
from test.users.common import _assert_user_defaults


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
    assert isinstance(user.id, uuid.UUID)
    assert len(user.id.bytes) == len(uuid.uuid4().bytes)
    assert user.user_role == User.Role.ADMIN
    _assert_password_len(user.password)
    _assert_is_email(user.email)
    _assert_user_defaults(user)