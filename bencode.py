from collections import OrderedDict
from itertools import islice, takewhile
from typing import IO, Any, Iterator


def dumps(v: Any) -> str:
    """Bencodes any type of data into a string"""    
    if isinstance(v, int):
        return f'i{v}e'

    elif isinstance(v, str):
        return f'{len(v)}:{v}'

    elif isinstance(v, bytes):
        return f'{len(v)}:{v.decode("utf8")}'

    elif isinstance(v, list):
        return f'l{"".join(dumps(i) for i in v)}e'

    elif isinstance(v, dict | OrderedDict):
        out = 'd'
        for key, value in v.items():
            key = dumps(key)
            value = dumps(value)
            out += f'{key}{value}'
        return out + 'e'


def dump(data: Any, io: IO[bytes], encoding: str = 'utf8') -> None:
    """Bencodes data and writes the bytes result into the io"""
    encoded = dumps(data).encode(encoding)
    io.write(encoded)


def sdump(data: Any, io: IO[str]) -> None:
    """Bencodes data and writes the string result into the io"""
    encoded = dumps(data)
    io.write(encoded)


def loads(data: bytes) -> Any:
    """Unpacks bencoded data"""
    it = iter(data)
    return _loads(it)


def _loads(it: Iterator) -> Any:
    ch = next(it)
    if ch == 0x69:  # 'i': int
        digits = takewhile(lambda x: x != 0x65, it)
        return int(bytes(digits))

    elif 48 <= ch <= 57:  # '0' < ch < '9': string | bytes
        length = [ch, *takewhile(lambda x: x != 0x3a, it)]
        length = int(''.join(chr(i) for i in length))
        return bytes(islice(it, length))

    elif ch == 0x6c:  # 'l': list
        arr = []
        while True:
            item = _loads(it)
            if item is None:
                break
            arr.append(item)

        return arr

    elif ch == 0x64:  # 'd': dictionary
        odict = OrderedDict()

        while True:
            key = _loads(it)
            if key is None:
                break
            value = _loads(it)

            odict[key] = value

        return odict

    elif ch == 0x65:  # 'e': end of the list or dict
        return None


def load(io: IO[bytes]) -> Any:
    """Reads benocded data from the io"""
    return loads(io.read())