import hashlib
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
import requests
from bs4 import BeautifulSoup
import trafilatura
from discover import canonical, USER_AGENT


def extract(url):
    url = canonical(url)
    robots_url = urljoin(url, "/robots.txt")
    r = requests.get(robots_url, headers={"User-Agent": USER_AGENT}, timeout=30, allow_redirects=False)
    if r.status_code == 404:
        rules = RobotFileParser(); rules.parse([])
    else:
        r.raise_for_status()
        if r.is_redirect: raise ValueError("Cannot verify robots policy through redirect")
        rules = RobotFileParser(); rules.parse(r.text.splitlines())
    if not rules.can_fetch(USER_AGENT, url): raise ValueError("robots.txt disallows this URL")
    for _ in range(4):
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30, allow_redirects=False)
        if response.is_redirect:
            url = canonical(urljoin(url, response.headers["Location"]))
            if not rules.can_fetch(USER_AGENT, url): raise ValueError("Redirect disallowed by robots.txt")
            continue
        response.raise_for_status()
        break
    else: raise ValueError("Too many redirects")
    if "text/html" not in response.headers.get("Content-Type", ""): raise ValueError("Not HTML")
    if len(response.content)>5_000_000: raise ValueError("Page too large")
    text = trafilatura.extract(response.text, include_comments=False, include_tables=False)
    if not text or len(text)<500: raise ValueError("Insufficient article text")
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.h1.get_text(" ", strip=True) if soup.h1 else (soup.title.get_text(" ", strip=True) if soup.title else url)
    return {"url":url,"title":title,"text":text,"hash":hashlib.sha256(text.encode()).hexdigest()}
