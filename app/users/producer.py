import os
import sys
import json
from typing import Type

import jaydebeapi
import logging as log
import xml.etree.ElementTree

from app.db.database import Database
from app.users.model import User
from app.users.formatter import UserFormatter
from app.users.generator import UserGenerator

from app.common.producer import AbstractProducer
from app.common.exceptions import MissingAttributeException


class UsersProducer(AbstractProducer[User]):

    def __init__(self, db: Database):
        super(UsersProducer, self).__init__(db)

    def save(self, user: User):
        return self.save_user(user)

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
            print(f"{os.linesep}Problem occurred saving user:{os.linesep * 2}"
                  f"{UserFormatter().pretty(user)}{os.linesep}")
            print(str(ex).split(':')[1].strip())
            return False
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
                users += UserFormatter().from_csv(file.read())
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
                users = UserFormatter().from_json(f.read())
            except json.decoder.JSONDecodeError:
                print('JSON is not valid format.')
                sys.exit(1)
            except MissingAttributeException as m_ex:
                print(f"User missing {m_ex}. All fields are required.")
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
                users += UserFormatter().from_xml(f.read())
            except xml.etree.ElementTree.ParseError as p_ex:
                print(f"Malformed XML: {p_ex}")
                sys.exit(1)
            except MissingAttributeException as k_ex:
                print(f"User missing {k_ex}. All fields are required.")
                sys.exit(1)

        self._confirm_and_save(users)

    def get_formatter(self) -> UserFormatter:
        return UserFormatter()

    def get_object_type(self) -> Type[User]:
        return User
