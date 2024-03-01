import hashlib

class URLShortener:
    def __init__(self):
        self.url_map = {}
    
    def shorten_url(self,original_url):
        hash_val = hashlib.sha384(original_url.encode('utf-8')).hexdigest()[:6] #SHA384 is used over SHA256 and MD5, because SHA384 provides improved collision resistance
        shortened_url = f"http://localhost:5000/{hash_val}"
        self.url_map[shortened_url] = original_url
        return shortened_url
    
    def expand_url(self, shortened_url):
        return self.url_map.get(shortened_url, "URL not found")


if __name__ == '__main__':
    shortener = URLShortener()

    original_url = "https://www.youtube.com/"
    print(f"Original URL: {original_url}")
    shortened_url = shortener.shorten_url(original_url)
    print(f"Shortened URL: {shortened_url}")

    # Expand a shortened URL
    expanded_url = shortener.expand_url(shortened_url)
    print(f"Expanded URL: {expanded_url}")