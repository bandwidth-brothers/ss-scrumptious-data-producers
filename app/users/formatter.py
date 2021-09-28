import uuid
import json
from typing import Type

from app.users.model import User
from app.common.formatter import AbstractFormatter
from app.common.converters import string_to_bool


class UserFormatter(AbstractFormatter[User]):

    class UserJsonDecoder(json.JSONDecoder):
        def __init__(self, *args, **kwargs):
            json.JSONDecoder.__init__(self, object_hook=UserFormatter.UserJsonDecoder._object_hook, *args, **kwargs)

        @classmethod
        def _object_hook(cls, dct):
            user_id = cls._get(dct, 'id')
            user_role = cls._get(dct, 'user_role')
            password = cls._get(dct, 'password')
            email = cls._get(dct, 'email')
            enabled = cls._get(dct, 'enabled')
            confirmed = cls._get(dct, 'confirmed')
            account_non_expired = cls._get(dct, 'account_non_expired')
            account_non_locked = cls._get(dct, 'account_non_locked')
            credentials_non_expired = cls._get(dct, 'credentials_non_expired')

            return User(user_id=uuid.UUID(user_id), user_role=user_role, password=password,
                        email=email, enabled=string_to_bool(enabled), confirmed=string_to_bool(confirmed),
                        account_non_expired=string_to_bool(account_non_expired),
                        account_non_locked=string_to_bool(account_non_locked),
                        credentials_non_expired=string_to_bool(credentials_non_expired))

        @classmethod
        def _get(cls, dct, prop):
            return AbstractFormatter.get_attr_or_throw(dct, prop)

    class UserJsonEncoder(json.JSONEncoder):
        def default(self, obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            else:
                return str(obj)

    def get_json_encoder(self) -> Type[UserJsonEncoder]:
        return UserFormatter.UserJsonEncoder

    def get_json_decoder(self) -> Type[UserJsonDecoder]:
        return UserFormatter.UserJsonDecoder

    def get_attr_list(self):
        return ['id', 'user_role', 'password', 'email', 'enabled', 'confirmed',
                'account_non_expired', 'account_non_locked', 'credentials_non_expired']

    def get_object_type(self) -> Type[User]:
        return User

    def create_object_from_string_fields(self, fields: list[str]) -> User:
        return User(user_id=uuid.UUID(fields[0]),
                    user_role=fields[1],
                    password=fields[2],
                    email=fields[3],
                    enabled=string_to_bool(fields[4]),
                    confirmed=string_to_bool(fields[5]),
                    account_non_expired=string_to_bool(fields[6]),
                    account_non_locked=string_to_bool(fields[7]),
                    credentials_non_expired=string_to_bool(fields[8]))

    def create_object_from_string_dict(self, _dict: dict) -> User:
        return User(user_id=uuid.UUID(_dict['id']),
                    user_role=_dict['user_role'],
                    password=_dict['password'],
                    email=_dict['email'],
                    enabled=string_to_bool(_dict['enabled']),
                    confirmed=string_to_bool(_dict['confirmed']),
                    account_non_expired=string_to_bool(_dict['account_non_expired']),
                    account_non_locked=string_to_bool(_dict['account_non_locked']),
                    credentials_non_expired=string_to_bool(_dict['credentials_non_expired']))
