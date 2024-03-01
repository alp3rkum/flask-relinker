import pyshorteners

def shorten_url(long_url):
    shortener = pyshorteners.Shortener().tinyurl
    output = shortener.short(long_url)
    return output