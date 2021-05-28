import json


def build_url(region: str, base_url: str, endpoint: str) -> str:
    """Build complete url to call.

    Parameters
    ----------
    region : str
    base_url : str
    endpoint : str

    Returns
    -------
    str
        Full url to call
    """
    return f'https://{region}.{base_url}{endpoint}'

def save_json(obj: dict, file: str) -> None:
    """Save dict as json file.

    Parameters
    ----------
    obj : dict
    file : dict
    """
    with open(f'outputs/{file}', 'w+') as f:
        json.dump(obj, f, indent=4)

def load_json(file: str) -> dict:
    """Load a json file and return its dict.

    Parameters
    ----------
    file : str

    Returns
    -------
    dict
    """
    with open(file, 'r') as f:
        obj = json.load(f)
    return obj