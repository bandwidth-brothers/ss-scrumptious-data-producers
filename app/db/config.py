
import os

from os import environ
from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv(os.getenv('ENV_FILE') or '.env')
        # Database configuration
        self.db_user = environ.get('DATABASE_USERNAME')
        self.db_password = environ.get('DATABASE_PASSWORD')
        self.db_url = environ.get('DATABASE_URL')
        self.db_driver = environ.get('DATABASE_DRIVER')
        self.db_jarfile = environ.get('DATABASE_JARFILE')

    def __str__(self):
        return f"driver: {self.db_driver}, jar: {self.db_jarfile}, url: {self.db_url}, " \
                f"user: {self.db_user}, pass: {self.db_password}"

