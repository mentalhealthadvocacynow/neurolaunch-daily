"""Discover NeuroLaunch article URLs from configured feeds or sitemaps."""

import os
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urlunparse

import requests

HOSTS = {"neurolaunch.com", "www.neurolaunch.com"}
USER_AGENT = os.getenv("USER_AGENT", "NeuroLaunchDaily/1.0")


def canonical(url):
    p = urlparse(url.strip())

    if (
        p.scheme != "https"
        or p.hostname not in HOSTS
        or p.username
        or p.password
        or p.port not in (None, 443)
    ):
        raise ValueError("Only HTTPS NeuroLaunch URLs are allowed")

    return urlunparse(
        ("https", "neurolaunch.com", p.path or "/", "", "", "")
    )


def local_name(tag):
    return tag.split("}")[-1]


def child_text(element, name):
    for child in element:
        if local_name(child.tag) == name:
            return (child.text or "").strip()
    return ""


def discover():
    articles = {}
    visited = set()

    def add_article(url, modified=""):
        try:
            url = canonical(url)
        except ValueError:
            return

        path = urlparse(url).path
        excluded = (
            "/category/",
            "/tag/",
            "/author/",
            "/wp-",
        )

        if path == "/" or any(part in path for part in excluded):
            return

        articles[url] = max(articles.get(url, ""), modified)

    def read_document(url, depth=0):
        url = canonical(url)

        if url in visited or depth > 3:
            return

        if len(visited) >= 40:
            raise ValueError("Sitemap document limit reached")

        visited.add(url)

        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=30,
            allow_redirects=False,
        )
        response.raise_for_status()

        if response.is_redirect:
            raise ValueError(
                f"Configure the final sitemap/feed URL: {url}"
            )

        if len(response.content) > 10_000_000:
            raise ValueError("Sitemap/feed is too large")

        root = ET.fromstring(response.content)
        kind = local_name(root.tag)

        if kind == "sitemapindex":
            for entry in root:
                nested_url = child_text(entry, "loc")
                if not nested_url:
                    continue

                # Skip obvious non-article sitemap groups.
                lowered = nested_url.lower()
                if any(
                    word in lowered
                    for word in (
                        "category-sitemap",
                        "post_tag-sitemap",
                        "author-sitemap",
                        "page-sitemap",
                    )
                ):
                    continue

                time.sleep(1)
                read_document(nested_url, depth + 1)

        elif kind == "urlset":
            for entry in root:
                add_article(
                    child_text(entry, "loc"),
                    child_text(entry, "lastmod"),
                )

        else:
            # RSS and Atom support.
            for entry in root.iter():
                if local_name(entry.tag) not in ("item", "entry"):
                    continue

                modified = (
                    child_text(entry, "updated")
                    or child_text(entry, "published")
                )

                for child in entry:
                    if local_name(child.tag) != "link":
                        continue

                    if child.attrib.get("rel", "alternate") != "alternate":
                        continue

                    link = child.attrib.get("href") or child.text
                    if link:
                        add_article(link, modified)

    source = os.getenv(
        "SOURCE_FEED_URL",
        "https://neurolaunch.com/sitemap_index.xml",
    ).strip()

    if source:
        read_document(source)

    # Explicit URLs remain available for manual testing.
    for url in os.getenv("SOURCE_URLS", "").splitlines():
        if url.strip():
            add_article(url)

    # Prefer recently modified articles where dates are available.
    # lastmod is an update date, not necessarily a publication date.
    return sorted(
        articles,
        key=lambda url: articles[url],
        reverse=True,
    )


if __name__ == "__main__":
    print("\n".join(discover()))
