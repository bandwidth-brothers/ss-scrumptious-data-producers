import random

from jaydebeapi import Error

from app.db.database import Database


class Restaurant:

    def __init__(self,
                 restaurant_id: int = None,
                 address_id: int = None,
                 owner_id: bytes = None,
                 name: str = None,
                 rating: float = None,
                 price_category: int = None,
                 phone: str = None,
                 is_active: bool = None,
                 picture: str = None
                 ):
        self.restaurant_id = restaurant_id
        self.address_id = address_id
        self.owner_id = owner_id
        self.name = name
        self.rating = rating
        self.price_category = price_category
        self.phone = phone
        self.is_active = is_active
        self.picture = picture

    def create_random(self, producer):
        self.address_id = producer.create_random_address()
        self.owner_id = random.choice(producer.restaurant_owners)[0]
        self.name = random.choice(producer.names)
        self.rating = random.random() * 5
        self.price_category = random.choice((1, 2, 3))
        self.phone = self.create_phone()
        self.is_active = random.choice((True, False))

    def create_phone(self):
        phone = "xxx-xxx-xxxx"
        output = [x if x != "x" else str(random.randint(1, 9)) for x in phone]
        return "".join(output)

    def save(self, database: Database):
        try:
            with database.conn.cursor() as cursor:
                sql = "INSERT INTO restaurant (address_id, owner_id, name, rating, price_category, phone, is_active, picture) " \
                      "VALUES (?,?,?,?,?,?,?,?)"
                values = (
                    self.address_id, self.owner_id, self.name, self.rating,
                    self.price_category,
                    self.phone, self.is_active, self.picture)

                cursor.execute(sql, values)
                cursor.close()
                return True
        except Error as e:
            print(f"Unable to save restaurant: {self.__str__()}\n  Because: {e}")
            return False

    def __str__(self):
        return f"Address ID: {self.address_id}, " \
               f"Owner ID: {self.owner_id}, Name: {self.name}, " \
               f"Rating: {self.rating}, Price category: {self.price_category}, " \
               f"Phone: {self.phone}, Is Active: {self.is_active}, Logo: {self.picture}"
