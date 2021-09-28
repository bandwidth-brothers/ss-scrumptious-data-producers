import os
import json
import functools
import xml.etree.ElementTree as ET

from xml.dom import minidom
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type, SupportsAbs
from app.common.exceptions import MissingAttributeException


T = TypeVar('T')
JE = TypeVar('JE', bound=SupportsAbs[json.JSONEncoder])
JD = TypeVar('JD', bound=SupportsAbs[json.JSONDecoder])


class AbstractFormatter(Generic[T], ABC):

    def pretty(self, item: T) -> str:
        """
        Get object formatted in a 'pretty' format.

        :param item: the object to format
        :return: the pretty formatted string
        """
        attrs = vars(item)
        max_len = functools.reduce(lambda max_val, _attr: max(len(_attr), max_val), dir(item), 0)
        pretty_str = ""
        for attr in attrs:
            spaces = (max_len + 1) - len(attr)
            pretty_str += f"  {attr}:{' ' * spaces}{attrs[attr]}{os.linesep}"
        return pretty_str

    def short(self, item: T, val_len: int = 2) -> str:
        """
        Get object formatted in short form.

        :param item: the object to format
        :param val_len: the length of the formatted value of an attribute
        :return: the short formatted string
        """
        short_str = ""
        attrs = vars(item)
        for attr in attrs:
            val_str = str(attrs[attr])
            short_str += f"{attr[0:2]}: {val_str[0:val_len]}{'...' if len(val_str) > val_len else ''}, "
        return short_str[0:-2]

    def to_json(self, items: list[T]):
        """
        Get formatted json string from list of objects.

        :param items: the objects to format
        :return: the formatted json string
        """
        return json.dumps(items, indent=4, cls=self.get_json_encoder())

    @abstractmethod
    def get_json_encoder(self) -> Type[JE]:
        """
        Get the JSONEncoder for the type.

        :return: the JSONEncoder
        """
        pass

    def from_json(self, json_str) -> list[T]:
        """
        Convert a json array of objects into a list of objects.

        :param json_str: the json string to convert
        :return: the list of objects
        """
        return json.loads(json_str, cls=self.get_json_decoder())

    @abstractmethod
    def get_json_decoder(self) -> Type[JD]:
        """
        Get the JSONDecoder for the type.

        :return: the JSONDecoder
        """
        pass

    @staticmethod
    def get_attr_or_throw(dct, name):
        """
        Get json attribute value from dictionary. If the attribute does not
        exist, a MissingAttributeException will be thrown.

        :param dct: the dictionary from json attributes
        :param name: the name of the attribute
        :return: the value of the json attribute
        """
        try:
            return str(dct[name])
        except KeyError:
            raise MissingAttributeException(f"'{name}'")

    def to_csv(self, items: list[T]) -> str:
        """
        Get formatted json string from a list of objects.

        :param items: the list of objects to format
        :return: the formatted json string
        """
        csv_str = ""
        for item in items:
            _dict = vars(item)
            for attr in self.get_attr_list():
                csv_str += f"{_dict[attr]},"
            csv_str = csv_str[0:-1] + os.linesep
        return csv_str[0:-1]

    def from_csv(self, csv_str) -> list[T]:
        """
        Convert a csv string into a list of objects.

        :param csv_str: the csv string to convert
        :return: the list of objects
        """
        items = []
        for line in csv_str.split(os.linesep):
            if not line.strip():
                continue
            fields = line.split(',')
            num_attrs = len(self.get_attr_list())
            if len(fields) != num_attrs:
                raise IndexError('Incorrect number of fields.')
            item = self.create_object_from_string_fields(fields)
            items.append(item)
        return items

    @abstractmethod
    def get_attr_list(self):
        """
        Get the list of attributes for a type. The order of the attributes should be
        in the same order as they would appear in a csv row.

        :return: the list of attributes
        """
        pass

    @abstractmethod
    def get_object_type(self) -> Type[T]:
        """
        Get the object type this formatter is used for.

        :return: the object type
        """
        pass

    @abstractmethod
    def create_object_from_string_fields(self, fields: list[str]) -> T:
        """
        Create an object from fields. Used for parsing csv. The field order will
        be in the same order as in the csv string/file.

        :param fields: the list of fields
        :return: the object
        """
        pass

    def to_xml(self, items: list[T]):
        """
        Format a list of objects into an xml string.

        :param items: the list of objects
        :return: the formatted xml string
        """
        _type = self.get_object_type().__name__.lower()
        doc = minidom.Document()
        root = doc.createElement(_type + 's')
        doc.appendChild(root)

        for item in items:
            _dict = vars(item)
            el = doc.createElement(_type)
            for attr in self.get_attr_list():
                child_el = doc.createElement(attr)
                val = self.get_attr_or_throw(_dict, attr)
                child_el.appendChild(doc.createTextNode(str(val)))
                el.appendChild(child_el)
            root.appendChild(el)

        return doc.toprettyxml().replace('\t', ' ' * 4)[0:-1]

    def from_xml(self, xml_str: str) -> list[T]:
        """
        Convert xml string to a list of objects.

        :param xml_str: the xml string to convert
        :return: the list of objects
        """
        def _find_or_throw(_item, _name: str):
            el = _item.find(_name)
            if el is None:
                raise MissingAttributeException(f"'{_name}'")
            return el.text

        _type = self.get_object_type().__name__.lower()
        tree = ET.fromstring(xml_str)
        items = []

        for item in tree.findall(f"./{_type}"):
            _dict = {}
            attr_names = self.get_attr_list()
            for name in attr_names:
                _dict[name] = _find_or_throw(item, name)
            items.append(self.create_object_from_string_dict(_dict))

        return items

    @abstractmethod
    def create_object_from_string_dict(self, _dict) -> T:
        """
        Create object from a string dictionary of values.

        :param _dict: the string values dictionary
        :return: the object
        """
        pass


# if __name__ == '__main__':
#     from app.items.model import Order
#
#     class OrderFormatter(AbstractFormatter[Order]):
#         def get_object_type(self) -> Type[T]:
#             return Order
#
#         def create_object_from_fields(self):
#             pass
#         def create_object_from_string_dict(self):
#             pass
#         def get_json_decoder(self):
#             pass
#         def get_json_encoder(self):
#             pass
#     formatter = OrderFormatter()
#     print(formatter._get_attrs_for_type())
