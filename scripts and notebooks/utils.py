import json, requests, time


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
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        response = response.json()
        return response
    else:
        print(response.text)
        retry_after = int(response.headers['Retry-After'])
        time.sleep(retry_after)
        response = call_with_retry(url, headers, params, retries+1)
        return response
