from functools import wraps
from requests import get
from flask import jsonify

from trinityx_config_manager.parsers.ood_slurm_partitions import (
    OODSlurmPartitionsConfigParser,
)
from trinityx_config_manager.parsers.ood_slurm_nodes import (
    OODSlurmNodesConfigParser,
)

from config import settings, get_token, get_luna_url

def get_luna_nodes():
    """
    This method will fetch the luna nodes.
    """
    daemon_url = f"{get_luna_url()}/config/node"
    headers = {"x-access-tokens": get_token()}
    response = get(
        daemon_url,
        headers=headers,
        verify=settings.api.verify_certificate.lower() == "true",
    )
    if response.status_code != 200:
        raise Exception(
            f"Error {response.status_code} fetching luna nodes: {response.text}"
        )
    return response.json()


def managed_by_ood():
    """Check if the configuration files are managed by OOD."""
    partitions_parser = OODSlurmPartitionsConfigParser().read()
    nodes_parser = OODSlurmNodesConfigParser().read()
    # print(
    #     f"checking if partitions is managed by OOD: {partitions_parser.get_manager()}",
    #     file=sys.stderr,
    # )
    # print(
    #     f"checking if nodes is managed by OOD: {nodes_parser.get_manager()}",
    #     file=sys.stderr,
    # )
    return partitions_parser.is_manager() and nodes_parser.is_manager()