import distutils

from distutils import util


def string_to_bool(bool_str: str) -> bool:
    return bool(distutils.util.strtobool(bool_str))
