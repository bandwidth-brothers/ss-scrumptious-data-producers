from db.config import Config
from db.database import Database


def main():
    db = Database(Config())
    results = db.run_query("SHOW TABLES")
    for result in results:
        print(result)


if __name__ == '__main__':
    main()
