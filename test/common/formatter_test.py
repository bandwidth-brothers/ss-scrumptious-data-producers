import json
import pytest
import xml.etree.ElementTree as ET

from typing import Type
from app.common.formatter import AbstractFormatter
from app.common.exceptions import MissingAttributeException


class Item:
    id = None
    name = None

    def __init__(self, item_id: int, name: str):
        self.id = item_id
        self.name = name


class ItemFormatter(AbstractFormatter[Item]):
    class ItemEncoder(json.JSONEncoder):
        def default(self, obj):
            return obj.__dict__

    class ItemDecoder(json.JSONDecoder):
        def __init__(self, *args, **kwargs):
            json.JSONDecoder.__init__(self, object_hook=ItemFormatter.ItemDecoder._object_hook, *args, **kwargs)

        @classmethod
        def _object_hook(cls, dct):
            item_id = cls._get(dct, 'id')
            name = cls._get(dct, 'name')
            return Item(item_id=int(item_id), name=name)

        @classmethod
        def _get(cls, dct, name):
            return AbstractFormatter.get_attr_or_throw(dct, name)

    def get_json_encoder(self) -> Type[ItemEncoder]:
        return ItemFormatter.ItemEncoder

    def get_json_decoder(self) -> Type[ItemDecoder]:
        return ItemFormatter.ItemDecoder

    def get_attr_list(self):
        return ['id', 'name']

    def get_object_type(self) -> Type[Item]:
        return Item

    def create_object_from_string_fields(self, fields: list[str]) -> Item:
        return Item(item_id=int(fields[0]), name=fields[1])

    def create_object_from_string_dict(self, _dict) -> Item:
        return Item(item_id=int(_dict['id']), name=_dict['name'])


def _assert_properties_in_formatted_string(formatted_string: str):
    assert 'id' in formatted_string
    assert 'name' in formatted_string


def test_formatter_pretty():
    item = Item(item_id=1, name='smoothstack')
    pretty_str = ItemFormatter().pretty(item)

    _assert_properties_in_formatted_string(pretty_str)


def test_formatter_to_json():
    item = Item(item_id=1, name='smoothstack')
    json_str = ItemFormatter().to_json([item])

    _assert_properties_in_formatted_string(json_str)


def test_formatter_from_json():
    item = Item(item_id=1, name='smoothstack')
    json_str = json.dumps([item.__dict__])

    items = ItemFormatter().from_json(json_str)
    assert len(items) == 1

    i = items[0]
    assert i.id == item.id
    assert i.name == item.name


def test_formatter_from_json_missing_property():
    json_str = '[{"id": 1}]'
    with pytest.raises(MissingAttributeException) as ex:
        ItemFormatter().from_json(json_str)

    assert 'name' in str(ex)


def test_formatter_from_csv():
    csv_str = "1234,smoothstack"
    items = ItemFormatter().from_csv(csv_str)

    assert len(items) == 1
    item = items[0]

    assert item.id == 1234
    assert item.name == 'smoothstack'


def test_formatter_from_csv_wrong_row_size():
    csv_str = "1234"

    with pytest.raises(IndexError) as ex:
        ItemFormatter().from_csv(csv_str)

    assert 'Incorrect number of fields' in str(ex)


def test_formatter_to_csv():
    item = Item(item_id=1234, name='smoothstack')

    csv_str = ItemFormatter().to_csv([item])
    fields = csv_str.split(',')

    assert fields[0] == str(item.id)
    assert fields[1] == item.name


def test_formatter_to_xml():
    item = Item(item_id=1234, name='smoothstack')
    xml_str = ItemFormatter().to_xml([item])

    root = ET.fromstring(xml_str)
    nodes = root.findall('./item')

    assert len(nodes) == 1

    node = nodes[0]
    assert node.find('id').text == str(item.id)
    assert node.find('name').text == item.name


def test_order_formatter_from_xml():
    xml_str = """<?xml version="1.0" ?>
    <items>
        <item>
            <id>1234</id>
            <name>smoothstack</name>
        </item>
    </items>
    """
    items = ItemFormatter().from_xml(xml_str)
    assert len(items) == 1

    item = items[0]
    assert item.id == 1234
    assert item.name == 'smoothstack'


def test_formatter_from_xml_missing_property():
    xml_str = """<?xml version="1.0" ?>
    <items>
        <item>
            <id>1234</id>
        </item>
    </items>
        """
    with pytest.raises(MissingAttributeException) as ex:
        ItemFormatter().from_xml(xml_str)

    assert 'name' in str(ex)
