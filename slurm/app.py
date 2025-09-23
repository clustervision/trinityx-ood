# This code is part of the TrinityX software suite
# Copyright (C) 2023  ClusterVision Solutions b.v.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>

"""
This is main file. It will create flask object and serve the API's.
"""

__author__ = "Diego Sonaglia"
__copyright__ = "Copyright 2022, Luna2 Project[OOD]"
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = "ClusterVision Solutions Development Team"
__email__ = "support@clustervision.com"
__status__ = "Development"

import os
import sys
import tempfile
import itertools

from flask import Flask, render_template, request, jsonify, redirect, url_for
from slurmlint.linter import lint

from trinityx_config_blocks import ConfigFile
from trinityx_config_slurm  import (
    SlurmConfig,
    SlurmEntry,
    SlurmProperty,
    )
from trinityx_config_manager.hostlist import compress, expand
#from ..hostlist import compress, expand
# soon deprecated
from trinityx_config_manager.parsers.ood_base import (
    NodesConfig,
    PartitionsConfig,
    Node,
    Group,
    Partition,
    HWPreset,
)
from trinityx_config_manager.parsers.ood_slurm_partitions import (
    OODSlurmPartitionsConfigParser,
)
from trinityx_config_manager.parsers.ood_slurm_nodes import (
    OODSlurmNodesConfigParser,
)
from base.config import get_configs
# ----

from helpers import (
    get_luna_nodes,
    managed_by_ood,
)

CONFIGS = get_configs()
app = Flask(
    __name__, template_folder="templates", static_folder="static", static_url_path="/"
)
# app.config["TEMPLATES_AUTO_RELOAD"] = True


# add a wrapper to all the routes to catch errors
@app.errorhandler(Exception)
def wrap_errors(error):
    """Decorator to wrap errors in a JSON response."""
    if app.debug:
        raise error
    return jsonify({"message": str(error)}), 500


@app.context_processor
def inject_settings():
    return {"CONFIGS": CONFIGS}


def slurm_config(file):
    config_block = ConfigFile.read(file)
    block_content = config_block.get_managed_block("TrinityX")
    if block_content:
        lines = []
        for line in block_content.splitlines():
            if line.startswith('#'):
                lines.append(line[1:])
            else:
                lines.append(line)
        slurm_config = SlurmConfig.parse('\n'.join(lines))
        return slurm_config


def load_configuration(load_from_backup=False):
    """Load the configuration files from the default path."""

    configuration = {"nodes": [], "partitions": [], "groups": [], "hw_presets": []}

    nodes_configs = slurm_config('/etc/slurm/slurm-nodes.conf')
    if nodes_configs:
        nodesets = {}
        nodes = []
        groups = []
        nodeset_list = nodes_configs.object_aslist(entry='NodeSet')
        nodes_list = nodes_configs.object_aslist(entry='NodeName')
        nodesets = {data['NodeSet']: data['Nodes'] for data in nodeset_list}
        #groups = {}
        #for nodeset in nodesets.keys():
        #    expanded_nodes = expand(nodesets[nodeset]).split(",")
        #    nodesets[nodeset] = expanded_nodes
        #    for node in expanded_nodes:
        #       if node not in groups:
        #           groups[node] = nodeset
        for group in nodeset_list:
            print(f"{group['Nodes']}")
            expanded_nodes = expand(group['Nodes']).split(",")
            group_dict = {"name": group['NodeSet'], "node_names": expanded_nodes}
            groups.append(group_dict)
        configuration['groups'] = groups
        for node in nodes_list:
            group_name = None
            if node['NodeName'] in groups:
                group_name = groups[node['NodeName']]
            properties = { k:v for k,v in node.items() if k not in ['NodeName'] }
            node_dict = {"name": node['NodeName'], "group_name": group_name, "properties": properties, "hw_preset_name": None}
            nodes.append(node_dict)
        configuration['nodes'] = nodes

    partitions_configs = slurm_config('/etc/slurm/slurm-partitions.conf')
    if partitions_configs:
        partitions = []
        partitions_list = partitions_configs.object_aslist(entry='PartitionName')
        if partitions_list:
            for partition in partitions_list:
                properties = { k:v for k,v in partition.items() if k not in ['PartitionName','Nodes'] }
                node_names = None
                if partition['Nodes'] in nodesets.keys():
                    node_names = expand(nodesets[partition['Nodes']]).split(",")
                #if 'Nodes' in partition:
                #    node_names = [partition['Nodes']]
                partition_dict={"name": partition['PartitionName'], "properties": properties, "hw_preset_name": None, "node_names": node_names}
                partitions.append(partition_dict)
            configuration['partitions'] = partitions

    return configuration

    """
    # If the configuration is not provided, load it from the default path
    partitions_parser = OODSlurmPartitionsConfigParser()
    nodes_parser = OODSlurmNodesConfigParser()

    # Load the configuration files
    if load_from_backup:
        print(
            f"loading configuration from backup {partitions_parser.backup_filepath}",
            file=sys.stderr,
        )
        print(
            f"loading configuration from backup {nodes_parser.backup_filepath}",
            file=sys.stderr,
        )
        partitions_parser = partitions_parser.read(partitions_parser.backup_filepath)
        nodes_parser = nodes_parser.read(nodes_parser.backup_filepath)
    else:
        partitions_parser = partitions_parser.read()
        nodes_parser = nodes_parser.read()

    partitions_config = partitions_parser.get_content()
    nodes_config = nodes_parser.get_content()

    configuration = nodes_config
    configuration.partitions = partitions_config.partitions

    return configuration
    """

def save_configuration(configuration):
    """Save the configuration files to the default path."""

    # If the configuration is not provided, load it from the default path
    partitions_parser = OODSlurmPartitionsConfigParser()
    nodes_parser = OODSlurmNodesConfigParser()

    # Load the configuration files
    partitions_parser = partitions_parser.read()
    nodes_parser = nodes_parser.read()

    partitions_parser.set_content(configuration)
    nodes_parser.set_content(configuration)

    partitions_parser.write(backup=True)
    nodes_parser.write(backup=True)

    return True


def parse_raw_configuration(raw_configuration):
    raw_groups = []
    group_nodes = [
        node for node in raw_configuration["nodes"] if node.get("group_name")
    ]
    sorted_nodes = sorted(group_nodes, key=lambda node: node["group_name"])
    for group_name, nodes in itertools.groupby(
        sorted_nodes, key=lambda node: node["group_name"]
    ):
        node_names = [node["name"] for node in nodes]
        raw_groups.append({"name": group_name, "node_names": node_names})
    for node in raw_configuration["nodes"]:
        node.pop("group_name", None)
        node["properties"] = {k: v for k, v in node.get("properties", {}).items()}

    nodes = [Node(**node) for node in raw_configuration["nodes"] or []]
    groups = [Group(**group) for group in raw_groups or []]
    partitions = [
        Partition(**partition) for partition in raw_configuration["partitions"] or []
    ]
    hw_presets = [
        HWPreset(**hw_preset) for hw_preset in raw_configuration["hw_presets"] or []
    ]

    config = NodesConfig(
        nodes=nodes, groups=groups, partitions=partitions, hw_presets=hw_presets
    )
    return config


# Pages
@app.route("/")
def index_route():
    """Render the index page."""
    message = request.args.get("message")

    if not managed_by_ood():
        return render_template("pages/unmanaged.html")
    return render_template(
        "pages/index.html",
        messages=[message] if message else [],
    )


@app.route("/set_manager")
def set_manager_route():
    """Set the manager of the managed block."""
    partitions_parser = OODSlurmPartitionsConfigParser().read()
    nodes_parser = OODSlurmNodesConfigParser().read()
    partitions_parser.set_manager(OODSlurmPartitionsConfigParser.MANAGER_NAME)
    nodes_parser.set_manager(OODSlurmNodesConfigParser.MANAGER_NAME)
    partitions_parser.write(force=True)
    nodes_parser.write(force=True)
    return redirect(url_for("index_route"))


# Actions
@app.route("/json/configuration/hw_presets", methods=["GET"])
def get_hw_presets_route():
    load_from_backup = request.args.get("load_from_backup")
    configuration = load_configuration(load_from_backup=load_from_backup) #.to_dict()
    return jsonify(configuration["hw_presets"])


"""
[
  {
    "group_name": "compute",
    "hw_preset_name": null,
    "name": "node001",
    "properties": {
      "State": "UNKNOWN"
    }
  },
"""

@app.route("/json/configuration/nodes", methods=["GET"])
def get_nodes_route():
    load_from_backup = request.args.get("load_from_backup")
    configuration = load_configuration(load_from_backup=load_from_backup)#.to_dict()
    nodes = configuration["nodes"]

    for node in nodes:
        group_name = next(
            (
                group["name"]
                for group in configuration["groups"]
                if node["name"] in group["node_names"]
            ),
            None,
        )
        node["group_name"] = group_name
    return jsonify(nodes)

"""
[
  {
    "hw_preset_name": null,
    "name": "compute",
    "node_names": [
      "compute"
    ],
    "properties": {}
  }
]
"""

@app.route("/json/configuration/partitions", methods=["GET"])
def get_partitions_route():
    load_from_backup = request.args.get("load_from_backup")
    configuration = load_configuration(load_from_backup=load_from_backup) #.to_dict()
    partitions = configuration["partitions"]
    return jsonify(partitions)
    

# TWAN---------------------------------------------------------
    """
    inside load_configuration
      call for:
        BaseConfigParser - read the config file:
            lines = {
                "before": [],
                "managed": [],
                "after": [],
            } --> raw lines. before/after are outside the managed block
           self.content = self.parse_managed_block(self.lines["managed"]) # raw data in, PartitionsConfig(partitions) out
           get_content return self.content

        partitions_parser = OODSlurmPartitionsConfigParser()
        nodes_parser = OODSlurmNodesConfigParser()
        partitions_config = partitions_parser.get_content() # == PartitionsConfig(partitions)
        nodes_config = nodes_parser.get_content()
        configuration = nodes_config
        configuration.partitions = partitions_config.partitions # == Partition -> self.name, self.properties...
        # configuration is 
        return configuration

    inside OODSlurmPartitionsConfigParser(BaseConfigParser):
        for each managed line:
          parse, key=value -- hw_preset split from properties. node_names == ref to group in slurm-nodes.conf
          partitions.append(Partition(name, node_names, properties, hw_preset)) # <--------------------------------------------------------------
          partition_configs = PartitionsConfig(partitions)
          return partition_configs == PartitionsConfig(partitions)

    inside Partition: # is class - bevat functions
        self.name = name
        self.node_names = node_names
        self.properties = {k:v for k,v in properties.items() if k not in HWPreset.MANAGED_PROPERTIES}
        self.hw_preset_name = hw_preset_name # is in config like comment ->  # HWPreset=name
        def to_dict(self):
            return {"name": self.name, "node_names": self.node_names, "properties": self.properties, "hw_preset_name": self.hw_preset_name}

    inside PartitionsConfig: # bevat functions - is class
        def __init__(self, partitions: List[Partition]):
            self.partitions = partitions
        def to_dict:
            return {"partitions": [partition.to_dict() for partition in self.partitions]}

    partitions in app.route contect == dict !!!
           {"partitions": [
              {"name": self.name, "node_names": self.node_names, "properties": self.properties, "hw_preset_name": self.hw_preset_name},
              {"name": self.name, "node_names": self.node_names, "properties": self.properties, "hw_preset_name": self.hw_preset_name}
           ]}

    """
###-----------------------------------------------


@app.route("/json/configuration/save", methods=["POST"])
def set_configuration_route():
    """Set the configuration."""
    raw_configuration = request.json
    configuration = parse_raw_configuration(raw_configuration)
    save_configuration(configuration)
    output = {
        "redirect": url_for(
            "index_route",
            message="Configuration saved successfully, restart the slurmctld service to apply the changes.",
        )
    }
    return jsonify(output)


@app.route("/json/configuration/preview", methods=["POST"])
def configuration_preview_route():
    """Render the configuration preview."""
    if request.args.get("load_from_backup", False):
        configuration = load_configuration(load_from_backup=True)
    else:
        configuration = parse_raw_configuration(request.json)

    partitions_parser = OODSlurmPartitionsConfigParser().read()
    partitions_parser.set_content(configuration)
    partitions_preview_lines = partitions_parser.dump_lines(marked=True)

    nodes_parser = OODSlurmNodesConfigParser().read()
    nodes_parser.set_content(configuration)
    nodes_preview_lines = nodes_parser.dump_lines(marked=True)

    return render_template(
        "components/configuration_preview.html",
        partitions_preview_lines=partitions_preview_lines,
        nodes_preview_lines=nodes_preview_lines,
    )


@app.route("/json/configuration/test", methods=["POST"])
def test_configuration_route():
    configuration = parse_raw_configuration(raw_configuration=request.json)

    node_lines = (
        OODSlurmNodesConfigParser().read().set_content(configuration).dump_lines()
    )
    partition_lines = (
        OODSlurmPartitionsConfigParser().read().set_content(configuration).dump_lines()
    )

    configuration_lines = node_lines + partition_lines
    configuration_lines = [l for l in configuration_lines if not l.startswith("NodeSet=")]
    configuration_text = "".join(configuration_lines)

    res = lint(configuration_text)

    errors = res.get("errors", [])

    expanded_errors = [
        f"{configuration_lines[idx-1]}: {error}" for idx, error in errors
    ]
    if not errors:
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "danger", "errors": expanded_errors}), 200


@app.route("/json/luna/nodes", methods=["GET"])
def import_luna_nodes_route():
    """Load the luna nodes from the luna daemon."""
    try:
        nodes = get_luna_nodes()
        return jsonify(nodes), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


if __name__ == "__main__":
    #app.run()
    # Sumit Testing Comments
    dev_context=(
             '/trinity/local/etc/ssl/twans-ansible-el9.taurusgroup.one.crt',
             '/trinity/local/etc/ssl/twans-ansible-el9.taurusgroup.one.key'
         )
    app.run(host='0.0.0.0', port=7755, debug= True, ssl_context=dev_context)
