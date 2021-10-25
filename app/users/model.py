import uuid


class User:

    def __init__(self, user_id: uuid.UUID, user_role: str, password: str, email: str, enabled: bool = True,
                 confirmed: bool = True, account_non_expired: bool = True, account_non_locked: bool = True,
                 credentials_non_expired: bool = True):
        self.id = user_id
        self.user_role = user_role
        self.password = password
        self.email = email
        self.enabled = enabled
        self.confirmed = confirmed
        self.account_non_expired = account_non_expired
        self.account_non_locked = account_non_locked
        self.credentials_non_expired = credentials_non_expired

    def __str__(self):
        def _trunc(val: str, length: int):
            return val[0: length] + "..."
        return f"id: {_trunc(str(self.id), 12)}, role: {self.user_role}, password: {_trunc(self.password, 16)}, " \
               f"email: {self.email}, enabled: {self.enabled}, confirmed: {self.confirmed}, " \
               f"acct_expired: {self.account_non_expired}, acct_locked: {self.account_non_locked}, " \
               f"cred_expired: {self.credentials_non_expired}"

    class Role:
        ADMIN = 'ROLE_ADMIN'
        DRIVER = 'ROLE_DRIVER'
        EMPLOYEE = 'ROLE_EMPLOYEE'
        CUSTOMER = 'ROLE_CUSTOMER'
