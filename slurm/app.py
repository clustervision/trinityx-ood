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
import re
import tempfile
import itertools

from flask import Flask, render_template, request, jsonify, redirect, url_for
from slurmlint.linter import lint

from trinityx_config_blocks import ConfigFile
from trinityx_config_slurm  import (
    SlurmConfig,
    SlurmEntry,
    SlurmProperty,
    Generate,
)
from trinityx_config_manager.hostlist import compress, expand
#from ..hostlist import compress, expand
"""
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
# ----
"""
from base.config import (
    get_configs,
    get_slurm_files,
    get_slurm_backup_files,
    MANAGER_NAME,
    MANAGER_NAME_OOD,
    MANAGED_PROPERTIES,
)

from helpers import (
    get_luna_nodes,
    managed_by_ood,
)

CONFIGS = get_configs()
SLURM_FILES = get_slurm_files()
SLURM_BACKUP_FILES = get_slurm_backup_files()
sys.stdout.write(f"SLURM: {SLURM_FILES}\n")

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


def check_managed_block(file,block_name=MANAGER_NAME):
    config_file = ConfigFile.read(file)
    block_managed = config_file.ismanaged(block_name)
    if block_managed:
        return True
    return False

def slurm_config(file,block_name=MANAGER_NAME):
    config_block = ConfigFile.read(file)
    block_content = config_block.get_managed_block(block_name)
    if block_content:
        lines = []
        for line in block_content.splitlines():
            if line.startswith('#'):
                lines.append(line[1:])
            else:
                lines.append(line)
        slurm_config = SlurmConfig.parse('\n'.join(lines))
        return slurm_config


def load_configuration(slurm_files=SLURM_FILES):
    """Load the configuration files from the default path."""

    configuration = {"nodes": [], "partitions": [], "groups": [], "hw_presets": []}

    hw_presets = {'nodes': {}, 'partitions': {}}
    defaults_configs = slurm_config(slurm_files['nodes'],'Defaults')
    if defaults_configs:
        defaults = []
        defaults_list = defaults_configs.object_aslist(entry='HWPresetName')
        for default in defaults_list:
            properties = { k:v for k,v in default.items() if k not in ['HWPresetName'] }
            default_dict = {"name": default['HWPresetName'], "properties": properties}
            defaults.append(default_dict)
        configuration['hw_presets'] = defaults
        # prefill for below nodes/partitions
        defaults_comments_nodes = defaults_configs.comment(name='Nodes')
        defaults_comments_partitions = defaults_configs.comment(name='Partitions')
        if defaults_comments_nodes:
            for key, nodes in defaults_comments_nodes.items():
                if key.startswith('HWPresetName'):
                    _, hw_preset = key.split('=',1)
                    for node in expand(nodes).split(","):
                        hw_presets['nodes'][node] = hw_preset
        if defaults_comments_partitions:
            for key, partitions in defaults_comments_partitions.items():
                if key.startswith('HWPresetName'):
                    _, hw_preset = key.split('=',1)
                    for partition in expand(partitions).split(","):
                        hw_presets['partitions'][partition] = hw_preset

    nodes_configs = slurm_config(slurm_files['nodes'])
    if not nodes_configs:
        nodes_configs = slurm_config(slurm_files['nodes'],MANAGER_NAME_OOD)
    if nodes_configs:
        nodesets = {}
        nodes = []
        groups = []
        nodeset_list = nodes_configs.object_aslist(entry='NodeSet')
        nodes_list = nodes_configs.object_aslist(entry='NodeName')
        nodesets = {data['NodeSet']: data['Nodes'] for data in nodeset_list}
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
            hw_preset = None
            if node['NodeName'] in hw_presets['nodes']:
                hw_preset = hw_presets['nodes'][node['NodeName']]
            properties = { k:v for k,v in node.items() if k not in ['NodeName'] }
            node_dict = {"name": node['NodeName'], "group_name": group_name, "properties": properties, "hw_preset_name": hw_preset}
            nodes.append(node_dict)
        configuration['nodes'] = nodes

    partitions_configs = slurm_config(slurm_files['partitions'])
    if not partitions_configs:
        partitions_configs = slurm_config(slurm_files['partitions'],MANAGER_NAME_OOD)
    if partitions_configs:
        partitions = []
        partitions_list = partitions_configs.object_aslist(entry='PartitionName')
        if partitions_list:
            for partition in partitions_list:
                node_names = None
                if partition['Nodes'] in nodesets.keys():
                    node_names = expand(nodesets[partition['Nodes']]).split(",")
                hw_preset = None
                if partition['PartitionName'] in hw_presets['partitions']:
                    hw_preset = hw_presets['partitions'][partition['PartitionName']]
                properties = { k:v for k,v in partition.items() if k not in ['PartitionName','Nodes'] }
                partition_dict={"name": partition['PartitionName'], "properties": properties, "hw_preset_name": hw_preset, "node_names": node_names}
                partitions.append(partition_dict)
            configuration['partitions'] = partitions

    return configuration


def init_tmp_files(slurm_files):
    for slurm_file in ['nodes', 'partitions', 'gres']:
        if len(slurm_files[slurm_file]) > 5 and slurm_files[slurm_file].startswith("/"):
            with open(slurm_files[slurm_file], "w") as file:
                file.write("#### Defaults Managed block start ####\n")
                file.write("#### Defaults Managed block end   ####\n\n")
                file.write("#### "+MANAGER_NAME+" Managed block start ####\n")
                file.write("#### "+MANAGER_NAME+" Managed block end   ####\n")

def remove_tmp_files(slurm_files):
    for slurm_file in ['nodes', 'partitions', 'gres']:
        if len(slurm_files[slurm_file]) > 5 and slurm_files[slurm_file].startswith("/"):
            if os.path.exists(slurm_files[slurm_file]):
               os.remove(slurm_files[slurm_file])

def set_manager(OOD=False, slurm_files=SLURM_FILES):    
    new_manager = f"# {MANAGER_NAME} "
    old_manager = f"# {MANAGER_NAME_OOD} "
    if OOD:
        new_manager = f"# {MANAGER_NAME_OOD} "
        old_manager = f"# {MANAGER_NAME} "
    sys.stdout.write(f"MGR: {new_manager}\n")

    for slurm_file in ['nodes','partitions','gres']:
        lines = []
        with open(slurm_files[slurm_file]) as file:
            for line in file:
                sys.stdout.write(f"IN: {line}")
                line = re.sub(r""+old_manager, new_manager, line)
                sys.stdout.write(f"OUT: {line}\n")
                lines.append(line)
        if lines:
            with open(slurm_files[slurm_file], "w") as file:
                for line in lines:
                    file.write(line)


def save_configuration(configuration, slurm_files=SLURM_FILES, backup=True, manager=MANAGER_NAME):
    """Save the configuration files to the default path."""    

    sys.stdout.write(f"FILES: {slurm_files}\n")
    fullset = []
    if 'groups' in configuration:
        for group in configuration['groups']:
            for node in group['node_names']:
                fullset.append({'name': node, 'group': group['name']})
    #
    raw_nodes_block = render_raw_nodes_defaults(configuration,slurm_files)
    nodes_file = ConfigFile.read(slurm_files['nodes'])
    block_managed = nodes_file.ismanaged("Defaults")
    if block_managed:
        nodes_file.set_managed_block("Defaults", raw_nodes_block)
        nodes_file.write(slurm_files['nodes'])
    #
    raw_partitions_block = render_raw_partitions_defaults(configuration,slurm_files)
    partitions_file = ConfigFile.read(slurm_files['partitions'])
    block_managed = partitions_file.ismanaged("Defaults")
    if block_managed:
        partitions_file.set_managed_block("Defaults", raw_partitions_block)
        partitions_file.write(slurm_files['partitions'])
    #
    status = Generate().all_configs(nodes=fullset, configs=slurm_files, manager=manager)
    if status:
        return True
    else:
        return False


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

    nodes = raw_configuration["nodes"] or []
    groups = raw_groups or []
    partitions = raw_configuration["partitions"] or []
    hw_presets = raw_configuration["hw_presets"] or []

    configuration = {"nodes": nodes, "partitions": partitions, "groups": groups, "hw_presets": hw_presets}
    sys.stdout.write(f"RAW PARSED: {configuration}\n")
    return configuration



def render_raw_nodes_defaults(configuration, slurm_files=SLURM_FILES):
    """
    we generate the raw lines that go into the Defaults blocks.
    For each node and partition we generate the correspondent lines, as such
    that the Generate part can generate what will go into the "TrinityX" managed blocks
    """
    defaults_configs = slurm_config(slurm_files['nodes'],'Defaults')
    try:
        defaults = defaults_configs.object(multiple=False)
    except:
        defaults = {}
    raw_block = ''

    hw_presets = {}
    hw_presets_addons = {}
    # let's find if there are any manually added properties:
    for default_preset, properties in defaults.items():
        if default_preset.startswith('NodeName'):
            addons = []
            items = properties.split(' ')
            #del items[0] # first entry is 'NodeName'
            for item in items:
                key, value = item.split('=')
                if (key not in MANAGED_PROPERTIES) and (item not in addons):
                    addons.append(item)
            if addons:
                hw_presets_addons[default_preset] = ' '.join(addons)
    sys.stdout.write(f"ADDON: {hw_presets_addons}\n")

    if 'hw_presets' in configuration:
        hw_preset_nodes = {}
        hw_preset_partitions = {}
        # what nodes are using the preset:
        if 'nodes' in configuration:
            for node in configuration['nodes']:
                if node['hw_preset_name']:
                    if node['hw_preset_name'] not in hw_preset_nodes:
                        hw_preset_nodes[node['hw_preset_name']] = []
                    hw_preset_nodes[node['hw_preset_name']].append(node['name'])
        # what partitions are using the preset:
        if 'partitions' in configuration:
            for partition in configuration['partitions']:
                if partition['hw_preset_name']:
                    if partition['hw_preset_name'] not in hw_preset_partitions:
                        hw_preset_partitions[partition['hw_preset_name']] = []
                    hw_preset_partitions[partition['hw_preset_name']].append(partition['name'])
        # now let's build a per node preset list and the hw presets themselves:
        for hw_preset in configuration['hw_presets']:
            if 'properties' in hw_preset:
                hw_preset_line="HWPresetName="+hw_preset['name']+" "
                hw_preset_properties = ""
                for key, value in hw_preset['properties'].items():
                    hw_preset_line+=f"{key}={value} "
                    hw_preset_properties+=f"{key}={value} "
                hw_preset_line+="# "
                if hw_preset['name'] in hw_preset_nodes:
                    hw_preset_line+="Nodes="+compress(','.join(hw_preset_nodes[hw_preset['name']]))+" "
                    for node in hw_preset_nodes[hw_preset['name']]:
                        properties_addons = ""
                        if "NodeName="+node in hw_presets_addons:
                            properties_addons = hw_presets_addons["NodeName="+node]+" "
                        node_preset_line="NodeName="+node+" "+hw_preset_properties+properties_addons+" # HWPreset="+hw_preset["name"]
                        hw_presets["NodeName="+node]=node_preset_line
                if hw_preset['name'] in hw_preset_partitions:
                    hw_preset_line+="Partitions="+compress(','.join(hw_preset_partitions[hw_preset['name']]))
                    for partition in hw_preset_partitions[hw_preset['name']]:
                        partition_preset_line="PartitionName="+partition+" "+hw_preset_properties+" # HWPreset="+hw_preset["name"]
                        hw_presets["PartitionName="+partition]=partition_preset_line
                hw_presets["HWPresetName="+hw_preset['name']]=hw_preset_line
    # now we build the raw content:
    for hw_preset, entry in sorted(hw_presets.items()):
        raw_block+="# "+entry+"\n"
        if hw_preset in defaults:
            del defaults[hw_preset]
    for hw_preset, entry in sorted(defaults.items()):
        raw_block+="# "+hw_preset+" "+entry+"\n"

    #sys.stdout.write(f"RENDER NODE RAW BLOCK:\n{raw_block}\n")
    return raw_block


def render_raw_partitions_defaults(configuration, slurm_files=SLURM_FILES):
    """
    we generate the raw lines that go into the Defaults blocks.
    For each partition we generate the correspondent lines, as such
    that the Generate part can generate what will go into the "TrinityX" managed blocks
    """
    defaults_configs = slurm_config(slurm_files['partitions'],'Defaults')
    try:
        defaults = defaults_configs.object(multiple=False)
    except:
        defaults = {}
    raw_block = ''

    properties = {}
    if 'partitions' in configuration:
        for partition in configuration['partitions']:
            if 'properties' in partition:
                properties_line="PartitionName="+partition['name']+" "
                for key, value in partition['properties'].items():
                    properties_line+=f"{key}={value} "
                properties["PartitionName="+partition['name']]=properties_line
    for property_preset, entry in sorted(properties.items()):
        raw_block+="# "+entry+"\n"
        if property_preset in defaults:
            del defaults[property_preset]
    for property_preset, entry in sorted(defaults.items()):
        raw_block+="# "+property_preset+" "+entry+"\n"

    #sys.stdout.write(f"RENDER PART RAW BLOCK:\n{raw_block}\n")
    return raw_block


# Pages
@app.route("/")
def index_route():
    """Render the index page."""
    message = request.args.get("message")

    #if not managed_by_ood():
    #    return render_template("pages/unmanaged.html")
    return render_template(
        "pages/index.html",
        messages=[message] if message else [],
    )


@app.route("/set_manager")
def set_manager_route():
    """Set the manager of the managed block."""
    """
    partitions_parser = OODSlurmPartitionsConfigParser().read()
    nodes_parser = OODSlurmNodesConfigParser().read()
    partitions_parser.set_manager(OODSlurmPartitionsConfigParser.MANAGER_NAME)
    nodes_parser.set_manager(OODSlurmNodesConfigParser.MANAGER_NAME)
    partitions_parser.write(force=True)
    nodes_parser.write(force=True)
    """
    who = request.args.get("manager")
    OOD = False
    if who == "OOD":
        OOD = True
    set_manager(OOD=OOD,slurm_files=SLURM_FILES)
    return redirect(url_for("index_route"))


@app.route("/get_manager")
def get_manager_route():
    """Get the manager of the managed block."""
    """
    who = request.args.get("manager")
    OOD = False
    if who == "OOD":
        OOD = True
    set_manager(OOD=OOD,slurm_files=SLURM_FILES)
    return redirect(url_for("index_route"))
    """
    return jsonify({"config": {"manager": MANAGER_NAME}})


@app.route("/whois_manager")
def whois_manager_route():
    """Who is the manager of the managed block."""
    file = SLURM_FILES['nodes']
    if check_managed_block(file, MANAGER_NAME):
        return jsonify({"config": {"manager": "default"}})
    elif check_managed_block(file, MANAGER_NAME_OOD):
        return jsonify({"config": {"manager": "OOD"}})
    return jsonify({"config": {"manager": "manual"}})


"""
[
  {
    "name": "test",
    "properties": {
      "Boards": "2",
      "CoresPerSocket": "2",
      "RealMemory": "6000",
      "SocketsPerBoard": "12",
      "ThreadsPerCore": "2"
    }
  }
]
"""

# Actions
@app.route("/json/configuration/hw_presets", methods=["GET"])
def get_hw_presets_route():
    load_from_backup = request.args.get("load_from_backup")
    slurm_files = SLURM_FILES
    if load_from_backup:
        slurm_files = SLURM_BACKUP_FILES
    configuration = load_configuration(slurm_files=slurm_files)
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
    slurm_files = SLURM_FILES
    if load_from_backup:
        slurm_files = SLURM_BACKUP_FILES
    configuration = load_configuration(slurm_files=slurm_files)
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
    slurm_files = SLURM_FILES
    if load_from_backup:
        slurm_files = SLURM_BACKUP_FILES
    configuration = load_configuration(slurm_files=slurm_files)
    partitions = configuration["partitions"]
    return jsonify(partitions)
    

@app.route("/json/configuration/save", methods=["POST"])
def set_configuration_route():
    """Set the configuration."""
    raw_configuration = request.json
    configuration = parse_raw_configuration(raw_configuration)

    file = SLURM_FILES['nodes']
    if check_managed_block(file, MANAGER_NAME):
        manager = MANAGER_NAME
    elif check_managed_block(file, MANAGER_NAME_OOD):
        manager = MANAGER_NAME_OOD
    status = save_configuration(configuration=configuration,
                                slurm_files=SLURM_FILES,
                                backup=True, manager=manager)
    message = f"Configuration saved successfully, restart the slurmctld service to apply the changes."
    if not status:
        message = f"Problem encountered during saving configuration. Please verify with ood logs."
    output = {
        "redirect": url_for(
            "index_route",
            message=message,
        )
    }
    return jsonify(output)


"""
raw_config + plus preview received:
{
  "hw_presets": [
    {
      "name": "test",
      "properties": {
        "Boards": "2",
        "CoresPerSocket": "2",
        "RealMemory": "6000",
        "SocketsPerBoard": "12",
        "State": "UNKNOWN",
        "ThreadsPerCore": "2"
      }
    }
  ],
  "nodes": [
    {
      "group_name": "compute",
      "hw_preset_name": null,
      "name": "node001",
      "properties": {
        "Boards": "1",
        "CoresPerSocket": "2",
        "RealMemory": "2000",
        "SocketsPerBoard": "1",
        "State": "UNKNOWN",
        "ThreadsPerCore": "2"
      }
    }
    ...
  ],
  "partitions": [
    {
      "hw_preset_name": "test",
      "name": "compute",
      "node_names": [
        "node001",
        "node002",
        "demonode"
      ],
      "properties": {}
    },
    ...
  ]
}

"""

@app.route("/json/configuration/preview", methods=["POST"])
def configuration_preview_route():
    """Render the configuration preview."""
    if request.args.get("load_from_backup", False):
        config_block = ConfigFile.read(SLURM_BACKUP_FILES['nodes'])
        nodes_preview_lines = config_block.dump()
        config_block = ConfigFile.read(SLURM_BACKUP_FILES['partitions'])
        partitions_preview_lines = config_block.dump()
    else:
        configuration = parse_raw_configuration(request.json)
        sys.stdout.write(f"PREVIEW: {configuration}\n")
        tmp_configs = {
            'nodes': '/tmp/slurm-nodes.conf',
            'partitions': '/tmp/slurm-partitions.conf',
            'gres': '/tmp/gres.conf'}
        init_tmp_files(tmp_configs)
        save_configuration(configuration=configuration, 
                           slurm_files=tmp_configs, 
                           backup=False, manager=MANAGER_NAME)

        config_block = ConfigFile.read(tmp_configs['nodes'])
        nodes_preview_lines = config_block.dump()
        config_block = ConfigFile.read(tmp_configs['partitions'])
        partitions_preview_lines = config_block.dump()
        remove_tmp_files(tmp_configs)

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
