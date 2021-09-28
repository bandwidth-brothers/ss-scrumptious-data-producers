
import os
import sys
import csv
import uuid
import json
import bcrypt
import string
import random
import pymysql
import argparse
import logging as log

from argparse import RawTextHelpFormatter
from app.db.config import Config
from app.db.database import Database
from app.producers.helpers import print_items_and_confirm


class UsersArgParser:
    def __init__(self, args):
        self.parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                              description="""Generate user data in MySQL database.
A CSV, JSON, or XML file with a dataset may be provided as an argument using the
--csv, --json, or --xml option, respectively. When either of these arguments are
provided, others will be ignored.

examples:

    python -m app.producers.users --csv <path-to-csv-file>
    python -m app.producers.users --json <path-to-json-file>
    python -m app.producers.users --xml <path-to-xml-file>
    python -m app.producers.users --custs 20 --admins 2 --emps 5 --drivers 5
    python -m app.producers.users --admins 2""")
        self.parser.add_argument('--csv', type=str, help="""a csv file with user data.
File should be in the format following (no header). All fields required.:
user_id,user_role,password,email,confirmed,acct_expired,acct_locked,cred_expired""")
        self.parser.add_argument('--custs', type=int, help='number of customers to generate')
        self.parser.add_argument('--admins', type=int, help='umber of admins to generate')
        self.parser.add_argument('--emps', type=int, help='number of employees to generate')
        self.parser.add_argument('--drivers', type=int, help='number of drivers to generate')
        self.args = self.parser.parse_args(args)


class User:
    def __init__(self, user_id: uuid.UUID, user_role: str, password: str, email: str, enabled: bool = True,
                 confirmed: bool = True, account_non_expired: bool = True, account_non_locked: bool = True,
                 credentials_non_expired: bool = True):
        self.user_id = user_id
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

        return f"id: {_trunc(str(self.user_id), 12)}, role: {self.user_role}, passwd: {_trunc(self.password, 16)}, " \
               f"email: {self.email}, enabled: {self.enabled}, confirmed: {self.confirmed}, " \
               f"acct_expired: {self.account_non_expired}, acct_locked: {self.account_non_locked}, " \
               f"cred_expired: {self.credentials_non_expired}"

    class Role:
        ADMIN = 'ADMIN'
        EMPLOYEE = 'EMPLOYEE'
        CUSTOMER = 'CUSTOMER'
        DRIVER = 'DRIVER'


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
        winext = extensions[random.randint(0, len(extensions) - 1)]
        windom = domains[random.randint(0, len(domains) - 1)]
        acclen = random.randint(min_len, max_len)
        winacc = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(acclen))
        finale = winacc + "@" + windom + "." + winext
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


class UsersProducer:
    def __init__(self, db: Database):
        self.db = db

    def save_user(self, user: User):
        """
        Create a user row in the user table

        :param user: the user to save
        """
        try:
            self.db.open_connection()
            with self.db.conn.cursor() as cursor:
                sql = "INSERT INTO user (id, user_role, password, email, enabled, confirmed, account_non_expired, " \
                      "account_non_locked, credentials_non_expired) " \
                      "VALUES (UNHEX(?), ?, ?, ?, ?, ?, ?, ?, ?)"
                cursor.execute(sql, (user.user_id.hex, user.user_role, user.password, user.email, user.enabled,
                                     user.confirmed, user.account_non_expired, user.account_non_locked,
                                     user.credentials_non_expired))
        except pymysql.MySQLError as ex:
            print(f"Problem occurred saving user: {user}")
            log.error(ex)
            return
        finally:
            if self.db.conn:
                self.db.conn.close()
                self.db.conn = None
                log.info('Database connection closed.')

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

        answer = print_items_and_confirm(items=users, item_type='users')
        if answer.strip().lower() == 'n':
            print('No records will be inserted.')
            sys.exit(0)
        else:
            for user in users:
                self.save_user(user)
            print(f"{len(users)} users created successfully.")

    def produce_from_csv(self, csv_path: str):
        """
        Create users from a csv file. The csv file should be in the format (no header):
        user_id,user_role,password,email,confirmed,acct_expired,acct_locked,cred_expired
        All fields must be present.

        :param csv_path: the path to the csv file
        """
        users = []
        with open(csv_path) as file:
            csv_reader = csv.reader(file, delimiter=',')
            for row in csv_reader:
                user_id = row[0]
                user_role = row[1]
                password = row[2]
                email = row[3]
                enabled = bool(row[4])
                confirmed = bool(row[5])
                acct_expired = bool(row[6])
                acct_locked = bool(row[7])
                cred_expired = bool(row[8])
                users.append(User(user_id=uuid.UUID(user_id), user_role=user_role, password=password, email=email,
                                  enabled=enabled, confirmed=confirmed, account_non_expired=acct_expired,
                                  account_non_locked=acct_locked, credentials_non_expired=cred_expired))

        answer = print_items_and_confirm(items=users, item_type='users')
        if answer.strip().lower() == 'n':
            print('No records will be inserted.')
            sys.exit(0)
        else:
            for user in users:
                self.save_user(user)
            print(f"{len(users)} users created successfully.")


def main(arguments):
    producer = UsersProducer(Database(Config()))
    parser = UsersArgParser(arguments)
    args = parser.args

    csv_file = args.csv
    if csv_file:
        if not os.path.isfile(csv_file):
            print(f"{csv_file} does not exist.")
            return
        producer.produce_from_csv(csv_file)
    else:
        custs = args.custs or 0
        admins = args.admins or 0
        emps = args.emps or 0
        drivers = args.drivers or 0
        producer.produce_random(num_custs=custs, num_admins=admins, num_emps=emps, num_drivers=drivers)


if __name__ == '__main__':
    main(sys.argv[1:])
