from app.users.model import User


TEST_DATA_DIR = "./tmp/test-users"


def _assert_user_defaults(user: User):
    assert user.enabled
    assert user.confirmed
    assert user.account_non_expired
    assert user.account_non_locked
    assert user.credentials_non_expired
