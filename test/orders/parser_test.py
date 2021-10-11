from app.orders.parser import OrdersArgParser
from app.common.constants import DEFAULT_OUTPUT_LIMIT


def test_orders_arg_parser_commands():
    parser = OrdersArgParser(['produce'])
    assert parser.args.command == 'produce'

    parser = OrdersArgParser(['ingest'])
    assert parser.args.command == 'ingest'


def test_orders_arg_parser_produce_args():
    args = OrdersArgParser(['produce', '--count', '5']).args
    assert args.count == 5


def test_orders_arg_producer_output_args():
    args = OrdersArgParser(['produce', '--count', '5']).args
    assert args.pretty is False
    assert args.short is False
    assert args.limit == DEFAULT_OUTPUT_LIMIT

    args = OrdersArgParser(['produce', '--count', '5', '--short', '--pretty', '--limit', '5']).args
    assert args.pretty is True
    assert args.short is True
    assert args.limit == 5


def test_orders_arg_parser_ingest_file_args():
    args = OrdersArgParser(['ingest', '--csv', 'file.csv', '--json', 'file.json', '--xml', 'file.xml']).args

    assert args.csv == 'file.csv'
    assert args.json == 'file.json'
    assert args.xml == 'file.xml'


def test_orders_arg_parser_ingest_show_format_args():
    args = OrdersArgParser(['ingest', '--csv-format']).args
    assert args.csv_format is True
    assert args.json_format is False
    assert args.xml_format is False

    args = OrdersArgParser(['ingest', '--json-format']).args
    assert args.csv_format is False
    assert args.json_format is True
    assert args.xml_format is False

    args = OrdersArgParser(['ingest', '--xml-format']).args
    assert args.csv_format is False
    assert args.json_format is False
    assert args.xml_format is True


def test_orders_arg_parser_ingest_output_args():
    args = OrdersArgParser(['ingest', '--csv', 'file.csv']).args
    assert args.pretty is False
    assert args.short is False
    assert args.limit == DEFAULT_OUTPUT_LIMIT

    args = OrdersArgParser(['ingest', '--csv', 'file.csv', '--short', '--pretty', '--limit', '5']).args
    assert args.pretty is True
    assert args.short is True
    assert args.limit == 5
