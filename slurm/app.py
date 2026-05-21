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
import shutil
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
from trinityx_config_slurm.utils.hostlist import compress, expand
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




home_dir = os.path.expanduser("~")
if os.path.exists(home_dir) and os.access(home_dir, os.R_OK | os.W_OK):
    TOKEN_FILE = f"{home_dir}/.luna-token.dat"
else:
    TOKEN_FILE = {
        "error": f"The home directory '{home_dir}' does not exist or lacks read/write permissions."
    }

INI_FILE = '/trinity/local/ondemand/3.0/config/luna.ini'
CONFIGS = get_configs()
SLURM_FILES = get_slurm_files()
SLURM_BACKUP_FILES = get_slurm_backup_files()
#sys.stdout.write(f"SLURM: {SLURM_FILES}\n")

app = Flask(
    __name__, template_folder="templates", static_folder="static", static_url_path="/"
)
# app.config["TEMPLATES_AUTO_RELOAD"] = True
@app.before_request
def validate_home_directory():
    """
    Validate the $HOME directory of the user before proceeding further.
    """
    if request.path.startswith('/static/'):
        return
    if isinstance(TOKEN_FILE, dict):
        return render_template("error.html", table="Slurm", data="", error=TOKEN_FILE["error"])
    file_check = os.path.isfile(INI_FILE)
    if file_check is False:
        return render_template("error.html", table="Slurm", data="", error=f'Luna Configuration File: <strong>{INI_FILE}</strong> Not Found')
    read_check = os.access(INI_FILE, os.R_OK)
    if read_check is False:
        return render_template("error.html", table="Slurm", data="", error=f'Luna Configuration File: <strong>{INI_FILE}</strong> is not readable.')
    return None

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


def load_gres_configuration(slurm_files=SLURM_FILES):
    """Load GRES presets and per-node/partition GRES assignments from gres.conf."""
    gres_presets = []
    gres_nodes   = {}   # node_name  -> [preset_name, ...]
    gres_parts   = {}   # part_name  -> [preset_name, ...]

    gres_file = slurm_files.get('gres')
    if not gres_file or not os.path.exists(gres_file):
        return gres_presets, gres_nodes, gres_parts

    # Read the Defaults block — preset definitions live here as comments
    defaults_cfg = slurm_config(gres_file, 'Defaults')
    if defaults_cfg:
        preset_list = defaults_cfg.object_aslist(entry='GRESPresetName')
        for p in preset_list:
            props = {k: v for k, v in p.items() if k != 'GRESPresetName'}
            # no_consume is stored as string "true"/"false"
            if 'no_consume' in props:
                props['no_consume'] = props['no_consume'].lower() == 'true'
            gres_presets.append({"name": p['GRESPresetName'], "properties": props})

        # Read comment annotations for node/partition assignments
        node_comments = defaults_cfg.comment(name='Nodes')
        part_comments = defaults_cfg.comment(name='Partitions')
        if node_comments:
            for key, val in node_comments.items():
                if key.startswith('GRESPresetName'):
                    _, preset_name = key.split('=', 1)
                    for node in expand(val).split(','):
                        gres_nodes.setdefault(node, [])
                        if preset_name not in gres_nodes[node]:
                            gres_nodes[node].append(preset_name)
        if part_comments:
            for key, val in part_comments.items():
                if key.startswith('GRESPresetName'):
                    _, preset_name = key.split('=', 1)
                    for part in expand(val).split(','):
                        gres_parts.setdefault(part, [])
                        if preset_name not in gres_parts[part]:
                            gres_parts[part].append(preset_name)

    return gres_presets, gres_nodes, gres_parts


def load_configuration(slurm_files=SLURM_FILES):
    """Load the configuration files from the default path."""

    configuration = {"nodes": [], "partitions": [], "groups": [], "hw_presets": [], "gres_presets": []}

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

    # Load GRES presets and assignments
    gres_presets, gres_nodes, gres_parts = load_gres_configuration(slurm_files)
    configuration['gres_presets'] = gres_presets

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
            gres_preset_names = gres_nodes.get(node['NodeName'], [])
            properties = { k:v for k,v in node.items() if k not in ['NodeName'] }
            node_dict = {"name": node['NodeName'], "group_name": group_name, "properties": properties,
                         "hw_preset_name": hw_preset, "gres_preset_names": gres_preset_names}
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
                gres_preset_names = gres_parts.get(partition['PartitionName'], [])
                properties = { k:v for k,v in partition.items() if k not in ['PartitionName','Nodes'] }
                partition_dict={"name": partition['PartitionName'], "properties": properties,
                                "hw_preset_name": hw_preset, "node_names": node_names,
                                "gres_preset_names": gres_preset_names}
                partitions.append(partition_dict)
            configuration['partitions'] = partitions

    return configuration


def init_tmp_files(slurm_files):
    for slurm_file in ['nodes', 'partitions', 'gres']:
        if len(slurm_files[slurm_file]) > 5 and slurm_files[slurm_file].startswith("/"):
            with open(slurm_files[slurm_file], "w") as file:
            #with slurm_files[slurm_file] as file:
                file.write("#### Defaults Managed block start ####\n")
                file.write("#### Defaults Managed block end   ####\n\n")
                file.write("#### "+MANAGER_NAME+" Managed block start ####\n")
                file.write("#### "+MANAGER_NAME+" Managed block end   ####\n")
        else:
            raise Exception(f"File name requirement not met for {slurm_files[slurm_file]}")

def save_tmp_files(configuration):
    my_home = os.path.expanduser("~/")
    tmp_configs = {
        'nodes': my_home+'/slurm-nodes.conf',
        'partitions': my_home+'/slurm-partitions.conf',
        'gres': my_home+'/gres.conf'}
    try:
        init_tmp_files(tmp_configs)
        save_configuration(configuration=configuration,
                           slurm_files=tmp_configs,
                           backup=False, manager=MANAGER_NAME)

        config_block = ConfigFile.read(tmp_configs['nodes'])
        nodes_preview_lines = config_block.dump()
        config_block = ConfigFile.read(tmp_configs['partitions'])
        partitions_preview_lines = config_block.dump()
        config_block = ConfigFile.read(tmp_configs['gres'])
        gres_preview_lines = config_block.dump()
    except Exception as exp:
        nodes_preview_lines = f"Problem generating preview: {exp}\n\n"
        partitions_preview_lines = f"Problem generating preview: {exp}\n\n"
        gres_preview_lines = f"Problem generating preview: {exp}\n\n"
    remove_tmp_files(tmp_configs)
    return nodes_preview_lines, partitions_preview_lines, gres_preview_lines

def remove_tmp_files(slurm_files):
    for slurm_file in ['nodes', 'partitions', 'gres']:
        #    slurm_files[slurm_file].close()
        if len(slurm_files[slurm_file]) > 5 and slurm_files[slurm_file].startswith("/"):
            if os.path.exists(slurm_files[slurm_file]):
               os.remove(slurm_files[slurm_file])

def set_manager(OOD=False, slurm_files=SLURM_FILES):    
    new_manager = f"# {MANAGER_NAME} "
    old_manager = f"# {MANAGER_NAME_OOD} "
    if OOD:
        new_manager = f"# {MANAGER_NAME_OOD} "
        old_manager = f"# {MANAGER_NAME} "
    #sys.stdout.write(f"MGR: {new_manager}\n")

    for slurm_file in ['nodes','partitions','gres']:
        lines = []
        with open(slurm_files[slurm_file]) as file:
            for line in file:
                #sys.stdout.write(f"IN: {line}")
                line = re.sub(r""+old_manager, new_manager, line)
                #sys.stdout.write(f"OUT: {line}\n")
                lines.append(line)
        if lines:
            with open(slurm_files[slurm_file], "w") as file:
                for line in lines:
                    file.write(line)


def save_configuration(configuration, slurm_files=SLURM_FILES, backup=True, manager=MANAGER_NAME):
    """
    Save the configuration files to the default path.
    """
    if backup:
        for name, backup_file in SLURM_BACKUP_FILES.items():
            if name in slurm_files.keys():
                if slurm_files[name] != backup_file:
                    shutil.copyfile(slurm_files[name], backup_file)

    # Auto-derive Gres= on each node from its assigned GRES presets,
    # merging in any presets inherited from partitions that contain the node.
    preset_map = {p['name']: p.get('properties', {})
                  for p in configuration.get('gres_presets', [])}
    # Build effective preset set per node: own presets + partition-inherited presets
    node_effective_gres = {}
    for node in configuration.get('nodes', []):
        node_effective_gres[node['name']] = set(node.get('gres_preset_names') or [])
    for part in configuration.get('partitions', []):
        for pname in (part.get('gres_preset_names') or []):
            for node_name in (part.get('node_names') or []):
                node_effective_gres.setdefault(node_name, set())
                node_effective_gres[node_name].add(pname)
    for node in configuration.get('nodes', []):
        gres_names = node_effective_gres.get(node['name'], set())
        if gres_names:
            # GRES presets assigned — derive Gres= from them, takes priority
            # over any Gres= set directly on the HW preset (Generic Resources).
            parts = []
            for pname in sorted(gres_names):  # sorted for deterministic output
                if pname in preset_map:
                    props = preset_map[pname]
                    g = props.get('Name', '')
                    if props.get('Type'):
                        g += ':' + props['Type']
                    if props.get('Count'):
                        g += ':' + str(props['Count'])
                    if g:
                        parts.append(g)
            if parts:
                node.setdefault('properties', {})['Gres'] = ','.join(parts)
        else:
            # No GRES presets assigned — fall back to any Gres= set directly
            # on the node's HW preset via the Generic Resources column.
            # This supports simple configs like Gres=gpu:8 without a full
            # gres.conf, which is valid Slurm when no File/Cores spec is needed.
            hw_preset_name = node.get('hw_preset_name')
            hw_gres = None
            if hw_preset_name:
                hw_preset = next((p for p in configuration.get('hw_presets', [])
                                  if p['name'] == hw_preset_name), None)
                if hw_preset:
                    hw_gres = hw_preset.get('properties', {}).get('Gres')
            if hw_gres:
                node.setdefault('properties', {})['Gres'] = hw_gres
            else:
                # Neither GRES presets nor HW preset Gres= — clear any stale value
                node.get('properties', {}).pop('Gres', None)

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
    # Write the gres.conf Defaults block first (preset definitions + node/partition annotations)
    # then call Generate().all_configs() which writes nodes/partitions TrinityX blocks via
    # Jinja templates — it also calls SlurmGres() but that template only reads from
    # the Defaults block, so we must re-write our gres TrinityX block afterwards.
    save_gres_configuration(configuration, slurm_files, defaults_only=True)
    #
    status = Generate().all_configs(nodes=fullset, configs=slurm_files, manager=manager)
    #
    # Re-write the gres TrinityX block after Generate() — SlurmGres() overwrites it
    # because the slurm-gres.j2 template does not know about GRESPresetName= keys.
    save_gres_configuration(configuration, slurm_files, defaults_only=False)
    #
    if status:
        return True
    else:
        return False


def parse_raw_configuration(raw_configuration):
    #sys.stdout.write(f"PARSE: {raw_configuration}\n")
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
        # normalise null/missing gres_preset_names from Tabulator to []
        if not node.get("gres_preset_names"):
            node["gres_preset_names"] = []
    for partition in raw_configuration["partitions"]:
        if not partition.get("gres_preset_names"):
            partition["gres_preset_names"] = []

    # the gui sometimes adds nodes, assigned to a partition, but not send as such.
    # here we make sure we leave no one behind.
    for partition in raw_configuration["partitions"]:
        idx = 0
        for raw_group in raw_groups:
            if partition["name"] == raw_group["name"]:
                for node_name in partition["node_names"]:
                    if node_name not in raw_group["node_names"]:
                        raw_groups[idx]["node_names"].append(node_name)
            idx += 1

    nodes = raw_configuration["nodes"] or []
    groups = raw_groups or []
    partitions = raw_configuration["partitions"] or []
    hw_presets = raw_configuration["hw_presets"] or []
    gres_presets = raw_configuration.get("gres_presets") or []

    configuration = {"nodes": nodes, "partitions": partitions, "groups": groups,
                     "hw_presets": hw_presets, "gres_presets": gres_presets}
    #sys.stdout.write(f"RAW PARSED: {configuration}\n")
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
    #sys.stdout.write(f"ADDON: {hw_presets_addons}\n")

    hw_preset_nodes = {}
    hw_preset_partitions = {}
    nodes_states = {}
    # what nodes are using the preset:
    if 'nodes' in configuration:
        for node in configuration['nodes']:
            if 'hw_preset_name' in node and node['hw_preset_name']:
                if node['hw_preset_name'] not in hw_preset_nodes:
                    hw_preset_nodes[node['hw_preset_name']] = []
                hw_preset_nodes[node['hw_preset_name']].append(node['name'])
            if 'properties' in node and 'State' in node['properties'] and node['properties']['State']:
                nodes_states[node['name']] = node['properties']['State']
    # what partitions are using the preset:
    if 'partitions' in configuration:
        for partition in configuration['partitions']:
            if 'hw_preset_name' in partition and partition['hw_preset_name']:
                if partition['hw_preset_name'] not in hw_preset_partitions:
                    hw_preset_partitions[partition['hw_preset_name']] = []
                hw_preset_partitions[partition['hw_preset_name']].append(partition['name'])
    # now let's build a per node preset list and the hw presets themselves:
    if 'hw_presets' in configuration:
        for hw_preset in configuration['hw_presets']:
            if 'properties' in hw_preset:
                hw_preset_line="HWPresetName="+hw_preset['name']+" "
                hw_preset_properties = ""
                for key, value in hw_preset['properties'].items():
                    if not (key == "State" and value == "UNKNOWN") and key != "Gres":
                        hw_preset_line+=f"{key}={value} "
                        hw_preset_properties+=f"{key}={value} "
                hw_preset_line+="# "
                if hw_preset['name'] in hw_preset_nodes:
                    hw_preset_line+="Nodes="+compress(','.join(hw_preset_nodes[hw_preset['name']]))+" "
                    for node in hw_preset_nodes[hw_preset['name']]:
                        properties_addons = ""
                        if "NodeName="+node in hw_presets_addons:
                            properties_addons = hw_presets_addons["NodeName="+node]+" "
                        if node in nodes_states:
                            properties_addons += "State="+nodes_states[node]
                            del nodes_states[node]
                        # Append Gres= so the Jinja template writes it into
                        # the TrinityX running block.
                        # Priority: GRES presets > HW preset Generic Resources fallback.
                        gres_str = ""
                        node_obj = next((n for n in configuration.get('nodes',[]) if n['name'] == node), None)
                        if node_obj and node_obj.get('gres_preset_names'):
                            preset_map = {p['name']: p.get('properties',{}) for p in configuration.get('gres_presets',[])}
                            parts = []
                            for pname in node_obj['gres_preset_names']:
                                if pname in preset_map:
                                    props = preset_map[pname]
                                    g = props.get('Name','')
                                    if props.get('Type'): g += ':' + props['Type']
                                    if props.get('Count'): g += ':' + str(props['Count'])
                                    if g: parts.append(g)
                            if parts:
                                gres_str = "Gres=" + ','.join(parts) + " "
                        else:
                            # Fallback: use Gres= from the HW preset itself (Generic Resources)
                            hw_gres = hw_preset.get('properties', {}).get('Gres')
                            if hw_gres:
                                gres_str = "Gres=" + hw_gres + " "
                        gres_preset_annotation = ""
                        if node_obj and node_obj.get('gres_preset_names'):
                            gres_preset_annotation = " GresPreset=" + ','.join(node_obj['gres_preset_names'])
                        node_preset_line="NodeName="+node+" "+hw_preset_properties+gres_str+properties_addons+" # HWPreset="+hw_preset["name"]+gres_preset_annotation
                        hw_presets["NodeName="+node]=node_preset_line
                if hw_preset['name'] in hw_preset_partitions:
                    hw_preset_line+="Partitions="+compress(','.join(hw_preset_partitions[hw_preset['name']]))
                    for partition in hw_preset_partitions[hw_preset['name']]:
                        properties_addons = ""
                        partition_preset_line="PartitionName="+partition+" "+hw_preset_properties+" # HWPreset="+hw_preset["name"]
                        hw_presets["PartitionName="+partition]=partition_preset_line
                hw_presets["HWPresetName="+hw_preset['name']]=hw_preset_line
    # a tiny entry for nodes that do not have a hw preset but set a State:
    for node in nodes_states:
        hw_presets["NodeName="+node]="NodeName="+node+" State="+nodes_states[node]

    # now we build the raw content:
    for hw_preset, entry in sorted(hw_presets.items()):
        raw_block+="# "+entry+"\n"
        if hw_preset in defaults:
            del defaults[hw_preset]
    for hw_preset, entry in sorted(defaults.items()):
        if hw_preset.startswith("HWPresetName=") and hw_preset not in hw_presets.keys():
            #sys.stdout.write(f"DELETE: {hw_preset}\n")
            continue
        elif hw_preset.startswith("NodeName="):
            _, node = hw_preset.split("=")
            if node not in configuration['nodes']:
                #sys.stdout.write(f"DELETE node: {node}\n")
                continue
        elif hw_preset.startswith("PartitionName="):
            _, partition = hw_preset.split("=")
            if partition not in configuration['partitions']:
                #sys.stdout.write(f"DELETE part: {partition}\n")
                continue
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
                    if not (key == "State" and value == "UNKNOWN"):
                        properties_line+=f"{key}={value} "
                properties["PartitionName="+partition['name']]=properties_line
    for property_preset, entry in sorted(properties.items()):
        raw_block+="# "+entry+"\n"
        if property_preset in defaults:
            del defaults[property_preset]
    for property_preset, entry in sorted(defaults.items()):
        if property_preset.startswith("PartitionName="):
            _, partition = property_preset.split("=")
            if partition not in configuration['partitions']:
                #sys.stdout.write(f"DELETE part: {partition}\n")
                continue
        raw_block+="# "+property_preset+" "+entry+"\n"

    #sys.stdout.write(f"RENDER PART RAW BLOCK:\n{raw_block}\n")
    return raw_block


def render_raw_gres_defaults(configuration):
    """
    Build the Defaults block content for gres.conf.

    Each GRES preset becomes a comment line:
      # GRESPresetName=<name> Name=<n> [Type=<t>] Count=<c> [File=<f>] [no_consume]
    Followed by comment annotations tracking which nodes/partitions use each preset:
      # GRESPresetName=<name> # Nodes=<hostlist> Partitions=<list>
    """
    raw_block = ''

    gres_preset_nodes = {}      # preset_name -> [node_name, ...]
    gres_preset_partitions = {} # preset_name -> [partition_name, ...]

    for node in configuration.get('nodes', []):
        for pname in (node.get('gres_preset_names') or []):
            gres_preset_nodes.setdefault(pname, [])
            if node['name'] not in gres_preset_nodes[pname]:
                gres_preset_nodes[pname].append(node['name'])

    for part in configuration.get('partitions', []):
        for pname in (part.get('gres_preset_names') or []):
            gres_preset_partitions.setdefault(pname, [])
            if part['name'] not in gres_preset_partitions[pname]:
                gres_preset_partitions[pname].append(part['name'])
            # propagate to all nodes in this partition for the Nodes= annotation
            for node_name in (part.get('node_names') or []):
                gres_preset_nodes.setdefault(pname, [])
                if node_name not in gres_preset_nodes[pname]:
                    gres_preset_nodes[pname].append(node_name)

    for preset in configuration.get('gres_presets', []):
        pname = preset['name']
        props = preset.get('properties', {})
        line = f"GRESPresetName={pname}"
        if props.get('Name'):
            line += f" Name={props['Name']}"
        if props.get('Type'):
            line += f" Type={props['Type']}"
        if props.get('Count'):
            line += f" Count={props['Count']}"
        if props.get('File'):
            line += f" File={props['File']}"
        if props.get('no_consume'):
            line += " no_consume"
        line += " #"
        if pname in gres_preset_nodes:
            line += " Nodes=" + compress(','.join(gres_preset_nodes[pname]))
        if pname in gres_preset_partitions:
            line += " Partitions=" + compress(','.join(gres_preset_partitions[pname]))
        raw_block += "# " + line + "\n"

    return raw_block


def save_gres_configuration(configuration, slurm_files=SLURM_FILES, defaults_only=False):
    """
    Write the gres.conf Defaults block (preset definitions + assignments)
    and optionally the TrinityX managed block (running NodeName= lines).

    defaults_only=True  — write Defaults block only (called before Generate())
    defaults_only=False — write TrinityX block only (called after Generate()
                          to overwrite the empty output from slurm-gres.j2)
    """
    gres_file = slurm_files.get('gres')
    if not gres_file:
        return

    if defaults_only:
        # --- Defaults block only ---
        raw_defaults = render_raw_gres_defaults(configuration)
        gres_config_file = ConfigFile.read(gres_file)
        if gres_config_file.ismanaged('Defaults'):
            gres_config_file.set_managed_block('Defaults', raw_defaults)
            gres_config_file.write(gres_file)
        return

    # --- TrinityX managed block: running NodeName= lines ---
    # Build a lookup: preset_name -> preset properties
    preset_map = {p['name']: p.get('properties', {})
                  for p in configuration.get('gres_presets', [])}

    # Build a lookup: partition_name -> [node_names]
    partition_nodes = {}
    for part in configuration.get('partitions', []):
        partition_nodes[part['name']] = part.get('node_names') or []

    # Collect effective gres_preset_names per node:
    # start from the node's own assignments, then add any presets inherited
    # from partitions that contain this node.
    node_effective_presets = {}   # node_name -> set of preset_names
    for node in configuration.get('nodes', []):
        node_effective_presets[node['name']] = set(node.get('gres_preset_names') or [])
    for part in configuration.get('partitions', []):
        for pname in (part.get('gres_preset_names') or []):
            for node_name in (part.get('node_names') or []):
                node_effective_presets.setdefault(node_name, set())
                node_effective_presets[node_name].add(pname)

    # Group nodes that share identical preset properties for hostlist compression
    # key: (preset_name, Name, Type, Count, File, no_consume) -> [node_names]
    line_groups = {}
    for node_name, presets in node_effective_presets.items():
        for pname in presets:
            if pname not in preset_map:
                continue
            props = preset_map[pname]
            key = (pname,
                   props.get('Name', ''),
                   props.get('Type', ''),
                   props.get('Count', ''),
                   props.get('File', ''),
                   bool(props.get('no_consume', False)))
            line_groups.setdefault(key, [])
            if node_name not in line_groups[key]:
                line_groups[key].append(node_name)

    running_block = ''
    for (pname, name, gtype, count, gfile, no_cons), node_names in sorted(line_groups.items()):
        nodelist = compress(','.join(node_names))
        line = f"NodeName={nodelist}"
        if name:
            line += f" Name={name}"
        if gtype:
            line += f" Type={gtype}"
        if count:
            line += f" Count={count}"
        if gfile:
            line += f" File={gfile}"
        if no_cons:
            line += " no_consume"
        running_block += line + "\n"

    # Re-read after defaults write so we update the right block
    gres_config_file = ConfigFile.read(gres_file)
    if gres_config_file.ismanaged(MANAGER_NAME):
        gres_config_file.set_managed_block(MANAGER_NAME, running_block)
        gres_config_file.write(gres_file)


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
    who = request.args.get("manager")
    OOD = False
    if who == "OOD":
        OOD = True
    set_manager(OOD=OOD,slurm_files=SLURM_FILES)
    return redirect(url_for("index_route"))


@app.route("/get_manager")
def get_manager_route():
    """Get the manager of the managed block."""
    file = SLURM_FILES['nodes']
    if check_managed_block(file, MANAGER_NAME):
        return jsonify({"config": {"manager": MANAGER_NAME}})
    elif check_managed_block(file, MANAGER_NAME_OOD):
        return jsonify({"config": {"manager": MANAGER_NAME_OOD}})
    return jsonify({"config": {"manager": "manual"}})


@app.route("/whois_manager")
def whois_manager_route():
    """
    Who is the manager of the managed block.
    Similar to /get_manager, however this one hides/translates
    to a generic/slurm app known/coded name/value
    """
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


@app.route("/json/configuration/gres_presets", methods=["GET"])
def get_gres_presets_route():
    load_from_backup = request.args.get("load_from_backup")
    slurm_files = SLURM_FILES
    if load_from_backup:
        slurm_files = SLURM_BACKUP_FILES
    configuration = load_configuration(slurm_files=slurm_files)
    return jsonify(configuration["gres_presets"])


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
        config_block = ConfigFile.read(SLURM_BACKUP_FILES['gres'])
        gres_preview_lines = config_block.dump()
    else:
        configuration = parse_raw_configuration(request.json)
        nodes_preview_lines, partitions_preview_lines, gres_preview_lines = save_tmp_files(configuration)
    return render_template(
        "components/configuration_preview.html",
        partitions_preview_lines=partitions_preview_lines,
        nodes_preview_lines=nodes_preview_lines,
        gres_preview_lines=gres_preview_lines,
    )


@app.route("/json/configuration/test", methods=["POST"])
def test_configuration_route():
    configuration = parse_raw_configuration(request.json)
    node_lines, partition_lines, _gres_lines = save_tmp_files(configuration)

    configuration_lines = node_lines + partition_lines
    configuration_lines = configuration_lines.split("\n")
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
    app.run()
