function nodeRadius(n) {
    var baseRadius = Math.sqrt(n.ports);
    if (n.type == "S") {
        return baseRadius + 16;
    } else {
        return baseRadius + 11;
    }
}
function nodeImage(n) {
    var imageName = (n.type == "S") ? "switch.png" : "host.png";
    var imageUrl = `${window.location.href}/assets/${imageName}`;
    return imageUrl;
}
function nodeText(n) {
    if ((n.type == "S") && (n.name == 'SwitchIB Mellanox Technologies')) {
        return Array.prototype.concat('SwitchIB', n.uid).join(" ");
    } else {
        return n.name;
    }
}
function nodeStrokeWidth(highlighted) {
    return (highlighted) ? 3 : 1.5;
}
function linkStrokeWidth(l, highlighted) {
    return (highlighted) ? l.count + 3 : l.count + 1;
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
    table: null,

    width() {
        return $("#graph").parent().width();
    },
    height() {
        return $("#graph").parent().height();
    },
    links() {
        return this.data.links;
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
    setSimulationType(type) {
        $("#simulation-type").val(type);
        this.onchangeSimulationType();
    },
    getSimulationType() {
        return $("#simulation-type").val();
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
                .force("link", d3.forceLink(this.links()).id(d => d.id))
                .force("charge", d3.forceManyBody().strength( -600 ))
                .force("collide", d3.forceCollide().radius(d => nodeRadius(d) + 30).strength(0.4))
                .force("center", d3.forceCenter(this.width() / 2, this.height() / 2))
                .on("tick", () => this.ticked());
        } else if (simulationType == 'compute') {
            return  d3.forceSimulation(this.nodes())
                .force("link", d3.forceLink(this.links()).id(d => d.id))
                .force("charge", d3.forceManyBody().strength( -600 ))
                .force("collide", d3.forceCollide().radius(d => nodeRadius(d) + 30).strength(0.4))
                // .force("center", d3.forceCenter(this.width() / 2, this.height() / 2))
                .on("tick", () => this.ticked());
        } else if (simulationType == 'none') {
            return  d3.forceSimulation(this.nodes())
                    .force("collide", d3.forceCollide().radius(d => nodeRadius(d) + 30).strength(0.4))
                    .on("tick", () => this.ticked());
        }

    },
    nodeselected(uid) {
        this.nodeItems.style('stroke-opacity', on => strokeOpacity(on.id == uid));
        this.nodeItems.style('stroke-width', on =>  nodeStrokeWidth(on.id == uid));
        this.linkItems.style('stroke-opacity', l => strokeOpacity(l.source.id == uid || l.target.id == uid));
        this.linkItems.style('stroke-width', l => linkStrokeWidth(l,(l.source.id == uid || l.target.id == uid)));
    },
    linkselected(source_uid, target_uid) {
        this.nodeItems.style('stroke-opacity', n => strokeOpacity(n.id == source_uid || n.id == target_uid));
        this.nodeItems.style('stroke-width', n =>  nodeStrokeWidth(n.id == source_uid || n.id == target_uid));
        this.linkItems.style('stroke-opacity', ol => strokeOpacity((source_uid == ol.source.id && target_uid == ol.target.id) || (source_uid == ol.target.id && target_uid == ol.source.id)));
        this.linkItems.style('stroke-width', ol => linkStrokeWidth(ol,((source_uid == ol.source.id && target_uid == ol.target.id) || (source_uid == ol.target.id && target_uid == ol.source.id))));        
    },

    unselected() {
        this.table.deselectRow();
        this.nodeItems.style('stroke-opacity', strokeOpacity(false));
        this.nodeItems.style('stroke-width', nodeStrokeWidth(false));
        this.linkItems.style('stroke-opacity', strokeOpacity(false));
        this.linkItems.style('stroke-width', l => linkStrokeWidth(l,false));
    },
    dragstarted(event) {

        if (this.getSimulationType() == 'all'){
            this.setSimulationType('compute');
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
        $("#container .row").height(canvasHeight);

        // Register the event handler for the simulation type
        $("#simulation-type").change(() => this.onchangeSimulationType());



    },
    async _graphInitialized() {
        this.svg = d3.select("#graph").append("svg")
            .attr("width", this.width())
            .attr("height", this.height())
            .attr("viewBox", [0, 0, this.width(), this.height()])
            .attr("style", "max-width: 100%; height: auto;")

        this.containerItem = this.svg.append("g")
            .attr("class", "container")
            .attr("style", "display: none;")

        this.linkItems = this.containerItem.append("g")
            .attr("stroke", "#222")
            .attr("stroke-opacity", strokeOpacity(false))
            .selectAll()
            .data(this.links())
            .join("line")
            .attr("stroke-width", l => linkStrokeWidth(l, false))

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
        



        this.zoomItem = d3.zoom().scaleExtent([0.5, 32])
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
            this.table.scrollToRow(n.id, "center", false);
            this.table.selectRow(n.id);
            this.nodeselected(n.id);
        });
        this.nodeContainerItems.on("mouseout", (e) => {
            this.unselected();
        });



        if (this.data.state){
            this.nodes().forEach((d) => {
                var nodePosition = this.data.state.nodePositions.find(n => n.id == d.id);
                if (nodePosition) {
                    d.x = nodePosition.x;
                    d.y = nodePosition.y;
                }
            });
            this.setSimulationType(this.data.state.simulationType);
            this.fitzoom();
        } else {
            this._simulation = this.simulation()
        }

    },
    async _tableInitialized() {
        this.table = new Tabulator("#table", {
            data: this.data.nodes,           //load row data from array
            layout:"fitData",
            height:this.height(),
            columns:[                        //define the table columns
                // {formatter:"rownum", hozAlign:"center", width:65},
                {title:"Name", field:"name"},
                {title:"UID", field:"uid"},
                {title:"Port", field:"port_id"},
                {title:"Target Name", field:"target_name"},
                {title:"Target Port", field:"target_port_id"},
                {title:"Target UID", field:"target_uid"},
                
            ],
            dataTree:true,
        });

        this.table.on("rowMouseOver", (e, row) =>{
            var data = row.getData();

            if (data.target_name != undefined) { 
                this.linkselected(data.uid, data.target_uid);
            } else {
                this.nodeselected(data.uid);
            }
        });

        this.table.on("rowMouseOut", () => {
            this.unselected()
        });
    },
    async _menuInitialized() {
        $('#n-switches').val(this.switchNodes().length);
        $('#n-computes').val(this.computeNodes().length);
        $('#n-links').val(this.links().length);

        $('#save-graph').click(() => this.saved());
    },
    initialized() {
        this._containerInitialized();
        this._tableInitialized();
        this._graphInitialized();
        this._menuInitialized();
    },
    loaded(endpoint) {
        // Get the current url without any trailing slash
        var currentUrl = window.location.href.replace(/\/$/, "");
        var url = `${currentUrl}${endpoint}`;
        var successCallback = (data) => {
            data.nodes.forEach((d) => {
                d._children = [];
            });
            data.extlinks.forEach((l) => {
                var source = data.nodes.find(n => n.uid == l.uid);
                source._children.push(l);
            });
            console.log(data)
            this.data = data
            this.initialized()
        }
        var failureCallback = (error) => {
            displayAlert("danger", error)
        }

        d3.json(url).then( successCallback, failureCallback);
    },
    ticked() {
        this.containerItem.attr("style", "display: block;");
        this.linkItems.attr("x1", d => d.source.x)
                      .attr("y1", d => d.source.y)
                      .attr("x2", d => d.target.x)
                      .attr("y2", d => d.target.y);

        this.nodeContainerItems.attr("transform", d => `translate(${d.x}, ${d.y})`)
    },
    saved() {
        var url = `${window.location.href}/graph/state/save`;
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
        var state = {
            simulationType: this.getSimulationType(),
            nodePositions: this.nodes().map(d => { return {id: d.id, x: d.x, y: d.y} })
        }
        return state;
    },
    fitzoom() {
        var minX = d3.min(this.nodes(), d => d.x);
        var maxX = d3.max(this.nodes(), d => d.x);
        var minY = d3.min(this.nodes(), d => d.y);
        var maxY = d3.max(this.nodes(), d => d.y);
        var midX = (minX + maxX) / 2;
        var midY = (minY + maxY) / 2;

        var width = maxX - minX;
        var height = maxY - minY;
        var scale = 0.9 / Math.max(width / this.width(), height / this.height());
        var translateX = this.width() / 2 - scale * midX;
        var translateY = this.height() / 2 - scale * midY;

        this.svg.call(this.zoomItem.transform, d3.zoomIdentity.translate(translateX, translateY).scale(scale));
        
    }
    
}

var context;
window.onload = function () {
    context = Object.create(Context)
    context.loaded("/graph/get");
}