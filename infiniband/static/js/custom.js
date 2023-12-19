window.onload = function () {
    // Set height and width of graph to the max height and width 
    document.getElementById('graph').style.height = window.innerHeight + 'px';
    document.getElementById('graph').style.width = window.innerWidth + 'px';
    // Make an ajax request to GET /graph
    // When the request is complete, if the request was successful, render the graph
    // in the div with id="graph", otherwise log the error with displayAlert('danger', error)
    var currentUrl = window.location.href;
    var targetUrl = currentUrl + '/graph';
    var xhr = new XMLHttpRequest();
    xhr.open('GET', targetUrl);
    xhr.onload = function () {
        console.log(xhr.responseText);
        if (xhr.status === 200) {

            var graph = cytoscape({

                container: document.getElementById('graph'), // container to render in

                elements: JSON.parse(xhr.responseText),

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
                            "border-opacity": "1",
                            "border-radius": "10px",
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
                            // 'line-color': '#111111',

                        }
                    }
                ],

                layout:  {
                    name: 'cose',
                    nodeDimensionsIncludeLabels: false, // Boolean which changes whether label dimensions are included when calculating node dimensions
                    fit: true, // Whether to fit
                    padding: 10, // Padding on fit
                    animate: false, // Whether to transition the node positions
                    // componentSpacing: 10,
                    nodeRepulsion: 0.1,
                    nodeOverlap: 200,
                    edgeElasticity: 10,
                    initialTemp: 4000,
                    coolingFactor: 0.995,
                    numIter: 5000,
                    // idealEdgeLength: function( edge ){ return 400; },

                  }

            });

        }
        else {
            displayAlert('danger', xhr.responseText);
        }
    };
    xhr.send();

};