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

__author__      = 'Diego Sonaglia'
__copyright__   = 'Copyright 2022, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'ClusterVision Solutions Development Team'
__email__       = 'support@clustervision.com'
__status__      = 'Development'

import os
import sys
import tempfile

from flask import Flask, render_template, request, jsonify, redirect, url_for

from trinityx_config_manager.parsers.ood_slurm_partitions import OODSlurmPartitionsConfigParser
from trinityx_config_manager.parsers.ood_slurm_nodes      import OODSlurmNodesConfigParser

from config import settings
from helpers import nodes_to_groups, get_luna_nodes, wrap_errors

app = Flask(__name__,
            template_folder="templates",
            static_folder="static",
            static_url_path='/')
app.config["TEMPLATES_AUTO_RELOAD"] = True


# add a wrapper to all the routes to catch errors
@app.errorhandler(Exception)
def wrap_errors(error):
    """Decorator to wrap errors in a JSON response."""
    return jsonify({"message": str(error)}), 500

@app.context_processor
def inject_dict_for_all_templates():
    return {'settings': {'app_name': 'Slurm', **settings}}


def _get_is_managed_by_ood():
    """Check if the configuration files are managed by OOD."""
    partitions_parser = OODSlurmPartitionsConfigParser().read()
    nodes_parser = OODSlurmNodesConfigParser().read()
    print(f"checking if partitions is managed by OOD: {partitions_parser.get_manager()}", file=sys.stderr)
    print(f"checking if nodes is managed by OOD: {nodes_parser.get_manager()}", file=sys.stderr)
    return partitions_parser.is_manager() and nodes_parser.is_manager()

def load_configuration():
    """Load the configuration files from the default path."""
    partitions_parser = OODSlurmPartitionsConfigParser()
    nodes_parser = OODSlurmNodesConfigParser()
    partitions_parser = partitions_parser.read()
    nodes_parser = nodes_parser.read()
    partitions = partitions_parser.get_content()
    nodes = nodes_parser.get_content()
    configuration = {"partitions": partitions, "nodes": nodes}
    return configuration

@app.route('/')
def index():
    """Render the index page."""
    if not _get_is_managed_by_ood():
        return render_template('pages/unmanaged.html')
    return render_template('pages/index.html')

@app.route('/set_manager')
def set_manager():
    """Set the manager of the managed block."""
    partitions_parser = OODSlurmPartitionsConfigParser().read()
    nodes_parser = OODSlurmNodesConfigParser().read()
    partitions_parser.set_manager(OODSlurmPartitionsConfigParser.MANAGER_NAME)
    nodes_parser.set_manager(OODSlurmNodesConfigParser.MANAGER_NAME)
    partitions_parser.write(force=True)
    nodes_parser.write(force=True)
    return redirect(url_for('index'))


@app.route('/import/luna/nodes', methods=['GET'])
def import_luna_nodes():
    """Load the luna nodes from the luna daemon."""
    try:
        nodes = get_luna_nodes()
        return jsonify(nodes), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/save', methods=['POST'])
def save_configuration():
    """Render the configuration preview."""
    configuration = request.json

    partitions_parser = OODSlurmPartitionsConfigParser().read()
    partitions_parser.set_content(configuration['partitions'])
    partitions_parser.write(backup=True)

    nodes_parser = OODSlurmNodesConfigParser().read()
    nodes_parser.set_content(configuration['nodes'])
    nodes_parser.write(backup=True)

    return redirect('/')

@app.route('/test', methods=['POST'])
def test_configuration():
    """Render the configuration preview."""
    # tmpdir = tempfile.mkdtemp()
    import time
    import shutil
    import subprocess
    tmpdir = '/tmp/ood-slurm-tests'
    shutil.rmtree(tmpdir, ignore_errors=True)
    
    os.makedirs( f"{tmpdir}/etc/", exist_ok=True)
    os.makedirs( f"{tmpdir}/var/log/slurm", exist_ok=True)
    
    shutil.copytree('/etc/slurm', f"{tmpdir}/etc/slurm")

    with open(f"{tmpdir}/etc/slurm/slurm.conf", 'r') as fin:
        lines = fin.readlines()
    
    lines = [line.replace('/etc/slurm', f"{tmpdir}/etc/slurm") for line in lines]
    lines = [line.replace('/var/log/slurm', f"{tmpdir}/var/log/slurm") for line in lines]

    with open(f"{tmpdir}/etc/slurm/slurm.conf", 'w') as fout:
        fout.writelines(lines)

        
    configuration = request.json

    partitions_parser = OODSlurmPartitionsConfigParser(output_filepath=f"{tmpdir}/etc/slurm/slurm-partitions.conf").read()
    partitions_parser.set_content(configuration['partitions'])
    partitions_parser.write()

    nodes_parser = OODSlurmNodesConfigParser(output_filepath=f"{tmpdir}/etc/slurm/slurm-nodes.conf").read()
    nodes_parser.set_content(configuration['nodes'])
    nodes_parser.write()


    slurmctld_proc = subprocess.Popen(["/usr/sbin/slurmctld", "-D", "-f", f"{tmpdir}/etc/slurm/slurm.conf", "-s", tmpdir], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    os.set_blocking(slurmctld_proc.stdout.fileno(), False)
    os.set_blocking(slurmctld_proc.stderr.fileno(), False)
    errors = []
    startup_completed = False
    while not startup_completed:
        for pipe in [slurmctld_proc.stderr, slurmctld_proc.stdout]:
            while (line_bytes := pipe.readline()):
                line = line_bytes.decode('utf-8').strip()
                print(line, file=sys.stderr)
                if line.startswith('slurmctld: Running'):
                    startup_completed = True
                if line.startswith('slurmctld: error'):
                    errors.append(line)

        time.sleep(0.5)
        if slurmctld_proc.poll() is not None:
            break
    

    if startup_completed:
        if not errors:
            return jsonify({"message": "success"}), 200
        else:
            return jsonify({"message": "warning", "errors": errors}), 200
    else:
        return jsonify({"message": "error", "errors": errors}), 500

@app.route('/restore', methods=['POST'])
def restore_configuration():

    OODSlurmPartitionsConfigParser().restore_backup()
    OODSlurmNodesConfigParser().restore_backup()

    return redirect('/')



@app.route('/components/node', methods=['POST'])
def node():
    """Render a node item."""
    node_name = request.args['node_name']
    group_name = request.args['group_name']
    print(f"rendering node item with node: {request.args}", file=sys.stderr)
    return render_template('components/node.html', node_name=node_name, group_name=group_name)

@app.route('/components/nodes_group', methods=['POST'])
def nodes_group():
    """Render a nodes group."""
    group_name = request.args['group_name']
    print(f"rendering nodes group with group: {group_name}", file=sys.stderr)
    return render_template('components/nodes_group.html', group_name=group_name, node_names=[])

@app.route('/components/nodes_card', methods=['POST'])
def nodes_card():
    """Render the nodes card."""
    configuration = request.get_json(silent=True) or load_configuration()
    partitions = configuration['partitions']
    nodes = configuration['nodes']
    groups = list(set([configuration['nodes'][node]['group'] for node in configuration['nodes']]))

    print(f"rendering nodes card with groups: {groups}", file=sys.stderr)
    assigned_nodes = []
    for partition in partitions:
        if 'nodes' in partitions[partition]:
            assigned_nodes += partitions[partition]['nodes']
    _unassigned_nodes = [node for node in nodes if node not in assigned_nodes]
    unassigned_nodes = {node: nodes[node] for node in _unassigned_nodes}
    grouped_unassinged_nodes = {}
    for node in unassigned_nodes:
        group = unassigned_nodes[node]['group']
        if group not in grouped_unassinged_nodes:
            grouped_unassinged_nodes[group] = []
        grouped_unassinged_nodes[group].append(node)
    print(f"rendering nodes card with nodes: {nodes}", file=sys.stderr)
    return render_template('components/nodes_card.html', groups=groups, grouped_unassinged_nodes=grouped_unassinged_nodes)

@app.route('/components/partition_card', methods=['POST'])
def partition_card():
    """Render a partition card."""
    partition = request.get_json(silent=True) or {"nodes": {}, "properties": {}}

    print(f"rendering partition card with partition: {partition}", file=sys.stderr)
    partition_name = request.args['partition_name']
    return render_template('components/partition_card.html', partition_name=partition_name, partition=partition)

@app.route('/components/partitions_cards', methods=['POST'])
def partitions_cards():
    """Render the partitions cards."""
    configuration = request.get_json(silent=True) or load_configuration()
    partitions = configuration['partitions']

    nodes_parser = OODSlurmNodesConfigParser().read()
    _aux_nodes = nodes_parser.get_content()
    print(f"rendering partitions cards with partitions: {partitions}", file=sys.stderr)
    print(f"rendering partitions cards with nodes: {_aux_nodes}", file=sys.stderr)

    for partition in partitions:
        if 'nodes' in partitions[partition]:
            partitions[partition]['nodes'] = {node: _aux_nodes[node] for node in partitions[partition]['nodes']}


    print(f"rendering partitions cards with partitions: {partitions}", file=sys.stderr)
    return render_template('components/partitions_cards.html', partitions=partitions)

@app.route('/components/configuration_preview', methods=['POST'])
def configuration_preview():
    """Render the configuration preview."""
    configuration = request.json

    partitions_parser = OODSlurmPartitionsConfigParser().read()
    partitions_parser.set_content(configuration['partitions'])
    partitions_preview_lines = partitions_parser.dump_lines(marked=True)

    nodes_parser = OODSlurmNodesConfigParser().read()
    nodes_parser.set_content(configuration['nodes'])
    nodes_preview_lines = nodes_parser.dump_lines(marked=True)

    return render_template('components/configuration_preview.html', partitions_preview_lines=partitions_preview_lines, nodes_preview_lines=nodes_preview_lines)

@app.route('/components/backup_configuration_preview', methods=['POST'])
def backup_configuration_preview():
    """Render the configuration preview."""
    configuration = request.json

    partitions_parser = OODSlurmPartitionsConfigParser()
    partitions_parser = partitions_parser.read(partitions_parser.backup_filepath)
    partitions_preview_lines = partitions_parser.dump_lines(marked=True)

    nodes_parser = OODSlurmNodesConfigParser().read()
    nodes_parser = nodes_parser.read(nodes_parser.backup_filepath)
    nodes_preview_lines = nodes_parser.dump_lines(marked=True)

    return render_template('components/configuration_preview.html', partitions_preview_lines=partitions_preview_lines, nodes_preview_lines=nodes_preview_lines)

@app.route('/download/partitions', methods=['POST'])
def download_partitions():
    """Download the partitions configuration file."""
    configuration = request.json
    partitions_parser = OODSlurmPartitionsConfigParser().read()
    partitions_parser.set_content(configuration['partitions'])
    partition_str = partitions_parser.dump()
    # make a file from partition_str to return
    import io
    import mimetypes
    from flask import Response
    from werkzeug.datastructures import Headers

    filename = 'slurm-partitions.conf'
    mimetype_tuple = mimetypes.guess_type(filename)
    response = Response()
    response.headers = Headers({
        'Pragma': "public",  # required,
        'Expires': '0',
        'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
        'Content-Type': mimetype_tuple[0],
        'Content-Disposition': f'attachment;filename={filename}',
        'Content-Transfer-Encoding': 'binary',
        'Content-Length': len(partition_str)
    })
    response.set_data(partition_str)
    return response

@app.route('/download/nodes', methods=['POST'])
def download_nodes():
    """Download the nodes configuration file."""
    configuration = request.json
    nodes_parser = OODSlurmNodesConfigParser().read()
    nodes_parser.set_content(configuration['nodes'])
    partition_str = nodes_parser.dump()
    # make a file from partition_str to return
    import io
    import mimetypes
    from flask import Response
    from werkzeug.datastructures import Headers

    filename = 'slurm-nodes.conf'
    mimetype_tuple = mimetypes.guess_type(filename)
    response = Response()
    response.headers = Headers({
        'Pragma': "public",  # required,
        'Expires': '0',
        'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
        'Content-Type': mimetype_tuple[0],
        'Content-Disposition': f'attachment;filename={filename}',
        'Content-Transfer-Encoding': 'binary',
        'Content-Length': len(partition_str)
    })
    response.set_data(partition_str)
    return response


if __name__ == "__main__":
    app.run()
