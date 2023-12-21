const baseOpacity = 0.3;
const highlightOpacity = 1;
var table;
var link;
var node;

function loadGraph(enpoint, callback) {
    url = `${window.location.href}${enpoint}`;
    d3.json(url).then(function (data) {
        callback(data);
    });
}

function nodeRadius(d) {
    return Math.sqrt(d.ports) + 11;
}

function nodeImage(d) {
    var imageName = (d.type == "S") ? "switch.png" : "host.png";
    var imageUrl = `${window.location.href}/${imageName}`;
    return imageUrl;
}

function wrap(text, width) {
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

function nodeHighlight(d) {
    table.selectRow(d.id);
    node.style('stroke-opacity', o => (o.id == d.id) ? highlightOpacity : baseOpacity);
    node.style('stroke-width', o => (o.id == d.id) ? 3 : 1.5);
    link.style('stroke-opacity', o => (o.source.id == d.id || o.target.id == d.id) ? highlightOpacity : baseOpacity);
    link.style('stroke-width', o => (o.source.id == d.id || o.target.id == d.id) ? Math.sqrt(o.count) + 3 : Math.sqrt(o.count));
}

function nodeHighlightReset() {
    table.deselectRow();
    node.style('stroke-opacity', baseOpacity);
    node.style('stroke-width', 1.5);
    link.style('stroke-opacity', baseOpacity);
    link.style('stroke-width', d => Math.sqrt(d.count));
}

function renderGraph(data) {

    const width = $("#graph").parent().width();
    const height = $("#graph").parent().height();


    // The force simulation mutates links and nodes, so create a copy
    // so that re-evaluating this cell produces the same result.
    const links = data.links.map(d => ({ ...d }));
    const nodes = data.nodes.map(d => ({ ...d }));

    // Create a simulation with several forces.
    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id))
        .force("charge", d3.forceManyBody().strength(-800))
        .force("collide", d3.forceCollide().radius(d => nodeRadius(d) + 30).strength(0.4))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .on("tick", ticked);


    const svg = d3.select("#graph").append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto;")

    // Create a container for the links and nodes. ( Hidden on startup )
    const container = svg.append("g")
                        .attr("class", "container")
                        .attr("style", "display: none;")

    // Add a line for each link, and a circle for each node.
    link = container.append("g")
        .attr("stroke", "#222")
        .attr("stroke-opacity", baseOpacity)
        .selectAll()
        .data(links)
        .join("line")
        .attr("stroke-width", d => Math.sqrt(d.count));

    const node_container = container.append("g")
        .selectAll()
        .data(nodes)
        .join("g")

    node = node_container.append("circle")
        .attr("stroke", "#222")
        .attr("stroke-opacity", baseOpacity)
        .attr("stroke-width", 1.5)
        .attr("fill", d => "#CCC")
        .attr("r", d => nodeRadius(d));

    const img = node_container.append("image")
        .attr("xlink:href", nodeImage)
        .attr("x", d => -nodeRadius(d) * 0.7)
        .attr("y", d => -nodeRadius(d) * 0.7)
        .attr("width", d => nodeRadius(d) * 0.7 * 2)
        .attr("height", d => nodeRadius(d) * 0.7 * 2)

    const label = node_container.append("text")
        .attr("text-anchor", "middle")
        .attr("alignment-baseline", "middle")
        .text(d => d.name.split(" ").join(" "))
        .attr("x", 0)
        .attr("y", d => nodeRadius(d) + 12)
        .attr("dy", 0)
        .call(wrap, 100)


    // invalidation.then(() => simulation.stop());
    function ticked() {
        container.attr("style", "display: block;")

        link.attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node_container.attr("transform", d => `translate(${d.x}, ${d.y})`)
    }

    const zoom = d3.zoom()
        .scaleExtent([0.5, 32])
        .on("zoom", zoomed);

    function zoomed({ transform }) {
        // link.attr("transform", transform);
        // node_container.attr("transform", transform);
        container.attr("transform", transform);
    }
    // Reheat the simulation when drag starts, and fix the subject position.
    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }

    // Update the subject (dragged node) position during drag.
    function dragged(event) {
        console.log(event)
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }

    // Restore the target alpha so the simulation cools after dragging ends.
    // Unfix the subject position now that it’s no longer being dragged.
    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }

    function mouseover(event) {
        d = d3.select(this).datum();
        nodeHighlight(d);

    };

    // Set the stroke width back to normal when mouse leaves the node.
    function mouseout(event) {
        nodeHighlightReset();
    };

    svg.call(zoom).call(zoom.transform, d3.zoomIdentity);
    
    node_container.call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended))

    node_container.on("mouseover", mouseover)
                  .on("mouseout", mouseout);

    //
};

function renderTable(data) {
    table = new Tabulator("#table", {
        data: data.nodes,           //load row data from array
        layout:"fitColumns",      //fit columns to width of table
        pagination:"local",       //paginate the data
        paginationSize:15,         //allow 7 rows per page of data
        paginationButtonCount:4,  // 4 page buttons
        paginationCounter:function(pageSize, currentRow, currentPage, totalRows, totalPages){
            return `Rows ${currentRow} - ${currentRow + pageSize - 1} of ${totalRows}`
        },
        initialSort:[             //set the initial sort order of the data
            {column:"name", dir:"asc"},
        ],
        // selectable:true,
        columns:[                 //define the table columns
            {title:"Name", field:"name"},
            {title:"ID", field:"id"},
        ],
    });
    table.on("rowMouseOver", function(e, row){
        //e - the event object
        //row - row component

        nodeHighlight(row.getData());
    });
    table.on("rowMouseOut", function(e, row){
        //e - the event object
        //row - row component

        nodeHighlightReset();
    });
}

window.onload = function () {
    loadGraph("/graph", renderTable);
    loadGraph("/graph", renderGraph);
}