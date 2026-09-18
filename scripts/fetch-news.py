import json
import re
import urllib.parse
import urllib.request
from html import escape
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
NEWS_JSON_FILE = SCRIPT_DIR / "news.json"
NEWS_HTML_FILE = SCRIPT_DIR / "news.html"

# Default RSS/Search API Query for media coverage
SEARCH_QUERY = "Sam Holland Oak Bay Mayor"


# --- STEP 1: FETCH METADATA & UPDATE NEWS.JSON ---
def fetch_latest_news_metadata(query=SEARCH_QUERY):
    """Fetches news metadata via Google News RSS feed and updates news.json."""
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-CA&gl=CA&ceid=CA:en"

    # Minimal XML parsing without extra dependencies
    req = urllib.request.Request(
        rss_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )

    items = []
    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read().decode("utf-8")

        # Parse <item> tags out of RSS XML
        raw_items = re.findall(r"<item>(.*?)</item>", xml_data, re.DOTALL)
        for item in raw_items:
            title_match = re.search(r"<title>(.*?)</title>", item)
            link_match = re.search(r"<link>(.*?)</link>", item)
            pub_date_match = re.search(r"<pubDate>(.*?)</pubDate>", item)

            title = title_match.group(1) if title_match else ""
            url = link_match.group(1) if link_match else ""
            published = pub_date_match.group(1) if pub_date_match else ""

            # Extract publisher from Google News title format "Title - Publisher"
            publisher = "Media"
            if " - " in title:
                parts = title.rsplit(" - ", 1)
                title = parts[0]
                publisher = parts[1]

            if title and url:
                items.append(
                    {
                        "title": title,
                        "url": url,
                        "publisher": publisher,
                        "published": published,
                        "description": f"Recent coverage regarding Sam Holland's campaign for Oak Bay Mayor in {publisher}.",
                        "image": "",  # Optional thumbnail relative path
                    }
                )
    except Exception as e:
        print(f"Warning: Could not fetch live news feed ({e}). Skipping RSS update.")

    # Load existing JSON if available to prevent wiping manually curated articles
    existing_articles = []
    if NEWS_JSON_FILE.exists():
        try:
            with NEWS_JSON_FILE.open("r", encoding="utf-8") as f:
                existing_articles = json.load(f)
        except json.JSONDecodeError:
            existing_articles = []

    # Merge unique articles by URL
    seen_urls = {a.get("url") for a in existing_articles if "url" in a}
    for item in items:
        if item["url"] not in seen_urls:
            existing_articles.insert(0, item)
            seen_urls.add(item["url"])

    # Write updated payload back to news.json
    with NEWS_JSON_FILE.open("w", encoding="utf-8") as f:
        json.dump(existing_articles, f, indent=2, ensure_ascii=False)

    print(f"Updated metadata in {NEWS_JSON_FILE.name} ({len(existing_articles)} total articles)")
    return existing_articles


# --- STEP 2: BUILD CARD HTML ---
def build_cards_markup(articles):
    """Transforms article dicts into .action-card HTML elements."""
    cards_html = []
    for item in articles:
        title = escape(item.get("title", ""))
        url = escape(item.get("url", "#"))
        publisher = escape(item.get("publisher", ""))
        description = escape(item.get("description", ""))
        image = item.get("image", "")
        published = escape(item.get("published", ""))
        published_date = published[:16] if published else ""

        image_markup = (
            f'<a href="{url}" target="_blank" rel="noopener">'
            f'<img src="{escape(image)}" alt="" class="hero-image" style="aspect-ratio: 16/9; margin-bottom: 1rem;" loading="lazy">'
            f"</a>"
            if image
            else ""
        )

        date_markup = f" &bull; {published_date}" if published_date else ""

        cards_html.append(f"""
        <article class="action-card">
          {image_markup}
          <span class="eyebrow">{publisher}{date_markup}</span>
          <h3><a href="{url}" target="_blank" rel="noopener">{title}</a></h3>
          <p>{description}</p>
          <a href="{url}" target="_blank" rel="noopener" class="btn btn-bordeaux btn-sm">
            Read Article <span class="visually-hidden">(opens in a new tab)</span>
          </a>
        </article>""")

    return "\n".join(cards_html)


# --- STEP 3: SURGICALLY UPDATE NEWS.HTML ---
def update_news_html_target(cards_markup):
    """Replaces ONLY the inner content of <div class="action-grid"> inside news.html."""
    if not NEWS_HTML_FILE.exists():
        print(f"Error: {NEWS_HTML_FILE.name} not found.")
        return

    content = NEWS_HTML_FILE.read_text(encoding="utf-8")

    # Regex targeting content between <div class="action-grid"> and its matching </div>
    pattern = r'(<div\s+class=["\']action-grid["\']>)(.*?)(</div>\s*</div>\s*</section>)'

    replacement = f"\\1\n{cards_markup}\n        \\3"

    new_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)

    if count == 0:
        print(
            "Target marker `<div class=\"action-grid\">` was not found in news.html. "
            "Ensure the HTML contains <div class=\"action-grid\"></div>."
        )
        return

    NEWS_HTML_FILE.write_text(new_content, encoding="utf-8")
    print(f"Surgically updated bottom section in {NEWS_HTML_FILE.name} without altering header or footer.")


# --- EXECUTION ---
if __name__ == "__main__":
    articles = fetch_latest_news_metadata()
    cards_html = build_cards_markup(articles)
    update_news_html_target(cards_html)
