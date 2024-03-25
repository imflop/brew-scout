import orjson
import typing as t


def orjson_dumps(v: t.Any, *, default: t.Any) -> str:
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()
