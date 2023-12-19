import subprocess
from flask import Flask, jsonify
from flask import render_template
import networkx as nx
import re

from base.config import settings
import networkx as nx

app = Flask(
    __name__, template_folder="templates", static_folder="static", static_url_path="/"
)

def plot_graph(text):
    """
    This method will plot a graph.
    """

    switches = []
    nodes = []
    links = {}

    last_uid = None
    last_type = None
    for line in text.splitlines():
        if line.startswith("Ca"):
            # Ca	1 "H-506b4b03003fa98a"		# "node019 HCA-1"
            match = re.search(r"Ca\s+([0-9]+) +\"(H|S)-([0-9a-fA-F]+)\"\s+#\s*\"(.*)\"(.*)", line)
            ports = match.group(1)
            uid = match.group(3)
            name = match.group(4)
            location = match.group(5)
            desc = f"UID: {uid} \nPORTS: {ports} \nNAME: {name} \nLOCATION: {location}"
            nodes.append({"id": uid, "desc": desc})
            last_uid = uid
            last_type = match.group(2)
            
        elif line.startswith("Switch"):
            # Switch	36 "S-ec0d9a0300ec8240"		# "SwitchIB Mellanox Technologies" base port 0 lid 48 lmc 0
            match = re.search(r"Switch\s+([0-9]+) +\"(H|S)-([0-9a-fA-F]+)\"\s+#\s*\"(.*)\"(.*)", line)
            ports = match.group(1)
            uid = match.group(3)
            name = match.group(4)
            location = match.group(5)
            desc = f"UID: {uid} \nPORTS: {ports} \nNAME: {name} \nLOCATION: {location}"
            switches.append({"id": uid, "desc": desc})
            last_uid = uid
            last_type = match.group(2)
            
        elif re.search(r"\[[0-9]+\]", line):
            match = re.search(r"\"(H|S)-([0-9a-fA-F]+)\"", line)
            
            type = match.group(1)
            uid = match.group(2)
            
            
            source, target = tuple(sorted([last_uid, uid]))
            # links_data = {"source": source, "target": target, "width": 1}
            if (source, target) in links:
                links[(source, target)]['width'] += 4
            else:
                links[(source, target)] = {"width": 4, "source": source, "target": target, "backbone": type == "S"}
            
            # links.append((last_uid, uid, count))
            

    # Plot the graph using NetworkX
    # G = nx.Graph()
    # G.add_nodes_from(nodes + switches)
    # G.add_edges_from(links)
    # dot = nx.drawing.nx_pydot.to_pydot(G).to_string()
    
    graph = [
        {"group": "nodes", "data": s, "classes": ["switch"]} for s in switches
    ] + [
        {"group": "nodes", "data": n,  "classes": ["compute"]} for n in nodes
    ] + [
        {"group": "edges", "data": c}  for (s, t), c in links.items()
    ]
    
    return jsonify(graph)




@app.route('/')
def index_route():
    # Display the graph
    return render_template("index.html", content="", settings=settings)

@app.errorhandler(Exception)
def wrap_errors(error):
    """Decorator to wrap errors in a JSON response."""
    if app.debug:
        raise error
    return jsonify({"message": str(error)}), 500


@app.route('/graph')
def graph_route():
    # Display the graph

    data = subprocess.check_output(["ibnetdiscover", "-p"])
    text = data.decode("utf-8")
    return plot_graph(text)

if __name__ == '__main__':
    app.run()