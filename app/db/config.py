
from os import environ
from dotenv import load_dotenv

load_dotenv('.env')


class Config:
    def __init__(self):
        # Database configuration
        self.db_user = environ.get('DATABASE_USERNAME')
        self.db_password = environ.get('DATABASE_PASSWORD')
        self.db_host = environ.get('DATABASE_HOST')
        self.db_port = environ.get('DATABASE_PORT')
        self.db_name = environ.get('DATABASE_NAME')

