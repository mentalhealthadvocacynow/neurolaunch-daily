"""Discover configured, permission-approved source URLs; no endpoint guessing."""
import os
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urlunparse
import requests

HOSTS = {"neurolaunch.com", "www.neurolaunch.com"}
USER_AGENT = os.getenv("USER_AGENT", "NeuroLaunchDaily/1.0")

def canonical(url):
    p = urlparse(url.strip())
    if p.scheme != "https" or p.hostname not in HOSTS or p.username or p.password or p.port not in (None,443):
        raise ValueError("Only HTTPS NeuroLaunch source URLs are allowed")
    return urlunparse(("https", "neurolaunch.com", p.path or "/", "", "", ""))

def discover():
    explicit = [canonical(u) for u in os.getenv("SOURCE_URLS", "").splitlines() if u.strip()]
    feed = os.getenv("SOURCE_FEED_URL", "").strip()
    if feed:
        r = requests.get(canonical(feed), headers={"User-Agent": USER_AGENT}, timeout=30, allow_redirects=False)
        r.raise_for_status()
        if r.is_redirect: raise ValueError("Configure the final feed URL, not a redirect")
        if len(r.content)>5_000_000: raise ValueError("Feed too large")
        tree = ET.fromstring(r.content)
        for el in tree.iter():
            tag = el.tag.split("}")[-1]
            candidate = el.attrib.get("href") if tag == "link" else None
            if tag in ("link", "loc") and (candidate or el.text):
                try: explicit.append(canonical(candidate or el.text))
                except ValueError: pass
    return list(dict.fromkeys(explicit))[:100]

if __name__ == "__main__":
    print("\n".join(discover()))
