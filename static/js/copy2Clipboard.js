function copyToClipboard(shortUrl) {
    var xpath = "//td[text()='" + shortUrl + "']";
    var matchingElement = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    navigator.clipboard.writeText(matchingElement.innerText)
    .then(function() {
        alertify.success("The link has successfully been copied!");
    })
    .catch(function() {
        alertify.error("An error occurred while copying the link.");
    });
}