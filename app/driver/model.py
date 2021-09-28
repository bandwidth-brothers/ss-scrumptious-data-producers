import random
from datetime import date

from jaydebeapi import Error

from app.db.database import Database


class Driver:
    def __init__(self,
                 id: bytes = None,
                 address_id: int = None,
                 first_name: str = None,
                 last_name: str = None,
                 phone: str = None,
                 dob: str = None,
                 license_num: str = None,
                 rating: float = None,
                 status: str = None
                 ):
        self.id = id
        self.address_id = address_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = f"{first_name}.{last_name}@mail.com" if first_name is not None and last_name is not None else None
        self.phone = phone
        self.dob = dob
        self.license_num = license_num
        self.rating = rating
        self.status = status

    def create_random(self, producer):
        self.id = random.choice(producer.user_ids)
        self.address_id = random.choice(producer.address_ids)
        self.first_name = random.choice(producer.first_names)
        self.last_name = random.choice(producer.last_names)
        self.email = self.first_name + "." + self.last_name + "@mail.com"
        self.phone = self.create_phone()
        self.dob = self.create_dob()
        self.license_num = str(random.randint(10000, 99999))
        self.rating = random.random() * 5
        self.status = "waiting"

    def save(self, database: Database):
        try:
            with database.conn.cursor() as cursor:
                sql = "INSERT INTO driver (id, address_id, first_name, last_name, " \
                      "phone, dob, license_num, rating, picture, status) " \
                      "VALUES (UNHEX(?),?,?,?,?,?,?,?,?,?)"
                values = (
                    self.id, self.address_id, self.first_name, self.last_name,
                    self.phone, self.dob, self.license_num, self.rating, "https://temp.url/", "active"
                )

                cursor.execute(sql, values)
                cursor.close()
                return True
        except Error as e:
            print(f"Unable to save driver: {self.__str__()}\n  Because: {e}")
            return False

    def create_dob(self):
        return date.today().strftime("%d/%m/%Y")

    def create_phone(self):
        phone = "xxx-xxx-xxxx"
        output = [x if x != "x" else str(random.randint(1, 9)) for x in phone]
        return "".join(output)

    def __str__(self):
        return f"User ID: {self.id}, Location ID: {self.address_id}, " \
               f"Name: {self.first_name} {self.last_name}, Phone: {self.phone}, " \
               f"DOB: {self.dob}, License Plate: {self.license_num}, Rating: {self.rating}"
