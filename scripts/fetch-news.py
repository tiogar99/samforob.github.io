import json
import re
import urllib.parse
import urllib.request
from html import escape
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
NEWS_JSON_FILE = SCRIPT_DIR / "news.json"
NEWS_HTML_FILE = SCRIPT_DIR / "news.html"

SEARCH_QUERY = "Sam Holland Oak Bay Mayor"


def fetch_latest_news_metadata(query=SEARCH_QUERY):
    """Fetches news metadata via Google News RSS feed and updates news.json."""
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-CA&gl=CA&ceid=CA:en"

    items = []
    try:
        req = urllib.request.Request(
            rss_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req) as response:
            xml_data = response.read().decode("utf-8")

        raw_items = re.findall(r"<item>(.*?)</item>", xml_data, re.DOTALL)
        for item in raw_items:
            title_match = re.search(r"<title>(.*?)</title>", item)
            link_match = re.search(r"<link>(.*?)</link>", item)
            pub_date_match = re.search(r"<pubDate>(.*?)</pubDate>", item)

            title = title_match.group(1) if title_match else ""
            url = link_match.group(1) if link_match else ""
            published = pub_date_match.group(1) if pub_date_match else ""

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
                        "image": "",
                    }
                )
    except Exception as e:
        print(f"Warning: Could not fetch live news feed ({e}). Skipping RSS update.")

    existing_articles = []
    if NEWS_JSON_FILE.exists():
        try:
            with NEWS_JSON_FILE.open("r", encoding="utf-8") as f:
                existing_articles = json.load(f)
        except json.JSONDecodeError:
            existing_articles = []

    seen_urls = {a.get("url") for a in existing_articles if "url" in a}
    for item in items:
        if item["url"] not in seen_urls:
            existing_articles.insert(0, item)
            seen_urls.add(item["url"])

    with NEWS_JSON_FILE.open("w", encoding="utf-8") as f:
        json.dump(existing_articles, f, indent=2, ensure_ascii=False)

    print(f"Updated {NEWS_JSON_FILE.name} with {len(existing_articles)} article(s).")
    return existing_articles


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


def update_news_html_target(cards_markup):
    """Splits news.html around <div class="action-grid"> and injects new cards."""
    if not NEWS_HTML_FILE.exists():
        print(f"Error: {NEWS_HTML_FILE.name} not found in script directory.")
        return

    content = NEWS_HTML_FILE.read_text(encoding="utf-8")

    grid_marker = '<div class="action-grid">'
    if grid_marker not in content:
        print('Error: Could not find `<div class="action-grid">` inside news.html.')
        return

    # Split into part before <div class="action-grid"> and part after
    before_grid, after_grid_start = content.split(grid_marker, 1)

    # Find the closing </div> of action-grid
    close_div_index = after_grid_start.find("</div>")
    if close_div_index == -1:
        print("Error: Could not find matching </div> for action-grid.")
        return

    remainder = after_grid_start[close_div_index:]

    # Reassemble news.html
    new_html = f"{before_grid}{grid_marker}\n{cards_markup}\n        {remainder}"

    NEWS_HTML_FILE.write_text(new_html, encoding="utf-8")
    print(f"Successfully updated {NEWS_HTML_FILE.name}!")


if __name__ == "__main__":
    articles = fetch_latest_news_metadata()
    cards_html = build_cards_markup(articles)
    update_news_html_target(cards_html)
