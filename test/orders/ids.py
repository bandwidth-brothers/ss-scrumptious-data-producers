
from app.db.database import Database


def get_ids(db: Database, query: str):
    results = db.run_query(query)
    return list(map(lambda result: result[0], results))


def get_user_ids(db: Database, user_role):
    return get_ids(db, f"SELECT HEX(userId) FROM user WHERE userRole = '{user_role}'")


def get_driver_ids(db: Database):
    return get_ids(db, "SELECT HEX(driverId) FROM driver")


def get_address_ids(db: Database):
    return get_ids(db, "SELECT addressId FROM address")

