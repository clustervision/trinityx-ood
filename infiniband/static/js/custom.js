const RED = "#FF0000";
const ORANGE = "#FFA500";
const GREY = "#222"

const slurm_idle = "#198754";
const slurm_down = "#6c757d";
const slurm_drain_other = "#ffc107"
const slurm_drain = "#dc3545"



function nodeRadius(node) {
    var baseRadius = Math.sqrt(node.n_ports);
    if (node.type == "S") {
        return baseRadius + 26;
    } else {
        return baseRadius + 21;
    }
}
function nodeImage(node) {
    var imageName = (node.type == "S") ? "switch.png" : "host.png";
    var imageUrl = `${window.location.href}/assets/${imageName}`;
    return imageUrl;
}
function nodeText(node) {
    if ((node.type == "S") && (node.name == 'SwitchIB Mellanox Technologies')) {
        return Array.prototype.concat('SwitchIB', node.uid).join(" ");
    } else {
        return node.name;
    }
}
function nodeStrokeWidth(highlighted) {
    return (highlighted) ? 3 : 1.5;
}
function linkStroke(l) {
    hasDanger = false
    hasWarning = false


    for (const errors of l.errors) {
        Object.keys(errors).forEach((key) => {
            if (errors[key][0] == "danger") {
                hasDanger = true;
            } else if (errors[key][0] == "warning") {
                hasWarning = true;
            }
        }
    )}

    if (hasDanger) {
        return RED;
    }
    if (hasWarning) {
        return ORANGE;
    }
    return GREY;
}
function linkStrokeWidth(l, highlighted) {
    return (highlighted) ? l.count + 3 : l.count + 1;
}
function linkRotationAngle(d) {
    var angle = Math.atan2(d.target.y - d.source.y, d.target.x - d.source.x);
    var angleDeg = ((angle * 180 / Math.PI) + 360) % 360;
    return angleDeg
}
function linkLabelTransform(d, type){
    var angle = d.angle;
    var rotation = (angle > 270 || angle < 90) ? 0 : 180;
    var radius = nodeRadius(d.source)
    var startPosition = radius + 10;
    var endPosition = Math.sqrt(Math.pow(d.target.x - d.source.x, 2) + Math.pow(d.target.y - d.source.y, 2)) - radius - 10;
    var translation = (type == "source") ? startPosition : endPosition;

    return `translate(${translation}, 0) rotate(${rotation})`;
}
function linkLabelAnchor(d, type){
    var angle = d.angle;
    var isRotated = (angle > 270 || angle < 90);
    var isSource = (type == "source");
    var anchor = (isRotated ^ isSource) ? "end" : "start";

    return anchor;
}
function strokeOpacity(highlighted) {
    return (highlighted) ? 0.8 : 0.3;
}
function wrapText(text, width) {
    text.each(function () {
        var text = d3.select(this),
            words = text.text().split(/\s+/).reverse(),
            word,
            line = [],
            lineNumber = 0,
            lineHeight = 1.1, // ems
            y = text.attr("y"),
            dy = parseFloat(text.attr("dy")),
            tspan = text.text(null).append("tspan").attr("x", 0).attr("y", y).attr("dy", dy + "em");
        while (word = words.pop()) {
            line.push(word);
            tspan.text(line.join(" "));
            if (tspan.node().getComputedTextLength() > width) {
                line.pop();
                tspan.text(line.join(" "));
                line = [word];
                tspan = text.append("tspan").attr("x", 0).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
            }
        }
    });
}

function slurm_info() {
    var url = window.location.href.replace('#', '') + "/slurm_info";
    console.debug("Calling:", url);

    return new Promise((resolve, reject) => {
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            success: function(response_data) {
                console.debug("Response:", response_data);
                if (response_data.status) {
                    let node_list = response_data.response;
                    if (typeof node_list === "string") {
                        try {
                            node_list = JSON.parse(node_list);
                        } catch (e) {
                            console.error("Invalid JSON:", node_list);
                            node_list = [];
                        }
                    }

                    resolve(node_list);
                } else {
                    resolve([]);
                }
            },
            error: function(err) {
                reject(err);
            }
        });
    });
}


function updateSlurmColors() {
    slurm_info().then(ress => {
        const slurmStateMap = {};
        const slurmReasonMap = {};

        ress.forEach(item => {
            slurmStateMap[item.name] = item.state;
            if (item.reason) slurmReasonMap[item.name] = item.reason;
        });

        // Update colors
        window.graph.nodeItems.attr("fill", d => {
            if (d.type !== "H") return "#CCC";

            const nodeName = d.name.split(" ")[0];

            const state = slurmStateMap[nodeName];
            const reason = slurmReasonMap[nodeName];

            if (!state) return "#CCC";

            let finalState = state.toLowerCase();

            console.debug(`Node: ${nodeName}, State: ${finalState}, Reason: ${reason}`);

            if (finalState === "drain") {
                if (reason !== "IB Analyzer drained node") {
                    finalState = "drain_other";
                }
            }

            switch (finalState) {
                case "idle": return slurm_idle;
                case "down": return slurm_down;
                case "drain": return slurm_drain;
                case "drain_other": return slurm_drain_other;
                default: return "#CCC";
            }

        });
    });
}


const Context = {
    
    svg: null,
    containerItem: null,
    nodeContainerItems: null,
    linkItems: null,
    nodeItems: null,
    nodeImageItems: null,
    ndeLabelItems: null,
    zoomItem: null,

    data: null,
    nodesTable: null,
    _simulation: null,

    width() {
        return $("#graph").parent().width();
    },
    height() {
        return window.innerHeight * 0.80;
    },
    links() {
        return this.data.links;
    },
    aggLinks() {
        const _aggLinks = {}
        for (const link of this.data.links) {
            const key = `${link.source_uid}.${link.target_uid}`;
            const sourcePortId = link.source_port_id;
            const targetPortId = link.target_port_id;
            const errors = link.errors;
            if ( ! _aggLinks[key]) {
                _aggLinks[key] = [];
            }
            _aggLinks[key].push({sourcePortId, targetPortId, errors});
        }


        const aggLinks = Object.keys(_aggLinks).map((key) => {
            var [sourceUid, targetUid] = key.split(".");
            return {
                source: this.data.nodes.find(n => n.uid == sourceUid),
                target: this.data.nodes.find(n => n.uid == targetUid),
                source_uid: sourceUid,
                target_uid: targetUid,
                errors: _aggLinks[key].map(l => l.errors),
                source_port_ids: _aggLinks[key].map(l => l.sourcePortId),
                target_port_ids: _aggLinks[key].map(l => l.targetPortId),
                count: _aggLinks[key].length
            }
        });

        


        return aggLinks;
    },
    nodes() {
        return this.data.nodes;
    },
    computeNodes() {
        return this.nodes().filter(d => d.type == "H");
    },
    switchNodes() {
        return this.nodes().filter(d => d.type == "S");
    },
    switchLinks() {
        return this.links().filter(d => d.source.type == "S" && d.target.type == "S");
    },
    getSimulationType() {
        return $("#simulation-type").val();
    },
    setSimulationType(type) {
        $("#simulation-type").val(type);

    },
    onchangeSimulationType() {
        this._simulation = this.simulation();
    },

    getDirectHostsForSwitch(uid) {
        const connections = this.getSwitchHostConnections();
        if (!connections[uid]) return [];
        
        return connections[uid].connectedHosts.map(h => ({
            name: h.host.name.split(" ")[0],
            uid: h.host.uid,
            type: h.host.type
        }));
    },

    getHostsForSwitch(uid) {
        const directHosts = this.getDirectHostsForSwitch(uid);
        const connections = this.getSwitchHostConnections();
        const sw = connections[uid];

        // Optionally include child switches’ hosts if needed
        if (!sw) return directHosts;

        const childHosts = sw.connectedSwitches.flatMap(child =>
            this.getDirectHostsForSwitch(child.switch.uid)
        );

        return [...directHosts, ...childHosts];
    },
    
    // Add this method to your Context object (inside the Context object)
    // Build mapping of switch -> { switch, connectedHosts: [], connectedSwitches: [], hostCount }
    getSwitchHostConnections() {
        const switchConnections = {};

        // Initialize an empty structure for each switch
        this.switchNodes().forEach(switchNode => {
            switchConnections[switchNode.uid] = {
                switch: switchNode,
                connectedHosts: [],
                connectedSwitches: [],
                hostCount: 0
            };
        });

        // Walk all links and populate either connectedHosts or connectedSwitches
        this.links().forEach(link => {
            const src = link.source;
            const tgt = link.target;

            // If link is switch -> host or host -> switch, add host to the switch entry
            if (src.type === "S" && tgt.type === "H") {
                if (switchConnections[src.uid]) {
                    switchConnections[src.uid].connectedHosts.push({ host: tgt, link });
                    switchConnections[src.uid].hostCount++;
                }
            } else if (src.type === "H" && tgt.type === "S") {
                if (switchConnections[tgt.uid]) {
                    switchConnections[tgt.uid].connectedHosts.push({ host: src, link });
                    switchConnections[tgt.uid].hostCount++;
                }
            }

            // If link is switch -> switch (either direction), add each other as connected switches
            if (src.type === "S" && tgt.type === "S") {
                if (switchConnections[src.uid]) {
                    // avoid duplicates: only push if not already present
                    if (!switchConnections[src.uid].connectedSwitches.some(s => s.switch.uid === tgt.uid)) {
                        switchConnections[src.uid].connectedSwitches.push({ switch: tgt, link });
                    }
                }
                if (switchConnections[tgt.uid]) {
                    if (!switchConnections[tgt.uid].connectedSwitches.some(s => s.switch.uid === src.uid)) {
                        switchConnections[tgt.uid].connectedSwitches.push({ switch: src, link });
                    }
                }
            }
        });

        // Debug: inspect mapping quickly in console
        console.debug("getSwitchHostConnections()", Object.keys(switchConnections).length, switchConnections);

        return switchConnections;
    },


    // This method print the connections
    printSwitchHostConnections() {
        const connections = this.getSwitchHostConnections();
        const switch_nodes = [];

        Object.values(connections).forEach(connection => {
            const switchInfo = {
                switch: connection.switch.name,
                uid: connection.switch.uid,
                node_list: connection.connectedHosts.map(hostInfo => ({
                    name: hostInfo.host.name,
                    uid: hostInfo.host.uid,
                    type: hostInfo.host.type
                })).concat(
                    (connection.connectedSwitches || []).map(sw => ({
                        name: sw.switch.name,
                        uid: sw.switch.uid,
                        type: "S"
                    }))
                )
            };
            switch_nodes.push(switchInfo);
        });

        return switch_nodes;
    },

    getAllConnectedHosts(startSwitchUid) {
        const visitedSwitches = new Set();
        const resultHosts = new Map();
        const switchMap = {};
        const nodeTypeMap = {};
        const connections = this.printSwitchHostConnections();
        connections.forEach(item => {
            switchMap[item.uid] = item.node_list;
            item.node_list.forEach(node => {
                nodeTypeMap[node.uid] = node;
            });
        });

        const traverse = (switchUid) => {
            if (visitedSwitches.has(switchUid)) return;
            visitedSwitches.add(switchUid);
            const connected = switchMap[switchUid] || [];
            connected.forEach(node => {
                if (node.type === "S") {
                    traverse(node.uid);
                } else {
                    resultHosts.set(node.uid, node);
                }
            });
        };
        traverse(startSwitchUid);
        return Array.from(resultHosts.values());
    },


    simulation() {
        var simulationType = this.getSimulationType();
        
        if ( this._simulation != null) {
            this._simulation.stop();
        }
        if (simulationType == 'all') {
            this.switchNodes().forEach((d) => {
                d.fx = null;
                d.fy = null;
            });
        } else {
            this.switchNodes().forEach((d) => {
                d.fx = d.x;
                d.fy = d.y;
            });
        }
        
        if (simulationType == 'all') {
            return d3.forceSimulation(this.nodes())
                .force("link", d3.forceLink(this.links()).id(d => d.uid))
                .force("charge", d3.forceManyBody().strength( -1600 ))
                .force("collide", d3.forceCollide().radius(d => nodeRadius(d) + 30).strength(0.4))
                .force("center", d3.forceCenter(this.width() / 2, this.height() / 2))
                .on("tick", () => this.ticked());
        } else if (simulationType == 'compute') {
            return  d3.forceSimulation(this.nodes())
                .force("link", d3.forceLink(this.links()).id(d => d.uid))
                .force("charge", d3.forceManyBody().strength( -1600 ))
                .force("collide", d3.forceCollide().radius(d => nodeRadius(d) + 30).strength(0.4))
                .on("tick", () => this.ticked());

        } else if (simulationType == 'none') {
            return  d3.forceSimulation(this.nodes())
                    .force("collide", d3.forceCollide().radius(d => nodeRadius(d) + 30).strength(0.4))
                    .on("tick", () => this.ticked())
        }

    },
    getLabelType() {
        return $("#label-type").val();
    },
    setLabelType(type) {
        $("#label-type").val(type);
    },
    onchangeLabelType() {
        this.showlabel();
    },
    nodeselected(uid, scrollToRow) {
        this.nodeItems.style('stroke-opacity', on => strokeOpacity(on.uid == uid));
        this.nodeItems.style('stroke-width', on =>  nodeStrokeWidth(on.uid == uid));
        this.linkItems.style('stroke-opacity', l => strokeOpacity(l.source.uid == uid || l.target.uid == uid));
        this.linkItems.style('stroke-width', l => linkStrokeWidth(l,(l.source.uid == uid || l.target.uid == uid)));
        if (scrollToRow) {
            const rows = this.nodesTable.searchRows([{field: 'uid', type: '=', value: uid}]);
            this.nodesTable.selectRow(rows);
            this.nodesTable.scrollToRow(rows[0], "top", false);
        }
    },
    linkselected(source_uid, target_uid, scrollToRow) {
        this.nodeItems.style('stroke-opacity', n => strokeOpacity(n.uid == source_uid || n.uid == target_uid));
        this.nodeItems.style('stroke-width', n =>  nodeStrokeWidth(n.uid == source_uid || n.uid == target_uid));
        this.linkItems.style('stroke-opacity', ol => strokeOpacity((source_uid == ol.source.uid && target_uid == ol.target.uid) || (source_uid == ol.target.uid && target_uid == ol.source.uid)));
        this.linkItems.style('stroke-width', ol => linkStrokeWidth(ol,((source_uid == ol.source.uid && target_uid == ol.target.uid) || (source_uid == ol.target.uid && target_uid == ol.source.uid))));        
        if (scrollToRow) {
            const rows = this.linksTable.searchRows([{field: 'source_uid', type: '=', value: source_uid}, {field: 'target_uid', type: '=', value: target_uid}]);
            this.linksTable.selectRow(rows);
            this.linksTable.scrollToRow(rows[0], "top", false);
        }
    },
    unselected() {
        this.nodesTable.deselectRow();
        this.linksTable.deselectRow();
        this.nodeItems.style('stroke-opacity', strokeOpacity(false));
        this.nodeItems.style('stroke-width', nodeStrokeWidth(false));
        this.linkItems.style('stroke-opacity', strokeOpacity(false));
        this.linkItems.style('stroke-width', l => linkStrokeWidth(l,false));
    },
    showlabel() {
        var labelType = this.getLabelType();

        this.nodeLabelItems.attr("style", "display: none;");
        this.linkSourceLabelItems.attr("style", "display: none;");
        this.linkTargetLabelItems.attr("style", "display: none;");

        if (labelType == "all") {
            this.nodeLabelItems.attr("style", "");
            this.linkSourceLabelItems.filter((d) => (d.source.type == "S") && (d.target.type == "S")).attr("style", "");
            this.linkTargetLabelItems.filter((d) => (d.source.type == "S") && (d.target.type == "S")).attr("style", "");
        } else if (labelType == "nodes") {
            this.nodeLabelItems.attr("style", "");
        } else if (labelType == "links") {
            this.linkSourceLabelItems.attr("style", "");
            this.linkTargetLabelItems.attr("style", "");
        }
    },
    dragstarted(event) {

        if (this.getSimulationType() == 'all'){
            this.setSimulationType('compute');
            this._simulation = this.simulation();
        }

        if (!event.active) this._simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    },
    dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    },
    dragended(event) {
        if (!event.active) this._simulation.alphaTarget(0);
        if ( event.subject.type != "S" ) {
            event.subject.fx = null;
            event.subject.fy = null;
        }
        // event.subject.fx = null;
        // event.subject.fy = null;
    },
    _containerInitialized() {
        // Set the container height to 80% of the window height
        var canvasHeight = window.innerHeight * 0.80;
        $("#app-container .row").height(canvasHeight);

    },
    async _graphInitialized() {
        var legendKeys = [`Switches: ${this.switchNodes().length}`, `Nodes: ${this.computeNodes().length}`, `Links: ${this.links().length}`];


        this.svg = d3.select("#graph").append("svg")
            .attr("width", this.width())
            .attr("height", this.height())
            .attr("viewBox", [0, 0, this.width(), this.height()])
            .attr("style", "max-width: 100%; height: auto;")

        this.svg.append('g')
            .attr("class", "legend")
            .selectAll("text")
            .data(legendKeys)
            .enter()
            .append("text")
            .attr("x", 0)
            .attr("y", (d, i) => (i+1) * 20)
            .text(d => d)


        this.containerItem = this.svg.append("g")
            .attr("class", "container")
            .attr("style", "display: none;")

        this.linkContainerItems = this.containerItem.append("g")
            .selectAll()
            .data(this.aggLinks())
            .join('g')

        this.linkItems = this.linkContainerItems.append("line")
            .attr("stroke-width", l => linkStrokeWidth(l, false))
            .attr("stroke", l => linkStroke(l))
            .attr("stroke-opacity", strokeOpacity(false))

        this.linkSourceLabelItems = this.linkContainerItems.append("text")
            .attr("text-anchor", "start")
            .attr("x", 0)
            .attr("y", 0)
            .attr("dy", 0)
            .text( d => d.source_port_ids)
            .attr("style", "display: none;")
        
        this.linkTargetLabelItems = this.linkContainerItems.append("text")
            .attr("text-anchor", "end")
            .attr("x", 0)
            .attr("y", 0)
            .attr("dy", 0)
            .text( d => d.target_port_ids ) 
            .attr("style", "display: none;")
        

        this.nodeContainerItems = this.containerItem.append("g")
            .selectAll()
            .data(this.nodes())
            .join("g")

        this.nodeItems = this.nodeContainerItems.append("circle")
            .attr("stroke", "#222")
            .attr("stroke-opacity", strokeOpacity(false))
            .attr("stroke-width", nodeStrokeWidth(false))
            .attr("fill", d => "#CCC")
            .attr("r", d => nodeRadius(d))

            slurm_info().then(ress => {
                const slurmStateMap = {};
                ress.forEach(item => slurmStateMap[item.name] = item.state);

                this.nodeItems.attr("fill", d => {
                    if (d.type !== "H") return "#CCC"; // only hosts

                    const slurmInfo = slurmStateMap[d.name.split(" ")[0]]; // get node info
                    if (!slurmInfo) return "#CCC";

                    let state = slurmInfo.toLowerCase();

                    // Special handling for drain reason
                    if (state === "drain") {
                        if (slurmInfo.reason !== "IB Analyzer drained node") {
                            state = "drain_other";
                        }
                    }

                    switch (state) {
                        case "idle":       return slurm_idle;
                        case "down":       return slurm_down;
                        case "drain":      return slurm_drain;
                        case "drain_other":return slurm_drain_other;
                        default:           return "#CCC";
                    }
                });

                // this.nodeItems.attr("fill", d => {
                //     if (d.type !== "H") return "#CCC"; // only hosts

                //     const state = slurmStateMap[d.name.split(" ")[0]];
                //     if (!state) return "#CCC";

                //     switch (state.toLowerCase()) {
                //         case "idle":  return slurm_idle;
                //         case "down":  return slurm_down;
                //         case "drain": return slurm_drain;
                //         case "drain_other": return slurm_drain_other;
                //         default: return "#CCC";
                //     }
                // });
            });


        window.graph = this;
        
        this.nodeImageItems = this.nodeContainerItems.append("image")
            .attr("class", "right-click")
            .attr("device_type", node => node.type)
            .attr("xlink:href", nodeImage)
            .attr("x", d => -nodeRadius(d) * 0.7)
            .attr("y", d => -nodeRadius(d) * 0.7)
            .attr("width", d => nodeRadius(d) * 0.7 * 2)
            .attr("height", d => nodeRadius(d) * 0.7 * 2)

            // Apply node_list to each <image> dynamically
            this.nodeImageItems
                .attr("node_list", d => {
                    if (d.type === "S") {
                        const hosts = this.getHostsForSwitch(d.uid);
                        return JSON.stringify(hosts);
                    }
                    return "[]";
                });

        this.nodeLabelItems = this.nodeContainerItems.append("text")
            .attr("text-anchor", "middle")
            .attr("alignment-baseline", "middle")
            .text( d => nodeText(d))
            .attr("x", 0)
            .attr("y", d => nodeRadius(d) + 12)
            .attr("dy", 0)
            .call(wrapText, 100)
            .attr("style", "display: none;")
        

        this.zoomItem = d3.zoom().scaleExtent([0.1, 4])
        this.dragItem = d3.drag()

        this.svg.call(this.zoomItem.on("zoom", ({transform}) => {
            this.containerItem.attr("transform", transform);
        }))
    
        this.nodeContainerItems.call(this.dragItem
                    .on("start", (e) => this.dragstarted(e))
                    .on("drag", (e) => this.dragged(e))
                    .on("end", (e) => this.dragended(e)))
            
        this.nodeContainerItems.on("mouseover", (e) => {
            n = d3.select(e.target).datum();
            this.nodeselected(n.uid, true);
        });
        this.nodeContainerItems.on("mouseout", (e) => {
            this.unselected();
        });
        this.linkContainerItems.on("mouseover", (e) => {
            l = d3.select(e.target).datum();
            this.linkselected(l.source.uid, l.target.uid, true)

        });
        this.linkContainerItems.on("mouseout", (e) => {
            this.unselected();
        });


        if (this.data?.state?.nodePositions){
            this.nodes().forEach((d) => {
                var nodePosition = this.data.state.nodePositions.find(n => n.uid == d.uid);
                if (nodePosition) {
                    d.x = nodePosition.x;
                    d.y = nodePosition.y;
                }
            })
        }
        if (this.data?.state?.zoom){
            this.svg.call(this.zoomItem.transform, d3.zoomIdentity.translate(this.data.state.zoom.x, this.data.state.zoom.y).scale(this.data.state.zoom.k));
        } else {
            this.svg.call(this.zoomItem.transform, d3.zoomIdentity.scale(0.5));
        }

        if (this.data.state?.simulationType){
            this.setSimulationType(this.data.state.simulationType);
        }
        this._simulation = this.simulation()

        if (this.data.state?.labelType){
            this.setLabelType(this.data.state.labelType);
        }
        this.showlabel()

    },
    async _nodesTableInitialized() {
        this.nodesTable = new Tabulator("#nodes-table", {
            data: this.data.nodes,           //load row data from array
            layout:"fitColumns",
            height:this.height()/2,
            columns:[                        //define the nodesTable columns
                {title: "Name", field: "name"},
                {title: "Type", field: "type", width:10 },
                {title: "UID",  field: "uid"},
                {title: "Ports", field: "n_ports", width:10 },
            ],
            // dataTree:true,
        });

        this.nodesTable.on("rowMouseOver", (e, row) =>{
            var data = row.getData();
            this.nodeselected(data.uid);
        });

        this.nodesTable.on("rowMouseOut", () => {
            this.unselected()
        });
    },
    async _linksTableInitialized() {
        this.linksTable = new Tabulator("#links-table", {
            data: this.data.links,           //load row data from array
            layout:"fitColumns",
            height:this.height()/2,
            columns:[                        //define the linksTable columns
                {title: "Source UID", field: "source_uid"},
                {title: "Source Port", field: "source_port_id", width:10 },
                {title: "Type", field: "type", width:10 },
                {title: "Target UID", field: "target_uid"},
                {title: "Target Port", field: "target_port_id", width:10 },
                {title: "E", field: "n_errors", width:10 },
                {title: "W", field: "n_warnings", width:10 },
            ],
            initialSort:[
                {column:"source_uid", dir:"asc"},
                {column:"target_uid", dir:"asc"},
                {column:"n_warnings", dir:"desc"},
                {column:"n_errors", dir:"desc"},
            ],
            rowFormatter:function(row){
                //create and style holder elements
                const errors = row.getData().errors;

                const listElement = document.createElement("ul");
                const holderElement = document.createElement("div");
                
                row.getElement().appendChild(holderElement);
                holderElement.appendChild(listElement);
                for ( const [severity, origin, metric, value] of errors) {
                    const listItem = document.createElement("li");
                    listItem.textContent = `[${origin}] ${metric} (${value}) `;
                    
                    switch (severity) {
                        case "danger":
                            listItem.style.color = RED;
                            break;
                        case "warning":
                            listItem.style.color = ORANGE;
                            break;
                        default:
                            listItem.style.color = GREY;
                            break;
                    }

                    listElement.appendChild(listItem);
                };
            },
        });

        this.linksTable.on("rowMouseOver", (e, row) =>{
            var data = row.getData();
            this.linkselected(data.source_uid, data.target_uid);
        });

        this.linksTable.on("rowMouseOut", () => {
            this.unselected()
        });
    },
    async _menuInitialized() {
        $('#save-graph').click(() => this.saved());
        $("#simulation-type").change(() => this.onchangeSimulationType());
        $("#label-type").change(() => this.onchangeLabelType());

        $("#all-label-button").click(() => this.showlabel("all"));
        $("#node-label-button").click(() => this.showlabel("node"));
        $("#link-label-button").click(() => this.showlabel("link"));
        $("#none-label-button").click(() => this.showlabel("none"));
    },
    async initialized() {
        this._containerInitialized();
        this._nodesTableInitialized();
        this._linksTableInitialized();
        this._graphInitialized();
        this._menuInitialized();
    },
    load() {
        // Get the current url without any trailing slash
        var currentUrl = window.location.href.replace(/\/$/, "");
        var url = `${currentUrl}/graph`;
        var successCallback = (data) => {

            data.links.forEach((link) => {
                var source = data.nodes.find(node => node.uid == link.source_uid);
                var target = data.nodes.find(node => node.uid == link.target_uid);
                var n_errors = 0
                var n_warnings = 0
                link.errors.forEach((errors) => {
                        if (errors[0] == "danger") {
                            n_errors += 1;
                        } else if (errors[0] == "warning") {
                            n_warnings += 1;
                        }
                    });


                link.source = source;
                link.target = target;
                link.n_errors = n_errors;
                link.n_warnings = n_warnings;
            });

            this.data = data
            this.initialized()
        }
        var failureCallback = (request) => {
            response = JSON.parse(request.responseText);
            displayAlert("danger", response.message)
        }

        $.ajax({
            url: url,
            type: "GET",
            contentType: "application/json",
            dataType: "json",
            success: successCallback,
            error: failureCallback
        });
    },
    ticked() {
        this.containerItem.attr("style", "display: block;");
        
        this.linkItems.attr("x1", 0)
                      .attr("y1", 0)
                      .attr("x2", d => Math.sqrt(Math.pow(d.target.x - d.source.x, 2) + Math.pow(d.target.y - d.source.y, 2)))
                      .attr("y2", 0 )

        this.linkContainerItems.each((d) => { d.angle = linkRotationAngle(d); })

        this.linkContainerItems.attr("transform", d => `translate(${d.source.x}, ${d.source.y}) rotate(${d.angle})`)
        this.nodeContainerItems.attr("transform", d => `translate(${d.x}, ${d.y})`)

        this.linkSourceLabelItems.attr("transform", d => linkLabelTransform(d, "source"))
        this.linkTargetLabelItems.attr("transform", d => linkLabelTransform(d, "target"))
        this.linkSourceLabelItems.attr("text-anchor", d => linkLabelAnchor(d, "source"))
        this.linkTargetLabelItems.attr("text-anchor", d => linkLabelAnchor(d, "target"))
        
    },
    saved() {
        var url = `${window.location.href}/graph/state`;
        var state = this.getState();

        var successCallback = (data) => { 
            displayAlert("success", data.message)
        }
        var failureCallback = (error) => {
            displayAlert("danger", error.message)
        }

        $.ajax({
            url: url,
            type: "POST",
            data: JSON.stringify(state),
            contentType: "application/json",
            dataType: "json",
            success: successCallback,
            error: failureCallback
        });
    },
    getState() {
        var currentTransform = d3.zoomTransform(context.containerItem.node())

        var state = {
            simulationType: this.getSimulationType(),
            labelType: this.getLabelType(),
            nodePositions: this.nodes().map(d => { return {uid: d.uid, x: d.x, y: d.y} }),
            zoom: {x: currentTransform.x, y: currentTransform.y, k: currentTransform.k}
        }
        return state;
    },
    resized() {
        console.debug(`Resized to ${this.width()} x ${this.height()}`)
        this.svg.attr("width", this.width())
                .attr("height", this.height())
                .attr("viewBox", [0, 0, this.width(), this.height()])
        this.nodesTable.setHeight(this.height()/2);
        this.linksTable.setHeight(this.height()/2);
    },




}

var context;
window.onload = function () {
    context = Object.create(Context)
    context.load();
    window.onresize = function () {
        context.resized();
    }
}


function control_action(system, action, device){
    var url = window.location.href
    url = url.replace('#','');
    url = url+'/perform/'+system+'/'+action+'/'+device;
    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        contentType: 'application/json; charset=UTF-8',
        success: function(response_data) {
            result = '<div class="alert alert-'+response_data.status+'" role="alert">'+response_data.message+'</div>';
            // console.log(result);
            $('#ajax').html();
            $('#ajax').html(result);
            setTimeout(function(){ $('#ajax').html(''); }, 5000);  
            
        }
    });
}


function slurm_action(nodes, action){
    var url = window.location.href
    url = url.replace('#','');
    url = `${url}/slurm_action/${action}`;
    console.debug(url);
    let payload = [];

    if (nodes.trim().startsWith("[") && nodes.trim().endsWith("]")) {
        try {
            let nodeList = JSON.parse(nodes);
            payload = nodeList.map(node => node.name);
        } catch {
            payload = [];
        }
    } else {
        payload = [nodes];
    }
    
    $.ajax({
        url: url,
        type: 'POST',
        data: JSON.stringify(payload),
        dataType: 'json',
        contentType: 'application/json; charset=UTF-8',
        success: function(response_data) {
            console.debug("response_data:", response_data);
            if (response_data.status) {
                result = `
                <div class="alert alert-success alert-dismissible fade show  d-flex align-items-center" role="alert">
                    <svg class="bi flex-shrink-0 mr-2" width="24" height="24" role="img" aria-label="Success:"><use xlink:href="#check-circle-fill"/></svg>
                    <div><strong>Success:</strong> ${response_data.data}</div>
                    <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                </div>`;
                $('#ajax').html(result);
                if (action === "drain"){
                    updateSlurmColors();
                } else { setTimeout(function(){ updateSlurmColors(); }, 5000); }
                
                setTimeout(function(){ $('#ajax').html(''); }, 30000); 
            } else {
                result = `
                <div class="alert alert-danger alert-dismissible fade show  d-flex align-items-center" role="alert">
                    <svg class="bi flex-shrink-0 mr-2" width="24" height="24" role="img" aria-label="Danger:"><use xlink:href="#exclamation-triangle-fill"/></svg>
                    <div><strong>Failed:</strong> ${response_data.data}</div>
                    <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                </div>`;
                $('#ajax').html(result);
                setTimeout(function(){ $('#ajax').html(''); }, 30000); 
            }
        }
    });
}


function createMenu(e, title, items) {
    var menu = $('<ul class="contextMenuPlugin"><div class="gutterLine"></div></ul>').appendTo(document.body);
    if (title) { $('<li class="header"></li>').text(title).appendTo(menu); }
    items.forEach(function(item) {
        if (item) {
        var rowCode = '<li><a href="#"><span></span></a></li>';
        var row = $(rowCode).appendTo(menu);
        if(item.icon){
            var icon = $('<img>');
            icon.attr('src', item.icon);
            icon.insertBefore(row.find('span'));
        }
        row.find('span').text(item.label);
        if (item.action) {
            row.find('a').click(function(){ item.action(e); });
        }
        } else { $('<li class="divider"></li>').appendTo(menu); }
    });
    menu.find('.header').html(title);
    return menu;
}

$(document).ready(function () {
    $(document).on('contextmenu', '.right-click', function (e) {
        e.preventDefault();

        var url = window.location.href
        url = url.replace('#','');
        var device_type = $(this).attr("device_type");
        var node_list = $(this).attr("node_list");
        var g = $(this).closest('g');
        var device_name = g.find('text tspan').first().text();


        // var device_color_code = g.find('circle').attr('fill');
        // var device_state = "default"
        // switch (device_color_code) {
        //     case slurm_idle:       device_state = "slurm_idle";
        //     case slurm_down:       device_state = "slurm_down";
        //     case slurm_drain:      device_state = "slurm_drain";
        //     case slurm_drain_other:  device_state = "slurm_drain_other";
        //     default:           device_state = "#CCC";
        // }
        // if (device_state.includes("#ffc107")) {
        //     device_state = "slurm_drain_other";
        // }


        if (device_type === "H"){
            var title = '<img class="device-icon" src="'+url+'/base/icons/processor.png" />   <strong>'+device_name+' Settings</strong>';
            info = url + "trinity_node/show/"+device_name;
            edit = url + "trinity_node/edit/"+device_name;
            rename = url + "trinity_node/rename/"+device_name;
            clone = url + "trinity_node/clone/"+device_name;
        } else if (device_type === "S"){
            var title = '<img class="device-icon" src="'+url+'/base/icons/switch-network.png" />   <strong>'+device_name+' Settings</strong>';
            info = url + "trinity_switch/show/"+device_name;
            edit = url + "trinity_switch/edit/"+device_name;
            rename = url + "trinity_switch/rename/"+device_name;
            clone = url + "trinity_switch/clone/"+device_name;
        }
        var items =[
            {label:'Details',               icon: url + '/base/icons/application-detail.png',       action: function(e) { e.preventDefault(); window.open(info, '_blank').focus(); }  },
        ];
        if (device_type == "H"){
            items.push(
                null,
                {label: `Drain Node ${device_name}`,    icon: url + '/base/icons/task--minus.png',   action: function(e) { e.preventDefault(); slurm_action(device_name, "drain"); }  },
                {label: `Resume Node ${device_name}`,    icon: url + '/base/icons/task--plus.png',   action: function(e) { e.preventDefault(); slurm_action(device_name, "resume"); }  },
                null,
                {label:'Power Status',          icon: url + '/base/icons/application-monitor.png',      action: function(e) { e.preventDefault(); control_action('power', 'status', device_name); } },
                {label:'Power Off',             icon: url + '/base/icons/network-status-busy.png',      action: function(e) { e.preventDefault(); control_action('power', 'off', device_name); } },
                {label:'Power ON',              icon: url + '/base/icons/network-status.png',           action: function(e) { e.preventDefault(); control_action('power', 'on', device_name); } },
                {label:'Power Reset',           icon: url + '/base/icons/network-status-away.png',      action: function(e) { e.preventDefault(); control_action('power', 'reset', device_name); } },
                null,
                {label:'Sel List',              icon: url + '/base/icons/application.png',              action: function(e) { e.preventDefault(); control_action('sel', 'list', device_name); } },
                {label:'Sel Clear',             icon: url + '/base/icons/application--minus.png',       action: function(e) { e.preventDefault(); control_action('sel', 'clear', device_name); } },
                null,
                {label:'Chassis Identify',      icon: url + '/base/icons/television.png',               action: function(e) { e.preventDefault(); control_action('chassis', 'identify', device_name); } },
                {label:'Chassis No Identify',   icon: url + '/base/icons/television--exclamation.png',  action: function(e) { e.preventDefault(); control_action('chassis', 'noidentify', device_name); } },
                // null,
                // {label:'Redfish Upload',     icon: url + '/base/icons/application-table.png',             action: function(e) {control_action('redfish', 'upload', device); } },
                // {label:'Redfish Setting',     icon: url + '/base/icons/application-table.png',             action: function(e) { control_action('redfish', 'setting', device); } },
            );
        }
        if (device_type == "S"){
            items.push(
                null,
                {label:'Drain All Nodes',       icon: url + '/base/icons/task--minus.png',       action: function(e) { e.preventDefault(); slurm_action(node_list, "drain"); }  },
                {label:'Resume All Nodes',       icon: url + '/base/icons/task--plus.png',       action: function(e) { e.preventDefault(); slurm_action(node_list, "resume"); }  },
            );
        }
        var menu = createMenu(e, title, items).show().css({zIndex:1000001, left:e.pageX + 5, top:e.pageY}).bind('contextmenu', function() { return false; });
        var bg = $('<div></div>').css({left:0, top:0, width:'1000%', height:'1000%', position:'absolute', zIndex:1000000}).appendTo(document.body)
        .bind('contextmenu click', function(e) {
            e.preventDefault();
            bg.remove();
            menu.remove();
            return false;
        });

        menu.find('a').click(function(e) {
            e.preventDefault();
        bg.remove();
        menu.remove();
        });

        return false;
    });
});
