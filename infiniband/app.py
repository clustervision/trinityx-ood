import re
import subprocess

from flask import Flask, jsonify, render_template

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
    return jsonify({"message": str(error)}), 500


def parse_graph(text):
    """
    This method will parse the ibnetdiscover output into a graph.
    """

    switch_regex = r"(Switch|Ca)\s+([0-9]+)\s+\"([SH]-[0-9a-z]+)\"\s+#\s*\"(.*)\".*\n?(\[[0-9]+\].*\n)*"
    link_regex = r"\[([0-9]+)\].*\"([SH]-[0-9a-z]+)\".*\[([0-9]+)\].*#\s*\"(.*)\""
    matches = re.finditer(switch_regex, text, re.MULTILINE)

    nodes = {}
    edges = {}

    for switch_match in matches:
        ports = switch_match.group(2)
        uid = switch_match.group(3)
        name = switch_match.group(4)
        nodes[uid] = {"name": name, "ports": ports, "type": uid[0]}

        for link_match in re.finditer(link_regex, switch_match.group(0)):
            _ = link_match.group(1)
            target_uid = link_match.group(2)
            _ = link_match.group(3)
            _ = link_match.group(4)

            edge_uid = tuple(sorted([uid, target_uid]))
            edge_count = edges.get(edge_uid, 0)
            edges[edge_uid] = edge_count + 1

    nodes = [{"id": uid, **data} for uid, data in nodes.items()]
    links = [
        {"source": source, "target": target, "count": count // 2}
        for (source, target), count in edges.items()
    ]

    graph = {"nodes": nodes, "links": links}
    return jsonify(graph)


@app.route("/")
def index_route():
    """
    Route to get the index page.
    """

    return render_template("index.html", content="", settings=settings)


@app.route("/graph")
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
    else:
        text = process.stdout.decode("utf-8")
        return parse_graph(text)
