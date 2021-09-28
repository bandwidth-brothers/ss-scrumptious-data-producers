import argparse

from app.db.config import Config
from app.db.database import Database
from app.orders.dependencies import DeliveryData
from app.orders.dependencies import CustomerData
from app.orders.dependencies import RestaurantData


def get_ids(db: Database, query: str):
    results = db.run_query(query)
    return list(map(lambda result: result[0], results))


def get_user_ids(db: Database, user_role):
    return get_ids(db, f"SELECT HEX(userId) FROM user WHERE userRole = '{user_role}'")


def get_driver_ids(db: Database):
    return get_ids(db, "SELECT HEX(driverId) FROM driver")


def get_address_ids(db: Database):
    return get_ids(db, "SELECT addressId FROM address")


def make_test_data(args):
    parser = argparse.ArgumentParser(description='Create test data')
    parser.add_argument('--clear', action='store_true', help='clear all records')
    parser.add_argument('--delete-orders', action='store_true', help='delete items when --clear is used')
    parser.add_argument('--all', type=int, help='create n of each type')
    parser.add_argument('--customers', type=int, help='create customers')
    parser.add_argument('--deliveries', type=int, help='create deliveries')
    parser.add_argument('--restaurants', type=int, help='create restaurants')

    args = parser.parse_args(args)
    db = Database(Config())

    if args.clear:
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        with db.conn.cursor() as cursor:
            if args.delete_orders:
                cursor.execute('DELETE FROM `order`')
            cursor.execute('DELETE FROM restaurant')
            cursor.execute('DELETE FROM owner')
            cursor.execute('DELETE FROM delivery')
            cursor.execute('DELETE FROM driver')
            cursor.execute('DELETE FROM customer')
            cursor.execute('DELETE FROM address')
            cursor.execute('DELETE FROM `user`')
        db.conn.commit()
        db.conn.close()
        db.conn = None
        return

    def create_data(custs, rests, delivs):
        CustomerData.create_customers(db, custs)
        DeliveryData.create_deliveries(db, delivs)
        RestaurantData.create_restaurants(db, rests)

    if args.all:
        count = args.all
        create_data(custs=count, rests=count, delivs=count)
    else:
        create_data(custs=args.customers or 0,
                    delivs=args.deliveries or 0,
                    rests=args.restaurants or 0)

