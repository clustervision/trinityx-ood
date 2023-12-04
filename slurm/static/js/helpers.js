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