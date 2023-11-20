from functools import wraps
from config import settings, get_token, get_luna_url
from requests import get
from flask import jsonify



def wrap_errors(f):
    """Decorator to wrap errors in a JSON response."""
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"message": str(e)}), 500
    return wrapped

def nodes_to_groups(nodes):
    """Convert a dict with node names as keys and groups as values to a dict with node names as keys and groups as values."""
    tuples = [(node, attrs['group']) for node, attrs in nodes.items()]
    groups = {}
    for node, group in tuples:
        if group not in groups:
            groups[group] = []
        groups[group].append(node)
    return groups

def get_luna_nodes():
    """
    This method will fetch the luna nodes.
    """
    daemon_url = f'{get_luna_url()}/config/node'
    headers = {'x-access-tokens': get_token()}
    response = get(daemon_url, headers=headers, verify=settings.api.verify_certificate.lower() == 'true')
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code} fetching luna nodes: {response.text}")
    return response.json()