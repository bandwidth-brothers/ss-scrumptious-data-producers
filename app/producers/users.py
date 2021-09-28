
import os
import sys
import uuid
import json
import bcrypt
import string
import random
import argparse
import jaydebeapi
import logging as log
import xml.etree
import xml.etree.ElementTree as ET

from xml.dom import minidom
from argparse import RawTextHelpFormatter
from app.db.config import Config
from app.db.database import Database
from app.producers.helpers import string_to_bool
from app.producers.helpers import print_items_and_confirm


class UsersArgParser:
    def __init__(self, args):
        self.parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                              description="""Generate user data in MySQL database.
A CSV, JSON, or XML file with a dataset may be provided as an argument using the
--csv, --json, or --xml option, respectively. When either of these arguments are
provided, others will be ignored.

examples:

    python -m app.producers.users --csv users.csv
    python -m app.producers.users --json users.json
    python -m app.producers.users --xml users.xml
    python -m app.producers.users --convert users.csv users.json
    python -m app.producers.users --custs 20 --admins 2 --emps 5 --drivers 5
    python -m app.producers.users --custs 20 --pretty --limit 5
    python -m app.producers.users --admins 2""")
        self.parser.add_argument('--csv', type=str, help='a CSV file with user data.')
        self.parser.add_argument('--csv-format', action='store_true', help='show CSV format')
        self.parser.add_argument('--json', type=str, help='a JSON file with user data.')
        self.parser.add_argument('--json-format', action='store_true', help='show the JSON format')
        self.parser.add_argument('--xml', type=str, help='an XML file with user data.')
        self.parser.add_argument('--xml-format', action='store_true', help='show the XML format')
        self.parser.add_argument('--convert', nargs=2, metavar=('FROM', 'TO'), type=str,
                                 help='convert one file format to another.')
        self.parser.add_argument('--custs', type=int, help='number of customers to generate')
        self.parser.add_argument('--admins', type=int, help='number of admins to generate')
        self.parser.add_argument('--emps', type=int, help='number of employees to generate')
        self.parser.add_argument('--drivers', type=int, help='number of drivers to generate')
        self.parser.add_argument('--short', action='store_true', help='print short output for users')
        self.parser.add_argument('--pretty', action='store_true', help='print pretty output for users')
        self.parser.add_argument('--limit', type=int, help='limit the user creation output. default 10', default=10)
        self.args = self.parser.parse_args(args)


class User:
    def __init__(self, user_id: uuid.UUID, user_role: str, password: str, email: str, enabled: bool = True,
                 confirmed: bool = True, account_non_expired: bool = True, account_non_locked: bool = True,
                 credentials_non_expired: bool = True):
        self.id = user_id
        self.password = password
        self.email = email
        self.user_role = user_role
        self.enabled = enabled
        self.confirmed = confirmed
        self.account_non_expired = account_non_expired
        self.account_non_locked = account_non_locked
        self.credentials_non_expired = credentials_non_expired

    def __str__(self):
        def _trunc(val: str, length: int):
            return val[0: length] + "..."
        return f"id: {_trunc(str(self.id), 12)}, role: {self.user_role}, passwd: {_trunc(self.password, 16)}, " \
               f"email: {self.email}, enabled: {self.enabled}, confirmed: {self.confirmed}, " \
               f"acct_expired: {self.account_non_expired}, acct_locked: {self.account_non_locked}, " \
               f"cred_expired: {self.credentials_non_expired}"

    def short_str(self):
        return UserFormatter.short(self)

    def pretty_str(self):
        return UserFormatter.pretty(self)

    class Role:
        ADMIN = 'ROLE_ADMIN'
        DRIVER = 'ROLE_DRIVER'
        EMPLOYEE = 'ROLE_EMPLOYEE'
        CUSTOMER = 'ROLE_CUSTOMER'


class UserGenerator:
    @classmethod
    def generate_password(cls, password_len: int) -> str:
        """
        Generate a random password.

        :param password_len: the length of the password
        :return: the generated password
        """
        lower = string.ascii_lowercase
        upper = string.ascii_uppercase
        numbers = string.digits
        symbols = string.punctuation
        all_chars = lower + upper + numbers + symbols
        password = "".join(random.sample(all_chars, password_len))

        def _salt_and_hash(_password: str):
            return bcrypt.hashpw(_password.encode('utf-8'), bcrypt.gensalt(rounds=10, prefix=b"2a"))

        return _salt_and_hash(password).decode('utf-8')

    @classmethod
    def generate_email(cls, min_len=4, max_len=20) -> str:
        """
        Generate a random email.

        :param min_len: the minimum length of the email
        :param max_len: the maximum length of the email
        :return: the generated email
        """
        extensions = ['com', 'net', 'org', 'gov']
        domains = ['gmail', 'yahoo', 'comcast', 'verizon', 'smoothstack', 'hotmail']
        win_ext = extensions[random.randint(0, len(extensions) - 1)]
        win_dom = domains[random.randint(0, len(domains) - 1)]
        acc_len = random.randint(min_len, max_len)
        win_acc = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(acc_len))
        finale = win_acc + "@" + win_dom + "." + win_ext
        return finale

    @classmethod
    def generate_user(cls, role) -> User:
        """
        Generate a random User.

        :param role: the role of the user
        :return: the generated User
        """
        password = cls.generate_password(password_len=12)
        email = cls.generate_email(min_len=4, max_len=12)
        user_id = uuid.uuid4()
        user = User(user_id=user_id, user_role=role, password=password, email=email)
        return user


class UserFormatter:
    @staticmethod
    def pretty(user: User) -> str:
        return f" id:                       {str(user.id)}{os.linesep}" \
               f" user_role:                {user.user_role}{os.linesep}" \
               f" password:                 {user.password}{os.linesep}" \
               f" email:                    {user.email}{os.linesep}" \
               f" enabled:                  {user.enabled}{os.linesep}" \
               f" confirmed:                {user.confirmed}{os.linesep}" \
               f" account_non_expired:      {user.account_non_expired}{os.linesep}" \
               f" account_non_locked:       {user.account_non_locked}{os.linesep}" \
               f" credentials_non_expired:  {user.credentials_non_expired}"

    @staticmethod
    def short(user: User) -> str:
        return f"id: {'null' if not user.id else str(user.id)[0:2] + '...'}, " \
               f"rl: {'null' if not user.user_role else user.user_role[5:7] + '...'} " \
               f"pw: {'null' if not user.password else user.password[0:2] + '...'}, " \
               f"em: {'null' if not user.email else user.email[0:2] + '...'}, " \
               f"en: {'T' if user.enabled else 'F'}, " \
               f"cn: {'T' if user.confirmed else 'F'}, " \
               f"ae: {'T' if user.account_non_expired else 'F'}, " \
               f"al: {'T' if user.account_non_locked else 'F'}, " \
               f"ce: {'T' if user.credentials_non_expired else 'F'}"

    class UserJsonDecoder(json.JSONDecoder):
        def __init__(self, *args, **kwargs):
            json.JSONDecoder.__init__(self, object_hook=UserFormatter.UserJsonDecoder._object_hook, *args, **kwargs)

        @staticmethod
        def _object_hook(dct):
            return User(user_id=uuid.UUID(dct['id']), user_role=dct['user_role'], password=dct['password'],
                        email=dct['email'], enabled=bool(dct['enabled']), confirmed=bool(dct['confirmed']),
                        account_non_expired=bool(dct['account_non_expired']),
                        account_non_locked=bool(dct['account_non_locked']),
                        credentials_non_expired=bool(dct['credentials_non_expired']))

    class UserJsonEncoder(json.JSONEncoder):
        def default(self, obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            else:
                return str(obj)

    @staticmethod
    def to_json(users: list[User]) -> str:
        return json.dumps(users, indent=4, cls=UserFormatter.UserJsonEncoder)

    @staticmethod
    def from_json(json_str: str) -> list[User]:
        return json.loads(json_str, cls=UserFormatter.UserJsonDecoder)

    @staticmethod
    def from_csv(csv_str) -> list[User]:
        users = []
        for line in csv_str.split(os.linesep):
            if not line.strip():
                continue
            fields = line.split(',')
            if len(fields) != 9:
                raise IndexError('not enough fields')

            users.append(User(user_id=uuid.UUID(fields[0]),
                              user_role=fields[1],
                              password=fields[2],
                              email=fields[3],
                              enabled=string_to_bool(fields[4]),
                              confirmed=string_to_bool(fields[5]),
                              account_non_expired=string_to_bool(fields[6]),
                              account_non_locked=string_to_bool(fields[7]),
                              credentials_non_expired=string_to_bool(fields[8])))
        return users

    @staticmethod
    def to_csv(users: list[User]) -> str:
        csv_str = ""
        for user in users:
            csv_str += f"{user.id},{user.user_role},{user.password},{user.email},{user.enabled},{user.confirmed}," \
                       f"{user.account_non_expired},{user.account_non_locked},{user.credentials_non_expired}" \
                       f"{os.linesep}"
        return csv_str[0:-1]

    @staticmethod
    def from_xml(xml_str) -> list[User]:
        tree = ET.fromstring(xml_str)

        def _find_or_throw(_item, name: str):
            el = _item.find(name)
            if el is None:
                raise KeyError(name)
            return el.text

        users = []
        for item in tree.findall('./user'):
            user = User(user_id=uuid.UUID(_find_or_throw(item, 'id')),
                        user_role=_find_or_throw(item, 'user_role'),
                        password=_find_or_throw(item, 'password'),
                        email=_find_or_throw(item, 'email'),
                        enabled=string_to_bool(_find_or_throw(item, 'enabled')),
                        confirmed=string_to_bool(_find_or_throw(item, 'confirmed')),
                        account_non_expired=string_to_bool(_find_or_throw(item, 'account_non_expired')),
                        account_non_locked=string_to_bool(_find_or_throw(item, 'account_non_locked')),
                        credentials_non_expired=string_to_bool(_find_or_throw(item, 'credentials_non_expired')))
            users.append(user)
        return users

    @staticmethod
    def to_xml(users: list[User]) -> str:
        doc = minidom.Document()
        root = doc.createElement('users')
        doc.appendChild(root)

        def _add_user_element(_user_el, name: str, value: str):
            child_el = doc.createElement(name)
            child_el.appendChild(doc.createTextNode(value))
            _user_el.appendChild(child_el)
            root.appendChild(user_el)

        for user in users:
            user_el = doc.createElement('user')
            _add_user_element(user_el, 'id', str(user.id))
            _add_user_element(user_el, 'user_role', user.user_role)
            _add_user_element(user_el, 'password', user.password)
            _add_user_element(user_el, 'email', user.email)
            _add_user_element(user_el, 'enabled', str(user.enabled))
            _add_user_element(user_el, 'confirmed', str(user.confirmed))
            _add_user_element(user_el, 'account_non_expired', str(user.account_non_expired))
            _add_user_element(user_el, 'account_non_locked', str(user.account_non_locked))
            _add_user_element(user_el, 'credentials_non_expired', str(user.credentials_non_expired))

        return doc.toprettyxml().replace('\t', ' ' * 4)


class UsersProducer:
    def __init__(self, db: Database):
        self.db = db
        self.short_output = False
        self.pretty_output = False
        self.output_limit = 10

    def save_user(self, user: User) -> bool:
        """
        Create a user row in the user table

        :param user: the user to save
        :return: true if the user was saved successfully, otherwise false
        """
        try:
            self.db.open_connection()
            with self.db.conn.cursor() as cursor:
                sql = "INSERT INTO user (id, user_role, password, email, enabled, confirmed, account_non_expired, " \
                      "account_non_locked, credentials_non_expired) " \
                      "VALUES (UNHEX(?), ?, ?, ?, ?, ?, ?, ?, ?)"
                cursor.execute(sql, (user.id.hex, user.user_role, user.password, user.email, user.enabled,
                                     user.confirmed, user.account_non_expired, user.account_non_locked,
                                     user.credentials_non_expired))
            return True
        except jaydebeapi.DatabaseError as ex:
            print(f"{os.linesep}Problem occurred saving user:{os.linesep * 2}{UserFormatter.pretty(user)}{os.linesep}")
            print(str(ex).split(':')[1].strip())
            return False
        finally:
            if self.db.conn:
                self.db.conn.close()
                self.db.conn = None
                log.info('Database connection closed.')

    def set_short_output(self, short_output: bool):
        self.short_output = short_output

    def set_pretty_output(self, pretty_output: bool):
        self.pretty_output = pretty_output

    def set_output_limit(self, output_limit: int):
        self.output_limit = output_limit

    def _confirm_and_save(self, users: list[User]):
        answer = print_items_and_confirm(items=users, item_type='users', print_limit=self.output_limit,
                                         short=self.short_output, pretty=self.pretty_output)
        if answer.strip().lower() == 'n':
            print('No records will be inserted.')
            sys.exit(0)
        else:
            saved = 0
            for user in users:
                if self.save_user(user):
                    saved += 1
            print(f"{saved} users created successfully.")

    def produce_random(self, num_custs=0, num_admins=0, num_emps=0, num_drivers=0):
        """
        Create random users (customers, admins, employees).

        :param num_custs: the number of customers to create
        :param num_admins: the number of admins to create
        :param num_emps: the number of employees to create
        :param num_drivers: the number of drivers to create
        """
        users = []
        for _ in range(num_custs):
            users.append(UserGenerator.generate_user(role=User.Role.CUSTOMER))
        for _ in range(num_admins):
            users.append(UserGenerator.generate_user(role=User.Role.ADMIN))
        for _ in range(num_emps):
            users.append(UserGenerator.generate_user(role=User.Role.EMPLOYEE))
        for _ in range(num_drivers):
            users.append(UserGenerator.generate_user(role=User.Role.DRIVER))

        self._confirm_and_save(users)

    def produce_from_csv(self, csv_path: str):
        """
        Create users from a csv file. The csv file should be in the format (no header):
        id,user_role,password,email,confirmed,acct_expired,acct_locked,cred_expired
        All fields must be present.

        :param csv_path: the path to the csv file
        """
        users = []
        with open(csv_path) as file:
            try:
                users += UserFormatter.from_csv(file.read())
            except IndexError:
                print(f"There are missing fields. Rows must contain all properties.")

        self._confirm_and_save(users)

    def produce_from_json(self, json_file: str):
        """
        Create users from a json file. All fields must be present.

        :param json_file: the path to the json file
        """
        with open(json_file) as f:
            try:
                users = UserFormatter.from_json(f.read())
            except json.decoder.JSONDecodeError:
                print('JSON is not valid format.')
                sys.exit(1)
            except KeyError as k_ex:
                print(f"User missing {k_ex}. All fields are required.")
                sys.exit(1)
            except ValueError as v_ex:
                print(v_ex)
                sys.exit(1)

        self._confirm_and_save(users)

    def produce_from_xml(self, xml_file: str):
        """
        Create users from an xml file. All fields must be present.

        :param xml_file: the path to the xml file
        """
        users = []
        with open(xml_file) as f:
            try:
                users += UserFormatter.from_xml(f.read())
            except xml.etree.ElementTree.ParseError as p_ex:
                print(f"Malformed XML: {p_ex}")
                sys.exit(1)
            except KeyError as k_ex:
                print(f"User missing {k_ex}. All fields are required.")
                sys.exit(1)

        self._confirm_and_save(users)

    @staticmethod
    def convert_files(in_file, out_file):
        """
        Convert user data file from one format to another.

        :param in_file: the path to the input file
        :param out_file: the path to the output file
        """
        in_ext = in_file.split('.')[-1]
        out_ext = out_file.split('.')[-1]

        ext_funcs = {
            'csv': {'from_func': UserFormatter.from_csv, 'to_func': UserFormatter.to_csv},
            'json': {'from_func': UserFormatter.from_json, 'to_func': UserFormatter.to_json},
            'xml': {'from_func': UserFormatter.from_xml, 'to_func': UserFormatter.to_xml}
        }

        if in_ext not in ext_funcs:
            print(f"{in_ext} input format not supported.")
            sys.exit(1)
        if out_ext not in ext_funcs:
            print(f"{out_ext} output format not supported.")
            sys.exit(1)

        with open(in_file) as f:
            in_contents = f.read()

        users = ext_funcs[in_ext]['from_func'](in_contents)
        out_contents = ext_funcs[out_ext]['to_func'](users)

        with open(out_file, 'w') as f:
            f.write(out_contents)


def main(arguments):
    producer = UsersProducer(Database(Config()))
    parser = UsersArgParser(arguments)
    args = parser.args

    def _check_file(file):
        if not os.path.isfile(file):
            print(f"{file} does not exist.")
            sys.exit(1)

    if args.convert:
        _check_file(args.convert[0])
        producer.convert_files(args.convert[0], args.convert[1])
        return

    if args.csv_format:
        print('ID,USER_ROLE,PASSWORD,EMAIL,ENABLED,CONFIRMED,ACCT_EXPIRED,ACCT_LOCKED,CRED_EXPIRED')
        print(UserFormatter.to_csv([UserGenerator.generate_user(User.Role.ADMIN)]))
        print('Headers should not be included in the file.')
        return

    if args.json_format:
        print(UserFormatter.to_json([UserGenerator.generate_user(User.Role.ADMIN)]))
        return

    if args.xml_format:
        print(UserFormatter.to_xml([UserGenerator.generate_user(User.Role.ADMIN)]))
        return

    producer.set_short_output(args.short)
    producer.set_pretty_output(args.pretty)
    producer.set_output_limit(args.limit)

    def _produce_from_file(file, _produce_func):
        _check_file(file)
        _produce_func(file)

    if args.csv:
        _produce_from_file(args.csv, producer.produce_from_csv)
    elif args.json:
        _produce_from_file(args.json, producer.produce_from_json)
    elif args.xml:
        _produce_from_file(args.xml, producer.produce_from_xml)
    else:
        custs = args.custs or 0
        admins = args.admins or 0
        emps = args.emps or 0
        drivers = args.drivers or 0
        producer.produce_random(num_custs=custs, num_admins=admins, num_emps=emps, num_drivers=drivers)


if __name__ == '__main__':
    main(sys.argv[1:])
