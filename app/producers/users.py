
import os
import sys
import csv
import uuid
import string
import random
import pymysql
import argparse
import logging as log

from argparse import RawTextHelpFormatter
from app.db.config import Config
from app.db.database import Database


class UsersArgParser:
    def __init__(self, args):
        self.parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                              description="""Generate user data in MySQL database.
A comma separated values (CSV) file with a dataset may be provided
as an argument using the --csv option. When this argument is provided,
others will be ignored.

examples:

    python -m app.producers.users --csv <path-to-csv-file>
    python -m app.producers.users --custs 20 --admins 2 --emps 5 --drivers 5
    python -m app.producers.users --admins 2""")
        self.parser.add_argument('-f', '--csv', type=str, help="""a csv file with user data.
File should be in the format (no header):
userId,userRole,username,password,email""")
        self.parser.add_argument('--custs', type=int, help='number of customers to generate')
        self.parser.add_argument('--admins', type=int, help='umber of admins to generate')
        self.parser.add_argument('--emps', type=int, help='number of employees to generate')
        self.parser.add_argument('--drivers', type=int, help='number of drivers to generate')
        self.args = self.parser.parse_args(args)


class User:
    def __init__(self, user_id: uuid.UUID, user_role: str, username: str, password: str, email: str):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.user_role = user_role

    def __str__(self):
        return f"id: {self.user_id.hex}, role: {self.user_role}, username: {self.username},"\
               f"password: {self.password}, email: {self.email}"

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
        return "".join(random.sample(all_chars, password_len))

    @classmethod
    def generate_username(cls, min_len=8, max_len=32) -> str:
        """
        Generate a random username.

        :param min_len: the minimum length of the username
        :param max_len: the maximum length of the username
        :return: the generated username
        """
        length = random.randint(min_len, max_len)
        return "".join(random.sample(string.ascii_lowercase, length))

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
        username = cls.generate_username(min_len=8, max_len=12)
        password = cls.generate_password(password_len=12)
        email = cls.generate_email(min_len=4, max_len=12)
        user_id = uuid.uuid4()
        user = User(user_id, role, username, password, email)
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
                sql = "INSERT INTO user (userId, username, password, email, userRole) " \
                      "VALUES (UNHEX(?), ?, ?, ?, ?)"
                cursor.execute(sql, (user.user_id.hex, user.username, user.password, user.email, user.user_role))
        except pymysql.MySQLError as ex:
            print(f"Problem occurred saving user: {user}")
            print("Not users will be saved.")
            log.error(ex)
            sys.exit(1)
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

        print('The following users will be created:', end=os.linesep * 2)
        print_limit = 10
        for i in range(len(users)):
            if i >= print_limit:
                break
            print(f"  {users[i]}")
        if len(users) > print_limit:
            remaining = len(users) - print_limit
            print(f"  {remaining} more...")
        print()

        answer = input('Would you like to insert these into the database [Y/n]? ')
        if answer.strip().lower() == 'n':
            print('No records will be inserted.')
            sys.exit(0)
        else:
            for user in users:
                self.save_user(user)
            print(f"{len(users)} users created successfully.")

    def produce_from_csv(self, csv_path: str):
        """
        Create users from a csv file. The csv file should be in the format (no header)
        userId,userRole,username,password,email

        :param csv_path: the path to the csv file
        """
        with open(csv_path) as file:
            csv_reader = csv.reader(file, delimiter=',')
            for row in csv_reader:
                user_id = row[0]
                user_role = row[1]
                username = row[2]
                password = row[3]
                email = row[4]
                user = User(uuid.UUID(user_id), user_role, username, password, email)
                self.save_user(user)


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
