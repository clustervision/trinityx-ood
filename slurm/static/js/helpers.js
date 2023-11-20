function _getRequestError(prefix, request) {
    errorString =  prefix;
    // if the responseText is not empty and is valid JSON, concatenate the 'message' field with the responseText
    try {
        responseJSON = JSON.parse(request.responseText);
        if ('message' in responseJSON) {
            message = responseJSON['message'];
            // replace newlines with <br>
            message = message.replace(/\n/g, '<br>');
            errorString = `${errorString}: ${message}`;
        }
    }
    catch (e) {
        // do nothing
    }
    return errorString;
}

function _nodeNamestoNodes(nodeNames) {
    console.log("nodeNames", nodeNames)
    var nodes = {};
    for (let i = 0; i < nodeNames.length; i++) {
        nodes[nodeNames[i]] = configuration['nodes'][nodeNames[i]];
    }
    return nodes;
}