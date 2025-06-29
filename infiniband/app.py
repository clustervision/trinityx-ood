import re
import os
import subprocess
import requests
from json import loads, dumps, JSONDecodeError

from flask import Flask, render_template, request, jsonify

from base.config import get_configs

STATE_PATH = os.path.join(os.path.dirname(__file__), "state.json")
CONFIGS = get_configs()

app = Flask(
    __name__, template_folder="templates", static_folder="static", static_url_path="/"
)


def _parse_severity(metric_name):
    if metric_name.startswith("delta_1h"):
        return "danger"
    return "warning"

@app.errorhandler(Exception)
def wrap_errors(error):
    """
    Decorator to wrap errors in a JSON response.
    """
    if app.debug:
        raise error
    return dumps({"message": str(error)}), 500


@app.context_processor
def inject_settings():
    return {"CONFIGS": CONFIGS}


def _parse_graph(graph_data, prometheus_data):
    """
    This method will parse the ibnetdiscover output into a graph.
    """

    node_regex = r"(Switch|Ca)\s+([0-9]+)\s+\"([SH]-[0-9a-z]+)\".*#.*\"(.*)\".*\n?(\[[0-9]+\].*\n)*"
    link_regex = r"\[([0-9]+)\].*\"([SH]-[0-9a-z]+)\".*\[([0-9]+)\].*#.*\"(.*)\""

    nodes_map = {}
    links_map = {}

    for switch_match in re.finditer(node_regex, graph_data, re.MULTILINE):
        type, uid  = switch_match.group(3).split("-")
        name = switch_match.group(4)
        n_ports = switch_match.group(2)

        node_id = uid
        node = {
            "uid": uid,
            "name": name,
            "n_ports": n_ports,
            "type": type
        }

        nodes_map[node_id] = node

        for link_match in re.finditer(link_regex, switch_match.group(0)):
            port_id = link_match.group(1)
            other_type, other_uid = link_match.group(2).split("-")
            other_name = link_match.group(4)
            other_port_id = link_match.group(3)
            
            
            if uid > other_uid:
                link_id = (uid, port_id, other_uid, other_port_id)
                link_type = type + other_type
                link =  {
                    "source_uid": uid,
                    "source_port_id": port_id,
                    "target_uid": other_uid,
                    "target_port_id": other_port_id,
                    "type": link_type,
                }
            else:
                link_id = (other_uid, other_port_id, uid, port_id)
                link_type = other_type + type
                link =  {
                    "source_uid": other_uid,
                    "source_port_id": other_port_id,
                    "target_uid": uid,
                    "target_port_id": port_id,
                    "type": link_type,
                }
            
            links_map[link_id] = link
            

    nodes = list(nodes_map.values())
    links = list(links_map.values())
    
    for link in links:
        source_uid = link['source_uid']
        source_port_id = link['source_port_id']
        target_uid = link['target_uid']
        target_port_id = link['target_port_id']
        
        source_errors = prometheus_data.get(source_uid, {}).get(source_port_id, {})
        target_errors = prometheus_data.get(target_uid, {}).get(target_port_id, {})
        
        source_errors_list = [(_parse_severity(k), f"{nodes_map[target_uid].get('name')} {source_uid}", k, v) for k, v in source_errors.items()]
        target_errors_list = [(_parse_severity(k), f"{nodes_map[target_uid].get('name')} {target_uid}", k, v) for k, v in target_errors.items()]
        
        merged_errors = source_errors_list + target_errors_list
        
        link['errors'] = merged_errors
        
    
    graph = {"nodes": nodes, "links": links} 
    return graph

def get_prometheus_data():
    try:
        series = [
            "infiniband_hca_port_symbol_error_total",
            "infiniband_hca_port_receive_errors_total",
            "infiniband_hca_port_local_link_integrity_errors_total",
            "infiniband_hca_port_receive_constraint_errors_total",
            "infiniband_hca_port_transmit_constraint_errors_total" ]
        
        queries = {
            "":{ "query": "max by (metric_name, guid, port) (label_replace({__name__=~'" + "|".join(series) + "'}, 'metric_name', '$1', '__name__', '(.+)'))"},
            "delta_1h_": {"query": "max by (metric_name, guid, port) ((label_replace({__name__=~'" + "|".join(series) + "'}, 'metric_name', '$1', '__name__', '(.+)')- label_replace({__name__=~'" + "|".join(series) + "'} offset 1h, 'metric_name', '$1', '__name__', '(.+)')))"},
        }
        data = {}
        for query_type, params in queries.items():

            response = requests.get(f"{CONFIGS['APP']['PROMETHEUS_ENDPOINT']}/api/v1/query", params=params, verify=False)

            for result in response.json()['data']['result']:
                guid = result['metric']['guid'][2:]
                port_id = result['metric']['port']
                metric = query_type + result['metric']['metric_name'].replace("infiniband_hca_port_", "", 1)
                value = result['value'][1]
                
                if guid not in data:
                    data[guid] = {}
                if port_id not in data[guid]:
                    data[guid][port_id] = {}
                if int(value) > 0:
                    data[guid][port_id][metric] = value
        
        return data
    except Exception as e:
        return {}

def save_graph_state(state):
    with open(STATE_PATH, "w") as f:
        f.write(dumps(state))

def get_graph_state():
    try:
        if os.path.exists(STATE_PATH):
            with open(STATE_PATH, "r") as f:
                return loads(f.read())
    except JSONDecodeError:
        pass
    return None

def get_graph_data():
    process = subprocess.run(
        CONFIGS['APP']['IBNETDISCOVER_CMD'] , stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    if process.returncode != 0:
        raise Exception(
            f"ibnetdiscover failed with code {process.returncode}:\n{process.stderr.decode('utf-8')}"
        )

    ibnetdiscover_output = process.stdout.decode("utf-8")    
    return ibnetdiscover_output





@app.route("/")
def index_route():
    """
    Route to get the index page.
    """

    return render_template("index.html", content="")

@app.route("/graph", methods=["GET"])
def graph_route():
    """
    Route to get the graph.
    """

    graph_data = get_graph_data()
    prometheus_data = get_prometheus_data()
    graph = _parse_graph(graph_data, prometheus_data)
    graph['state'] = get_graph_state()
    
    return jsonify(graph)
    

@app.route("/graph/state", methods=["POST"])
def graph_state_save_route():
    """
    Route to save the graph.
    """
    state = request.json
    save_graph_state(state)
    response = {"message": f"Saved state to {STATE_PATH}"}
    return dumps(response)



if __name__ == "__main__":
    from pprint import pprint
    
    pprint(get_prometheus_data())