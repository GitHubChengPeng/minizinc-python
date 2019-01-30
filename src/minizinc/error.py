import re
from pathlib import Path
from typing import NamedTuple, Optional


# TODO: Python 3.7 -> @dataclass
class Location(NamedTuple):
    file: Optional[Path]
    line: int = 0
    column: int = 0

    @classmethod
    def unknown(cls):
        return cls(None)


class MiniZincError(Exception):
    """
    Exception raised for errors raised by the MiniZinc Driver
    Attributes:
        location -- file location of the error
        message -- explanation of the error
    """

    def __init__(self, location: Location, message: str):
        super().__init__(message)
        self.location = location


class EvaluationError(MiniZincError):
    pass


class MiniZincAssertionError(EvaluationError):
    pass


class MiniZincTypeError(MiniZincError):
    pass


def parse_error(error_txt: bytes) -> MiniZincError:
    error = MiniZincError
    if re.search(rb"evaluation error:", error_txt):
        error = EvaluationError
        if re.search(rb"evaluation error:", error_txt):
            error = MiniZincAssertionError
    elif re.search(rb"MiniZinc: type error:", error_txt):
        error = MiniZincTypeError

    location = Location.unknown()
    match = re.search(rb"(\w[^\w]+:(\d+)(.\d+)?:\w)", error_txt)
    if match:
        print(match.groups())
        column = int(match[2].decode()) if match.groups() else location.column
        location = Location(Path(match[0].decode()), int(match[3].decode()), column)

    message = ""
    lst = error_txt.split(b"\n")
    if lst:
        while len(lst) > 1 and lst[-1] == b"":
            lst.pop()
        message = lst[-1].split(b"error:", 1)[-1].strip()

    return error(location, message.decode())