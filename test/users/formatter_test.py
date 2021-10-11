import json

from app.users.model import User
from app.users.formatter import UserFormatter


def test_user_formatter_create_object_from_string_fields():
    fields = ["698bb0dd-ef09-4f47-adf0-0cfa08a485bb", User.Role.ADMIN,
              'p@ssw0rd', 'me@m.com', 'True', 'false', 'true', 'False', 'True']
    user = UserFormatter().create_object_from_string_fields(fields)

    assert str(user.id) == "698bb0dd-ef09-4f47-adf0-0cfa08a485bb"
    assert user.user_role == User.Role.ADMIN
    assert user.password == 'p@ssw0rd'
    assert user.email == 'me@m.com'
    assert user.enabled is True
    assert user.confirmed is False
    assert user.account_non_expired is True
    assert user.account_non_locked is False
    assert user.credentials_non_expired is True


def test_user_formatter_create_object_from_string_dict():
    _dict = {'id': "698bb0dd-ef09-4f47-adf0-0cfa08a485bb",
             'user_role': User.Role.ADMIN,
             'password': 'p@ssw0rd',
             'email': 'me@me.com',
             'enabled': 'True',
             'confirmed': 'False',
             'account_non_expired': 'True',
             'account_non_locked': 'False',
             'credentials_non_expired': 'True'}
    user = UserFormatter().create_object_from_string_dict(_dict)

    assert str(user.id) == '698bb0dd-ef09-4f47-adf0-0cfa08a485bb'
    assert user.user_role == User.Role.ADMIN
    assert user.password == 'p@ssw0rd'
    assert user.email == 'me@me.com'
    assert user.enabled is True
    assert user.confirmed is False
    assert user.account_non_expired is True
    assert user.account_non_locked is False
    assert user.credentials_non_expired is True


def test_user_formatter_json_decoder():
    json_str = """
    [
        {
            "id": "698bb0dd-ef09-4f47-adf0-0cfa08a485bb",
            "user_role": "ROLE_ADMIN",
            "password": "p@ssw0rd",
            "email": "me@me.com",
            "enabled": true,
            "confirmed": false,
            "account_non_expired": true,
            "account_non_locked": false,
            "credentials_non_expired": true
        }
    ]
    """
    user = json.loads(json_str, cls=UserFormatter.UserJsonDecoder)[0]

    assert str(user.id) == "698bb0dd-ef09-4f47-adf0-0cfa08a485bb"
    assert user.user_role == User.Role.ADMIN
    assert user.password == 'p@ssw0rd'
    assert user.email == 'me@me.com'
    assert user.enabled is True
    assert user.confirmed is False
    assert user.account_non_expired is True
    assert user.account_non_locked is False
    assert user.credentials_non_expired is True


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
#     <users>
#         <user>
#             <id>698bb0dd-ef09-4f47-adf0-0cfa08a485bb</id>
#             <user_role>ROLE_ADMIN</user_role>
#             <password>$2a$10$9Kc914m7c1yQ2iP6mzmz3.rjKsJhjA.fQL83rIM86ehmUrfl3lXXa</password>
#             <email>u5acm8rlmnif@yahoo.org</email>
#             <enabled>True</enabled>
#             <confirmed>False</confirmed>
#             <account_non_expired>True</account_non_expired>
#             <account_non_locked>False</account_non_locked>
#             <credentials_non_expired>True</credentials_non_expired>
#         </user>
#     </users>
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
