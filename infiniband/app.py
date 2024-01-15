import re
import os
import subprocess
from json import loads, dumps, JSONDecodeError

from flask import Flask, render_template, request

from base.config import settings

app = Flask(
    __name__, template_folder="templates", static_folder="static", static_url_path="/"
)


@app.errorhandler(Exception)
def wrap_errors(error):
    """
    Decorator to wrap errors in a JSON response.
    """
    if app.debug:
        raise error
    return dumps({"message": str(error)}), 500


def _compress_portrange(port_ids):
    port_ids = sorted(list(set(port_ids)))
    port_ranges = []
    start = None
    end = None
    for port_id in port_ids:
        if start is None:
            start = port_id
            end = port_id
        elif port_id == end + 1:
            end = port_id
        else:
            port_ranges.append(f"{start}-{end}")
            start = port_id
            end = port_id
    if start is not None:
        port_ranges.append(f"{start}-{end}")
    return ",".join(port_ranges)


def _compress_extlinks(extlinks):
    links_dict = {}

    sorted_extlinks = sorted(
        extlinks,
        key=lambda x: f"{x['uid']} {x['target_uid']} {x['port_id']} {x['target_port_id']}",
    )
    for extlink in sorted_extlinks:
        _source, _target = extlink["uid"], extlink["target_uid"]
        source, target = sorted([_source, _target])

        count, source_port_ids, target_port_ids, type = links_dict.get(
            (source, target), (0, [], [], None)
        )

        count += 1
        if source.startswith("S") and target.startswith("S"):
            type = type or "SS"
            if _source == source:
                source_port_ids.append(extlink["port_id"])
                target_port_ids.append(extlink["target_port_id"])
            else:
                source_port_ids.append(extlink["target_port_id"])
                target_port_ids.append(extlink["port_id"])
        else:
            type = type or "SH"

        links_dict[(source, target)] = (count, source_port_ids, target_port_ids, type)

    links = [
        {
            "source": source,
            "target": target,
            "count": count // 2,
            "source_name": _compress_portrange(source_port_ids),
            "target_name": _compress_portrange(target_port_ids),
            "type": type,
        }
        for (source, target), (
            count,
            source_port_ids,
            target_port_ids,
            type,
        ) in links_dict.items()
    ]
    return links


def parse_graph(text):
    """
    This method will parse the ibnetdiscover output into a graph.
    """

    node_regex = r"(Switch|Ca)\s+([0-9]+)\s+\"([SH]-[0-9a-z]+)\".*#.*\"(.*)\".*\n?(\[[0-9]+\].*\n)*"
    link_regex = r"\[([0-9]+)\].*\"([SH]-[0-9a-z]+)\".*\[([0-9]+)\].*#.*\"(.*)\""

    nodes = []
    links = []
    extlinks = []

    for switch_match in re.finditer(node_regex, text, re.MULTILINE):
        uid = switch_match.group(3)
        name = switch_match.group(4)
        ports = switch_match.group(2)

        node = {
            "uid": uid,
            "name": name,
            "ports": ports,
            "type": uid[0],
            "_children": [],
        }

        nodes.append(node)

        for link_match in re.finditer(link_regex, switch_match.group(0)):
            port_id = link_match.group(1)
            target_uid = link_match.group(2)
            target_name = link_match.group(4)
            target_port_id = link_match.group(3)

            link = {
                "name": name,
                "uid": uid,
                "port_id": int(port_id),
                "target_name": target_name,
                "target_uid": target_uid,
                "target_port_id": int(target_port_id),
            }

            extlinks.append(link)

    nodes = [{"id": n["uid"], **n} for n in nodes]
    links = _compress_extlinks(extlinks)
    graph = {"nodes": nodes, "links": links, "extlinks": extlinks}
    return graph


@app.route("/")
def index_route():
    """
    Route to get the index page.
    """

    return render_template("index.html", content="", settings=settings)


@app.route("/graph/get")
def graph_route():
    """
    Route to get the graph.
    """

    process = subprocess.run(
        ["ibnetdiscover"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    if process.returncode != 0:
        raise Exception(
            f"ibnetdiscover failed with code {process.returncode}:\n{process.stderr.decode('utf-8')}"
        )

    ibnetdiscover_output = process.stdout.decode("utf-8")
    graph = parse_graph(ibnetdiscover_output)
    state_path = os.path.join(os.path.dirname(__file__), "state.json")

    try:
        if os.path.exists(state_path):
            with open(state_path, "r") as f:
                graph["state"] = loads(f.read())
    except JSONDecodeError:
        pass
    finally:
        return dumps(graph)


@app.route("/graph/state/save", methods=["POST"])
def save_route():
    """
    Route to save the graph.
    """

    state = request.json
    state_path = os.path.join(os.path.dirname(__file__), "state.json")
    with open(state_path, "w") as f:
        f.write(dumps(state))
    response = {"message": f"Saved state to {state_path}"}
    return dumps(response)
