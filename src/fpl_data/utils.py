from typing import Any, Dict, List


def drop_keys(d: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """Used to drop an array of keys from a dictionary"""
    return {k: v for k, v in d.items() if k not in keys}
