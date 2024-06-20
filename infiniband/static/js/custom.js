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
        return $("#graph").parent().height();
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
            if ( ! _aggLinks[key]) {
                _aggLinks[key] = [];
            }
            _aggLinks[key].push({sourcePortId, targetPortId});
        }
        const aggLinks = Object.keys(_aggLinks).map((key) => {
            var [sourceUid, targetUid] = key.split(".");
            return {
                source: this.data.nodes.find(n => n.uid == sourceUid),
                target: this.data.nodes.find(n => n.uid == targetUid),
                source_uid: sourceUid,
                target_uid: targetUid,
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
            // .attr("transform", "translate(10, 10)")
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
            .attr("stroke", "#222")
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

        this.nodeImageItems = this.nodeContainerItems.append("image")
            .attr("xlink:href", nodeImage)
            .attr("x", d => -nodeRadius(d) * 0.7)
            .attr("y", d => -nodeRadius(d) * 0.7)
            .attr("width", d => nodeRadius(d) * 0.7 * 2)
            .attr("height", d => nodeRadius(d) * 0.7 * 2)

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
                {title:"Name", field:"name"},
                {title:"UID", field:"uid"},
                {title:"Ports", field:"n_ports", width:10 },
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
                {title:"Source UID", field:"source_uid"},
                {title:"Source Port", field:"source_port_id", width:10 },
                {title:"Target UID", field:"target_uid"},
                {title:"Target Port", field:"target_port_id", width:10 },
            ],
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

                link.source = source;
                link.target = target;
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
        console.log("Resized")
        this.svg.attr("width", this.width())
                .attr("height", this.height())
                .attr("viewBox", [0, 0, this.width(), this.height()])
        this.nodesTable.setHeight(this.height());
    }
}

var context;
window.onload = function () {
    context = Object.create(Context)
    context.load();
    window.onresize = function () {
        context.resized();
    }
}
