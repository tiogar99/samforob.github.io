import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import escape, unescape
from pathlib import Path

# Paths are relative to the repo root, not this script, so the script works
# the same whether it's run from the repo root (as the workflow does) or here.
ROOT = Path(__file__).resolve().parents[1]
NEWS_JSON_FILE = ROOT / "data" / "news.json"
NEWS_HTML_FILE = ROOT / "news.html"

SEARCH_QUERY = "Sam Holland Oak Bay Mayor"

# news.html is rewritten only between these two markers.
START_MARKER = "<!-- NEWS:START -->"
END_MARKER = "<!-- NEWS:END -->"


def fetch_rss_items(query=SEARCH_QUERY):
    """Fetches article metadata from the Google News RSS feed for `query`."""
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-CA&gl=CA&ceid=CA:en"

    req = urllib.request.Request(
        rss_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        xml_data = response.read().decode("utf-8")

    items = []
    raw_items = re.findall(r"<item>(.*?)</item>", xml_data, re.DOTALL)
    for item in raw_items:
        title_match = re.search(r"<title>(.*?)</title>", item)
        link_match = re.search(r"<link>(.*?)</link>", item)
        pub_date_match = re.search(r"<pubDate>(.*?)</pubDate>", item)

        # The feed is XML, so titles arrive entity-encoded (&amp;, &#39;).
        # Decode them here; build_cards_markup escapes them again for HTML.
        title = unescape(title_match.group(1)) if title_match else ""
        url = unescape(link_match.group(1)) if link_match else ""
        published = pub_date_match.group(1) if pub_date_match else ""

        publisher = "Media"
        if " - " in title:
            title, publisher = title.rsplit(" - ", 1)

        if title and url:
            items.append(
                {
                    "title": title,
                    "url": url,
                    "publisher": publisher,
                    "published": published,
                    "description": f"Recent coverage regarding Sam Holland's campaign for Oak Bay Mayor in {publisher}.",
                    "image": "",
                }
            )

    return items


def display_title(article):
    """Article title without the " - Publisher" suffix page metadata often adds."""
    title = article.get("title", "")
    publisher = article.get("publisher", "")
    if publisher and title.endswith(f" - {publisher}"):
        title = title[: -len(f" - {publisher}")]
    return title


def title_key(article):
    """Normalized title used to spot the same story under different URLs.

    Google News links are redirect URLs, so the same article shows up with a
    different URL than the one in news.json.
    """
    return re.sub(r"[^a-z0-9]+", " ", display_title(article).lower()).strip()


def is_renderable(article):
    """Skips entries whose metadata fetch failed (their title is just the URL)."""
    title = article.get("title", "")
    return bool(title) and not article.get("error") and title != article.get("url")


def merge_articles(existing_articles, new_items):
    """Adds RSS items that aren't already in news.json. Returns the merged list."""
    seen_urls = {a.get("url") for a in existing_articles}
    seen_titles = {title_key(a) for a in existing_articles if is_renderable(a)}

    added = 0
    for item in new_items:
        if item["url"] in seen_urls or title_key(item) in seen_titles:
            continue
        existing_articles.insert(0, item)
        seen_urls.add(item["url"])
        seen_titles.add(title_key(item))
        added += 1

    print(f"Added {added} new article(s) from the RSS feed.")
    return existing_articles


def parse_published(value):
    """Parses RSS (RFC 2822) or ISO 8601 dates. Returns None if unparseable."""
    if not value:
        return None
    for parse in (parsedate_to_datetime, datetime.fromisoformat):
        try:
            parsed = parse(value)
        except (TypeError, ValueError):
            continue
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    return None


def articles_for_display(articles):
    """Drops broken entries and duplicates, then sorts newest first.

    Undated articles keep their news.json order and go after the dated ones.
    """
    unique = []
    seen_titles = set()
    for article in articles:
        if not is_renderable(article):
            continue
        key = title_key(article)
        if key in seen_titles:
            continue
        seen_titles.add(key)
        unique.append(article)

    dated = [a for a in unique if parse_published(a.get("published"))]
    undated = [a for a in unique if not parse_published(a.get("published"))]
    dated.sort(key=lambda a: parse_published(a["published"]), reverse=True)
    return dated + undated


def build_cards_markup(articles):
    """Transforms article dicts into .action-card HTML elements."""
    cards_html = []
    for item in articles:
        title = escape(display_title(item))
        url = escape(item.get("url", "#"))
        publisher = escape(item.get("publisher", ""))
        description = escape(item.get("description", ""))
        image = item.get("image", "")
        published = parse_published(item.get("published"))
        published_date = f"{published:%b} {published.day}, {published.year}" if published else ""

        image_markup = (
            f'<a href="{url}" target="_blank" rel="noopener">'
            f'<img src="{escape(image)}" alt="" class="hero-image" style="aspect-ratio: 16/9; margin-bottom: 1rem;" loading="lazy">'
            f"</a>"
            if image
            else ""
        )

        date_markup = f" &bull; {published_date}" if published_date else ""

        cards_html.append(f"""          <article class="action-card">
            {image_markup}
            <span class="eyebrow">{publisher}{date_markup}</span>
            <h3><a href="{url}" target="_blank" rel="noopener">{title}</a></h3>
            <p>{description}</p>
            <a href="{url}" target="_blank" rel="noopener" class="btn btn-bordeaux btn-sm">
              Read Article <span class="visually-hidden">(opens in a new tab)</span>
            </a>
          </article>""")

    return "\n".join(cards_html)


def update_news_html(cards_markup):
    """Replaces everything between the NEWS:START and NEWS:END markers in news.html."""
    content = NEWS_HTML_FILE.read_text(encoding="utf-8")

    if content.count(START_MARKER) != 1 or content.count(END_MARKER) != 1:
        raise RuntimeError(
            f"{NEWS_HTML_FILE.name} must contain exactly one {START_MARKER} and one {END_MARKER}."
        )

    before, rest = content.split(START_MARKER, 1)
    _, after = rest.split(END_MARKER, 1)

    new_html = f"{before}{START_MARKER}\n{cards_markup}\n          {END_MARKER}{after}"
    NEWS_HTML_FILE.write_text(new_html, encoding="utf-8")
    print(f"Updated {NEWS_HTML_FILE.name}.")


def main():
    with NEWS_JSON_FILE.open("r", encoding="utf-8") as f:
        articles = json.load(f)

    # A feed outage shouldn't fail the run: the page still gets rebuilt from
    # what's already in news.json, and the next scheduled run will retry.
    try:
        new_items = fetch_rss_items()
    except Exception as e:
        print(f"Warning: Could not fetch live news feed ({e}). Skipping RSS update.")
        new_items = []

    articles = merge_articles(articles, new_items)

    with NEWS_JSON_FILE.open("w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"{NEWS_JSON_FILE.name} now holds {len(articles)} article(s).")

    display = articles_for_display(articles)
    update_news_html(build_cards_markup(display))
    print(f"Rendered {len(display)} article card(s).")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Fail loudly so a broken run shows red in Actions instead of green.
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
