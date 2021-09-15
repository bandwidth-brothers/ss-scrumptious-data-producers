
import sys
import pymysql
import logging as log

import jaydebeapi


class Database:

    def __init__(self, config):
        self.db_url = config.db_url
        self.db_user = config.db_user
        self.db_password = config.db_password
        self.db_driver = config.db_driver
        self.db_jarfile = config.db_jarfile
        self.conn = None

    def open_connection(self):
        try:
            if self.conn is None:
                self.conn = jaydebeapi.connect(
                    self.db_driver,
                    self.db_url,
                    {'user': self.db_user, 'password': self.db_password},
                    self.db_jarfile
                )
        except pymysql.MySQLError as e:
            print('Could not connect to the database. '
                  'Check environment variables and database accessibility.')
            log.error(e)
            sys.exit(1)
        finally:
            log.info('Connection opened successfully.')

    def run_query(self, query):
        try:
            self.open_connection()
            with self.conn.cursor() as cur:
                records = []
                cur.execute(query)
                result = cur.fetchall()
                for row in result:
                    records.append(row)
                cur.close()
                return records
        except pymysql.MySQLError as e:
            print(e)
        finally:
            if self.conn:
                self.conn.close()
                self.conn = None
                log.info('Database connection closed.')
