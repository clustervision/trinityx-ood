var layouts = {
    'force': {
        name: 'cose',
        nodeOverlap: 100,

    },
    'hierarchical': {
        name: 'breadthfirst',
        directed: false,
        roots: undefined,
        circle: false,
        spacingFactor: 1,
    },
    'concentric': {
        name: 'breadthfirst',
        directed: false,
        roots: undefined,
        circle: true,
        spacingFactor: 3,
    },
    // 'concentric': {
    //     name: 'concentric',
    //     concentric: function( node ){ // returns numeric value for each node, placing higher nodes in levels towards the centre
    //         return node._private.data.rank;
    //         },
    //     levelWidth: function( nodes ){ // the variation of concentric values in each level
    //         return 1;
    //         }
    // },
}
var graph;
var data;

function handleLayoutChange(event) {
    var layoutName = event.target.value;
    var layout = graph.layout(layouts[layoutName]);
    layout.run()

}

window.onload = function () {
    // Set height and width of graph to the max height and width 
    document.getElementById('graph').style.height = window.innerHeight + 'px';
    document.getElementById('graph').style.width = window.innerWidth + 'px';

    $(".layout-button").click(handleLayoutChange);
    // Make an ajax request to GET /graph
    // When the request is complete, if the request was successful, render the graph
    // in the div with id="graph", otherwise log the error with displayAlert('danger', error)
    var currentUrl = window.location.href;
    var targetUrl = currentUrl + '/graph';
    var xhr = new XMLHttpRequest();
    xhr.open('GET', targetUrl);
    xhr.onload = function () {
        
        if (xhr.status === 200) {
            data = JSON.parse(xhr.responseText);
            var roots = (
                data.map(function (x) { 
                    if (x.data.rank == 3){
                        return x.data.id;
                    }}).filter(function (x) { return x != undefined; })
             );
            layouts['hierarchical']['roots'] = roots;
            layouts['concentric']['roots'] = roots;
            graph = cytoscape({
                container: document.getElementById('graph'), // container to render in
                elements: data,
                style: [ // the stylesheet for the graph
                    {
                        selector: 'node',
                        style: {
                            'width': 220,
                            'height': 100,
                            'background-color': '#ddd',
                            'shape': 'rectangle',
                            'text-wrap': 'wrap',
                            'content': 'data(desc)',
                            "text-valign": "center",
                            "text-justification": "left",
                            "text-max-width": 200,
                            "border-width": "3px",
                            "border-color": "#000",
                        }
                    },
                    {
                        selector: '.switch',
                        style: {
                            'height': 160,
                            'background-color': '#00ff00',

                        }
                    },

                    {
                        selector: 'edge',
                        style: {
                            'width': 'data(width)',
                            'curve-style': 'bezier',

                        }
                    }
                ],
                layout:  layouts['force'],
            });
        } else {
            displayAlert('danger', xhr.responseText);
        }
    };
    xhr.send();

};