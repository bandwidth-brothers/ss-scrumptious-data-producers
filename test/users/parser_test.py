from app.users.parser import UsersArgParser
from app.common.constants import DEFAULT_OUTPUT_LIMIT


def test_users_arg_parser_commands():
    parser = UsersArgParser(['produce'])
    assert parser.args.command == 'produce'

    parser = UsersArgParser(['ingest'])
    assert parser.args.command == 'ingest'


def test_users_arg_parser_produce_args():
    args = UsersArgParser(['produce', '--custs', '1', '--admins', '2', '--drivers', '3', '--emps', '4', '--all', '5',
                           '--pretty', '--short', '--limit', '6']).args
    assert args.custs == 1
    assert args.admins == 2
    assert args.drivers == 3
    assert args.emps == 4
    assert args.all == 5


def test_users_arg_producer_output_args():
    args = UsersArgParser(['produce', '--all', '5']).args
    assert args.pretty is False
    assert args.short is False
    assert args.limit == DEFAULT_OUTPUT_LIMIT

    args = UsersArgParser(['produce', '--all', '5', '--short', '--pretty', '--limit', '5']).args
    assert args.pretty is True
    assert args.short is True
    assert args.limit == 5


def test_users_arg_parser_ingest_file_args():
    args = UsersArgParser(['ingest', '--csv', 'file.csv', '--json', 'file.json', '--xml', 'file.xml']).args

    assert args.csv == 'file.csv'
    assert args.json == 'file.json'
    assert args.xml == 'file.xml'


def test_users_arg_parser_ingest_show_format_args():
    args = UsersArgParser(['ingest', '--csv-format']).args
    assert args.csv_format is True
    assert args.json_format is False
    assert args.xml_format is False

    args = UsersArgParser(['ingest', '--json-format']).args
    assert args.csv_format is False
    assert args.json_format is True
    assert args.xml_format is False

    args = UsersArgParser(['ingest', '--xml-format']).args
    assert args.csv_format is False
    assert args.json_format is False
    assert args.xml_format is True


def test_users_arg_parser_ingest_output_args():
    args = UsersArgParser(['ingest', '--csv', 'file.csv']).args
    assert args.pretty is False
    assert args.short is False
    assert args.limit == DEFAULT_OUTPUT_LIMIT

    args = UsersArgParser(['ingest', '--csv', 'file.csv', '--short', '--pretty', '--limit', '5']).args
    assert args.pretty is True
    assert args.short is True
    assert args.limit == 5
