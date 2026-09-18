#!/usr/bin/env python3

import html
import json
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]

SOURCE_FILE = ROOT / "data" / "news-sources.json"
OUTPUT_FILE = ROOT / "data" / "news.json"

USER_AGENT = (
    "Mozilla/5.0 (compatible; CampaignNewsMetadata/1.0; "
    "+https://samforob.github.io/)"
)

TIMEOUT = 15
MAX_BYTES = 2_000_000


class MetadataParser(HTMLParser):
    """Extract useful metadata from an article's <head>."""

    def __init__(self):
        super().__init__(convert_charrefs=True)

        self.meta = {}
        self.title = ""
        self.canonical = ""

        self.in_title = False
        self.title_parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag.lower() == "title":
            self.in_title = True
            return

        if tag.lower() == "meta":
            property_name = attrs.get("property", "").lower()
            name = attrs.get("name", "").lower()
            content = attrs.get("content", "")

            if content:
                if property_name:
                    self.meta[property_name] = content.strip()

                if name:
                    self.meta[name] = content.strip()

        elif tag.lower() == "link":
            rel = attrs.get("rel", "").lower()

            if "canonical" in rel and attrs.get("href"):
                self.canonical = attrs["href"].strip()

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.in_title = False
            self.title = " ".join(self.title_parts).strip()

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)


def clean(value):
    if not value:
        return ""

    return html.unescape(" ".join(value.split())).strip()


def fetch_page(url):
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
        },
    )

    with urlopen(request, timeout=TIMEOUT) as response:
        final_url = response.geturl()
        content_type = response.headers.get("Content-Type", "")

        if "text/html" not in content_type.lower():
            raise ValueError(
                f"URL did not return HTML ({content_type})"
            )

        body = response.read(MAX_BYTES)

    encoding = "utf-8"

    # Most modern pages are UTF-8. This fallback handles common
    # legacy pages that explicitly declare another charset.
    charset = response.headers.get_content_charset()

    if charset:
        encoding = charset

    return (
        final_url,
        body.decode(encoding, errors="replace"),
    )


def get_metadata(source_url):
    final_url, page = fetch_page(source_url)

    parser = MetadataParser()
    parser.feed(page)

    parsed = urlparse(final_url)
    domain = parsed.netloc.lower().removeprefix("www.")

    meta = parser.meta

    article_url = (
        urljoin(final_url, parser.canonical)
        if parser.canonical
        else final_url
    )

    title = clean(
        meta.get("og:title")
        or meta.get("twitter:title")
        or parser.title
        or final_url
    )

    description = clean(
        meta.get("og:description")
        or meta.get("twitter:description")
        or meta.get("description")
    )

    image = (
        meta.get("og:image")
        or meta.get("twitter:image")
        or ""
    )

    if image:
        image = urljoin(final_url, image)

    publisher = clean(
        meta.get("og:site_name")
        or meta.get("application-name")
        or domain
    )

    published = clean(
        meta.get("article:published_time")
        or meta.get("date")
        or meta.get("pubdate")
        or meta.get("datepublished")
    )

    return {
        "url": article_url,
        "title": title,
        "description": description,
        "image": image,
        "publisher": publisher,
        "published": published,
        "domain": domain,
        "fetched": datetime.now(timezone.utc).isoformat(),
    }


def main():
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Missing source file: {SOURCE_FILE}"
        )

    with SOURCE_FILE.open("r", encoding="utf-8") as file:
        sources = json.load(file)

    if not isinstance(sources, list):
        raise ValueError(
            "news-sources.json must contain a JSON array."
        )

    results = []

    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict) or not source.get("url"):
            print(f"Skipping invalid entry #{index}")
            continue

        source_url = source["url"].strip()

        parsed = urlparse(source_url)

        if parsed.scheme not in ("http", "https"):
            print(f"Skipping non-web URL: {source_url}")
            continue

        print(f"[{index}/{len(sources)}] Fetching {source_url}")

        try:
            article = get_metadata(source_url)
            results.append(article)

        except Exception as error:
            print(f"  WARNING: {error}")

            results.append({
                "url": source_url,
                "title": source_url,
                "description": "",
                "image": "",
                "publisher": urlparse(source_url).netloc,
                "published": "",
                "domain": urlparse(source_url).netloc,
                "fetched": datetime.now(timezone.utc).isoformat(),
                "error": str(error),
            })

        # Be polite to publishers and avoid hammering sites.
        time.sleep(1)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
        )
        file.write("\n")

    print(f"\nWrote {len(results)} articles to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()