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

from config import settings
from helpers import (
    get_luna_nodes,
    wrap_errors,
)

app = Flask(
    __name__, template_folder="templates", static_folder="static", static_url_path="/"
)
app.config["TEMPLATES_AUTO_RELOAD"] = True


# add a wrapper to all the routes to catch errors
# @app.errorhandler(Exception)
# def wrap_errors(error):
#     """Decorator to wrap errors in a JSON response."""
#     if app.debug:
#         raise error
#     return jsonify({"message": str(error)}), 500


@app.context_processor
def inject_settings():
    return {"settings": {"app_name": "Slurm", **settings}}

def get_is_managed_by_ood():
    """Check if the configuration files are managed by OOD."""
    partitions_parser = OODSlurmPartitionsConfigParser().read()
    nodes_parser = OODSlurmNodesConfigParser().read()
    print(
        f"checking if partitions is managed by OOD: {partitions_parser.get_manager()}",
        file=sys.stderr,
    )
    print(
        f"checking if nodes is managed by OOD: {nodes_parser.get_manager()}",
        file=sys.stderr,
    )
    return partitions_parser.is_manager() and nodes_parser.is_manager()


def load_configuration(load_from_backup=False):
    """Load the configuration files from the default path."""

    # If the configuration is not provided, load it from the default path
    partitions_parser = OODSlurmPartitionsConfigParser()
    nodes_parser = OODSlurmNodesConfigParser()

    # Load the configuration files
    if load_from_backup:
        partitions_parser = partitions_parser.read(partitions_parser.backup_filepath)
        nodes_parser = nodes_parser.read(nodes_parser.backup_filepath)
    else:
        partitions_parser = partitions_parser.read()
        nodes_parser = nodes_parser.read()

    partitions_config = partitions_parser.get_content()
    nodes_config = nodes_parser.get_content()

    configuration = nodes_config
    configuration.partitions = partitions_config.partitions

    print("loaded configuration:", file=sys.stderr)
    print(f"{configuration}", file=sys.stderr)

    return configuration

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

    partitions_parser.write()
    nodes_parser.write()

    return True

def parse_raw_configuration(raw_configuration):
    raw_groups = []
    group_nodes = [node for node in raw_configuration["nodes"] if node["group_name"]]
    sorted_nodes = sorted(group_nodes, key=lambda node: node["group_name"])
    for group_name, nodes in itertools.groupby(sorted_nodes, key=lambda node: node["group_name"]):
        node_names = [node["name"] for node in nodes]
        raw_groups.append({"name": group_name, "node_names": node_names})
    for node in raw_configuration["nodes"]:
        node.pop("group_name", None)

    nodes = [ Node(**node) for node in raw_configuration["nodes"] ]
    groups = [ Group(**group) for group in raw_groups ]
    partitions = [ Partition(**partition) for partition in raw_configuration["partitions"] ]
    hw_presets = [ HWPreset(**hw_preset) for hw_preset in raw_configuration["hw_presets"] ]

    config = NodesConfig(nodes=nodes, groups=groups, partitions=partitions, hw_presets=hw_presets)
    return config

# Pages
@app.route("/")
def index_route():
    """Render the index page."""
    message = request.args.get("message")
    configuration = load_configuration(
        load_from_backup="load_from_backup" in request.args
    )

    if not get_is_managed_by_ood():
        return render_template("pages/unmanaged.html")
    return render_template(
        "pages/index.html",
        configuration=configuration,
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
    configuration = load_configuration().to_dict()
    return jsonify(configuration["hw_presets"])

@app.route("/json/configuration/nodes", methods=["GET"])
def get_nodes_route():
    configuration = load_configuration().to_dict()
    nodes = configuration["nodes"]

    for node in nodes:
        print( configuration["groups"] )
        group_name = next((group['name'] for group in configuration["groups"] if node['name'] in group["node_names"]), None)
        node['group_name'] = group_name
    
    return jsonify(nodes)

@app.route("/json/configuration/partitions", methods=["GET"])
def get_partitions_route():
    configuration = load_configuration().to_dict()
    partitions = configuration["partitions"]
    return jsonify(partitions)


@app.route("/json/configuration", methods=["POST"])
def set_configuration_route():
    """Set the configuration."""
    raw_configuration = request.json
    configuration = parse_raw_configuration(raw_configuration)
    save_configuration(configuration)
    output = {"redirect":  url_for("index_route", message="Configuration saved successfully, restart the slurmctld service to apply the changes.") }
    return jsonify(output)

@app.route("/json/configuration/preview", methods=["POST"])
def configuration_preview_route():
    """Render the configuration preview."""
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

# @app.route("/import/luna/nodes", methods=["GET"])
# def import_luna_nodes_route():
#     """Load the luna nodes from the luna daemon."""
#     try:
#         nodes = get_luna_nodes()
#         return jsonify(nodes), 200
#     except Exception as e:
#         return jsonify({"message": str(e)}), 500


# @app.route("/save", methods=["POST"])
# def save_configuration_route():
#     """Render the configuration preview."""
#     configuration = load_configuration(raw_configuration=request.json)

#     partitions_parser = OODSlurmPartitionsConfigParser().read()
#     partitions_parser.set_content(configuration["partitions"])
#     partitions_parser.write(backup=True)

#     nodes_parser = OODSlurmNodesConfigParser().read()
#     nodes_parser.set_content(configuration["nodes"])
#     nodes_parser.write(backup=True)
#     message = "Configuration saved successfully, restart the slurmctld service to apply the changes."
#     return url_for("index_route", message=message)


# @app.route("/test", methods=["POST"])
# def test_configuration_route():
#     """Render the configuration preview."""
#     tmpdir = tempfile.mkdtemp()
#     import time
#     import shutil
#     import subprocess

#     # tmpdir = '/tmp/ood-slurm-tests'
#     # shutil.rmtree(tmpdir, ignore_errors=True)

#     os.makedirs(f"{tmpdir}/etc/slurm", exist_ok=True)
#     os.makedirs(f"{tmpdir}/run/slurm", exist_ok=True)

#     for root, dirs, files in os.walk("/etc/slurm"):
#         for file in files:
#             try:
#                 shutil.copy(os.path.join(root, file), f"{tmpdir}/etc/slurm")
#             except Exception as e:
#                 print(f"error copying file {file}: {e}", file=sys.stderr)

#     with open(f"{tmpdir}/etc/slurm/slurm.conf", "r") as fin:
#         lines = fin.readlines()

#     lines = [line.replace("/etc/slurm", f"{tmpdir}/etc/slurm") for line in lines]
#     lines = [
#         line.replace("/var/log/slurm", f"{tmpdir}/var/log/slurm") for line in lines
#     ]
#     lines = [f"#{line}" if line.startswith("Accounting") else line for line in lines]
#     lines = [f"#{line}" if line.startswith("SlurmdLogFile") else line for line in lines]
#     lines = [
#         f"#{line}" if line.startswith("SlurmctldLogFile") else line for line in lines
#     ]
#     lines = [
#         f"#{line}" if line.startswith("SlurmctldPidFile") else line for line in lines
#     ]
#     lines.append(f"SlurmctldPidFile={tmpdir}/run/slurm/slurmctld.pid")

#     with open(f"{tmpdir}/etc/slurm/slurm.conf", "w") as fout:
#         fout.writelines(lines)

#     configuration = load_configuration(raw_configuration=request.json)

#     partitions_parser = OODSlurmPartitionsConfigParser(
#         output_filepath=f"{tmpdir}/etc/slurm/slurm-partitions.conf"
#     ).read()
#     partitions_parser.set_content(configuration["partitions"])
#     partitions_parser.write()

#     nodes_parser = OODSlurmNodesConfigParser(
#         output_filepath=f"{tmpdir}/etc/slurm/slurm-nodes.conf"
#     ).read()
#     nodes_parser.set_content(configuration["nodes"])
#     nodes_parser.write()

#     workdir_args = ["-s", f"{tmpdir}/var/slurm"]
#     conf_args = ["-f", f"{tmpdir}/etc/slurm/slurm.conf"]

#     slurmctld_proc = subprocess.Popen(
#         ["/usr/sbin/slurmctld", "-D", "-s", tmpdir, *conf_args],
#         stderr=subprocess.PIPE,
#         stdout=subprocess.PIPE,
#     )
#     os.set_blocking(slurmctld_proc.stdout.fileno(), False)
#     os.set_blocking(slurmctld_proc.stderr.fileno(), False)
#     errors = []
#     startup_completed = False
#     while not startup_completed:
#         for pipe in [slurmctld_proc.stderr, slurmctld_proc.stdout]:
#             while line_bytes := pipe.readline():
#                 line = line_bytes.decode("utf-8").strip()
#                 print(line, file=sys.stderr)
#                 if line.startswith("slurmctld: Running"):
#                     startup_completed = True
#                 if line.startswith("slurmctld: error"):
#                     errors.append(line)

#         time.sleep(0.5)
#         if slurmctld_proc.poll() is not None:
#             break

#     for pipe in [slurmctld_proc.stderr, slurmctld_proc.stdout]:
#         while line_bytes := pipe.readline():
#             line = line_bytes.decode("utf-8").strip()
#             print(line, file=sys.stderr)
#             if line.startswith("slurmctld: Running"):
#                 startup_completed = True
#             if line.startswith("slurmctld: error"):
#                 errors.append(line)

#     if startup_completed:
#         if not errors:
#             return jsonify({"status": "success"}), 200
#         else:
#             return jsonify({"status": "warning", "errors": errors}), 200
#     else:
#         return jsonify({"status": "error", "errors": errors}), 200


# @app.route("/test", methods=["POST"])
# def test_configuration_route():
#     configuration = load_configuration(raw_configuration=request.json)
#     print(configuration, file=sys.stderr)
#     node_lines = OODSlurmNodesConfigParser.dump_managed_block(configuration["nodes"])
#     partition_lines = OODSlurmPartitionsConfigParser.dump_managed_block(
#         configuration["partitions"]
#     )

#     configuration_lines = partition_lines + node_lines

#     from slurmlint.linter import lint

#     res = lint("\n".join(configuration_lines))
#     print(f"running lint with configuration: {configuration_lines}", file=sys.stderr)
#     print(f"res: {res}", file=sys.stderr)
#     errors = res.get("errors", [])

#     expanded_errors = [
#         f"{configuration_lines[line]}: {error}" for line, error in errors
#     ]
#     if not errors:
#         return jsonify({"status": "success"}), 200
#     else:
#         return jsonify({"status": "error", "errors": expanded_errors}), 200


# @app.route("/load", methods=["POST"])
# def load_configuration_route():
#     """load the configuration files from the backup path."""
#     return url_for(
#         "index_route",
#         load_from_backup=True,
#         message="Backup configuration loaded successfully, save the configuration to apply the changes.",
#     )


# @app.route("/download/partitions", methods=["POST"])
# def download_partitions_route():
#     """Download the partitions configuration file."""
#     configuration = load_configuration(raw_configuration=request.json)
#     partitions_parser = OODSlurmPartitionsConfigParser().read()
#     partitions_parser.set_content(configuration["partitions"])
#     partition_str = partitions_parser.dump()
#     # make a file from partition_str to return
#     import io
#     import mimetypes
#     from flask import Response
#     from werkzeug.datastructures import Headers

#     filename = "slurm-partitions.conf"
#     mimetype_tuple = mimetypes.guess_type(filename)
#     response = Response()
#     response.headers = Headers(
#         {
#             "Pragma": "public",  # required,
#             "Expires": "0",
#             "Cache-Control": "must-revalidate, post-check=0, pre-check=0",
#             "Content-Type": mimetype_tuple[0],
#             "Content-Disposition": f"attachment;filename={filename}",
#             "Content-Transfer-Encoding": "binary",
#             "Content-Length": len(partition_str),
#         }
#     )
#     response.set_data(partition_str)
#     return response


# @app.route("/download/nodes", methods=["POST"])
# def download_nodes_route():
#     """Download the nodes configuration file."""
#     configuration = load_configuration(raw_configuration=request.json)
#     nodes_parser = OODSlurmNodesConfigParser().read()
#     nodes_parser.set_content(configuration["nodes"])
#     partition_str = nodes_parser.dump()
#     # make a file from partition_str to return
#     import io
#     import mimetypes
#     from flask import Response
#     from werkzeug.datastructures import Headers

#     filename = "slurm-nodes.conf"
#     mimetype_tuple = mimetypes.guess_type(filename)
#     response = Response()
#     response.headers = Headers(
#         {
#             "Pragma": "public",  # required,
#             "Expires": "0",
#             "Cache-Control": "must-revalidate, post-check=0, pre-check=0",
#             "Content-Type": mimetype_tuple[0],
#             "Content-Disposition": f"attachment;filename={filename}",
#             "Content-Transfer-Encoding": "binary",
#             "Content-Length": len(partition_str),
#         }
#     )
#     response.set_data(partition_str)
#     return response


# # Components
# @app.route("/components/node", methods=["POST"])
# def node_route():
#     """Render a node item."""
#     node_name = request.args["node_name"]
#     group_name = request.args["group_name"]
#     print(f"rendering node item with node: {request.args}", file=sys.stderr)
#     return render_template(
#         "components/node.html", node_name=node_name, group_name=group_name
#     )


# @app.route("/components/nodes_group", methods=["POST"])
# def nodes_group_route():
#     """Render a nodes group."""
#     group_name = request.args["group_name"]
#     print(f"rendering nodes group with group: {group_name}", file=sys.stderr)
#     return render_template(
#         "components/nodes_group.html", group_name=group_name, node_names=[]
#     )


# @app.route("/components/partition_card", methods=["POST"])
# def partition_card_route():
#     """Render a partition card."""
#     partition = Partition(name=request.args['partition_name'], nodenames=[], properties={})

#     print(f"rendering partition card with partition: {partition}", file=sys.stderr)

#     return render_template(
#         "components/partition_card.html",
#         partition=partition,
#     )





# @app.route("/components/backup_configuration_preview", methods=["POST"])
# def backup_configuration_preview_route():
#     """Render the configuration preview."""
#     configuration = load_configuration(raw_configuration=request.json)

#     partitions_parser = OODSlurmPartitionsConfigParser()
#     partitions_parser = partitions_parser.read(partitions_parser.backup_filepath)
#     partitions_preview_lines = partitions_parser.dump_lines(marked=True)

#     nodes_parser = OODSlurmNodesConfigParser().read()
#     nodes_parser = nodes_parser.read(nodes_parser.backup_filepath)
#     nodes_preview_lines = nodes_parser.dump_lines(marked=True)

#     return render_template(
#         "components/configuration_preview.html",
#         partitions_preview_lines=partitions_preview_lines,
#         nodes_preview_lines=nodes_preview_lines,
#     )


if __name__ == "__main__":
    app.run()
