import sys

from abc import abstractmethod, ABC
from typing import TypeVar, SupportsAbs, Generic, Type
from app.db.database import Database
from app.common.formatter import AbstractFormatter
from app.common.constants import DEFAULT_OUTPUT_LIMIT
from app.common.helpers import print_items_and_confirm


T = TypeVar('T')
F = TypeVar('F', bound=SupportsAbs[AbstractFormatter])


class AbstractProducer(Generic[T], ABC):
    def __init__(self, db: Database):
        self.db = db
        self.short_output = False
        self.pretty_output = False
        self.output_limit = DEFAULT_OUTPUT_LIMIT

    def set_short_output(self, short_output: bool):
        self.short_output = short_output

    def set_pretty_output(self, pretty_output: bool):
        self.pretty_output = pretty_output

    def set_output_limit(self, output_limit: int):
        self.output_limit = output_limit

    def convert_files(self, in_file, out_file):
        """
        Convert data file from one format to another. The formatter is an
        implementation of the abstract AbstractFormatter class. Supported formats
        are csv, json, and xml

        :param in_file: the path to the input file
        :param out_file: the path to the output file
        """
        in_ext = in_file.split('.')[-1]
        out_ext = out_file.split('.')[-1]
        formatter = self.get_formatter()

        ext_funcs = {
            'csv': {'from_func': formatter.from_csv, 'to_func': formatter.to_csv},
            'json': {'from_func': formatter.from_json, 'to_func': formatter.to_json},
            'xml': {'from_func': formatter.from_xml, 'to_func': formatter.to_xml}
        }

        if in_ext not in ext_funcs:
            print(f"{in_ext} input format not supported.")
            sys.exit(1)
        if out_ext not in ext_funcs:
            print(f"{out_ext} output format not supported.")
            sys.exit(1)

        with open(in_file) as f:
            in_contents = f.read()

        users = ext_funcs[in_ext]['from_func'](in_contents)
        out_contents = ext_funcs[out_ext]['to_func'](users)

        with open(out_file, 'w') as f:
            f.write(out_contents)

    @abstractmethod
    def get_formatter(self) -> F:
        pass

    @abstractmethod
    def get_object_type(self) -> Type[T]:
        pass

    def _confirm_and_save(self, items: list[T]):
        if len(items) == 0:
            print('No records to insert.')
            sys.exit(0)

        _type = self.get_object_type().__name__.lower() + 's'
        answer = print_items_and_confirm(items=items, item_type=_type, print_limit=self.output_limit,
                                         short=self.short_output, pretty=self.pretty_output)
        if answer.strip().lower() == 'n':
            print('No records will be inserted.')
            sys.exit(0)
        else:
            saved = 0
            for item in items:
                if self.save(item):
                    saved += 1
            print(f"{saved} {_type} created successfully.")

    @abstractmethod
    def save(self, item: T):
        pass
