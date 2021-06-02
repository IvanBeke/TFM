import json, requests, time, os
import dill as pickle

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


def call_with_retry(url: str, headers: dict, params: dict = {}, retries: int = 1) -> dict:
    """Call the Riot API with retries in case the request fails

    Parameters
    ----------
    url : str
    headers : dict
    params : dict, optional by default {}
    retries : int, optional by default 1

    Returns
    -------
    dict
    """
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        response = response.json()
        return response
    else:
        retry_after = int(response.headers['Retry-After'])
        time.sleep(retry_after)
        response = call_with_retry(url, headers, params, retries+1)
        return response


def save_execution_state(object, path: str):
    """Serialize an object

    Parameters
    ----------
    object : Any
    path : str
    """
    with open(path, 'wb') as f:
        pickle.dump(object, f)


def load_execution_state(path: str, default):
    """Load a serialized object, return default if it doesn't exist

    Parameters
    ----------
    path : str
    default : Any

    Returns
    -------
    Any
    """
    if os.path.exists(path) and os.stat(path).st_size != 0:
        with open(path, 'rb') as f:
            object = pickle.load(f)
    else:
        object = default
    return object