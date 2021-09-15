
import os

from app.db.config import Config
from app.db.database import Database


def init_db():
    db = Database(Config())
    db.open_connection()
    with db.conn.cursor() as curs:
        with open('db/h2/schema.sql') as file:
            sql = file.read().replace(os.linesep, '')
            tables = sql.split(';')[0:-1]
            for table in tables:
                curs.execute(table)
    db.conn.close()
    db.conn = None


if __name__ == '__main__':
    init_db()
