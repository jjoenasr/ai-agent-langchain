import json
from typing import Any

def try_parse(string: str) -> str | dict[str, Any]:
    try:
        return json.loads(string)
    except Exception:
        return string