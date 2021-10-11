import uuid

from app.users.model import User
from test.users.common import _assert_user_defaults


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
    assert user.id == user_id
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
