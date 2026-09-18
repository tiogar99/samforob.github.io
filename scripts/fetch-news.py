import html
from pathlib import Path

OUTPUT_HTML = Path("news.html")

def generate_html(articles):
    """Generates news.html using existing style.css classes directly."""
    cards_html = []

    for item in articles:
        title = html.escape(item.get("title", ""))
        url = html.escape(item.get("url", "#"))
        publisher = html.escape(item.get("publisher", ""))
        description = html.escape(item.get("description", ""))
        image = item.get("image", "")
        published = html.escape(item.get("published", ""))
        published_date = published[:10] if published else ""

        # Image element using site's border-radius token
        image_markup = (
            f'<a href="{url}" target="_blank" rel="noopener">'
            f'<img src="{html.escape(image)}" alt="" class="hero-image" style="aspect-ratio: 16/9; margin-bottom: 1rem;" loading="lazy">'
            f'</a>'
            if image else ""
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
        </article>
        """)

    full_html = f"""<!DOCTYPE html>
<html lang="en-CA">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>In The News | Sam Holland for Oak Bay Mayor</title>
  <meta name="description" content="Recent media coverage and news articles mentioning Sam Holland's campaign for Mayor of Oak Bay.">
  <link rel="canonical" href="https://samuelholland.ca/news.html">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="theme-color" content="#1A3FC7">

  <link rel="icon" href="/assets/icon.png" type="image/png">
  <link rel="apple-touch-icon" href="/assets/icon.png">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Dela+Gothic+One&family=Simonetta&family=Fugaz+One&display=swap">
  <link rel="stylesheet" href="style.css">
</head>
<body>

  <a href="#main" class="skip-link">Skip to main content</a>

  <main id="main">
    <section class="panel panel--blue tex-rings">
      <div class="container">
        
        <div class="masthead">
          <a href="/" class="logo" aria-label="Sam Holland for Oak Bay Mayor — home">
            <img src="assets/logo-wordmark-horizontal.svg" alt="Sam Holland for Oak Bay Mayor" class="logo-mark" width="600" height="300">
          </a>

          <nav class="main-nav" aria-label="Main">
            <ul>
              <li><a href="/" class="link-highlight">Home</a></li>
              <li><a href="about.html" class="link-highlight">About</a></li>
              <li><a href="platform.html" class="link-highlight">Platform</a></li>
              <li><a href="news.html" class="link-highlight">News</a></li>
              <li><a href="/volunteer.html" class="link-highlight">Get Involved</a></li>
              <li><a href="/lawn.html" class="link-highlight">Request a Sign</a></li>
              <li><a href="/vote.html" class="link-highlight">How to Vote</a></li>
              <li><a href="/#contact" class="link-highlight">Contact</a></li>
            </ul>
          </nav>

          <a href="/donate.html" class="btn btn-outline btn-sm">Donate</a>
        </div>

        <div class="panel-head text-center" style="margin-top: 2rem;">
          <span class="eyebrow">Media & Press</span>
          <h2>In The News</h2>
          <p class="section-intro">Articles and media coverage referencing Sam Holland's campaign for Oak Bay Mayor.</p>
        </div>

      </div>
    </section>

    <section class="panel panel--blue tex-cross">
      <div class="container">
        <div class="action-grid">
          {"".join(cards_html)}
        </div>
      </div>
    </section>
  </main>

  <footer class="site-footer tex-hatch">
    <div class="container text-center">
      <div class="footer-endorsement">
        <h2>Endorsed by the <a href="https://victorialabour.ca/2026-municipal-endorsements/" target="_blank" rel="noopener">Victoria Labour Council</a></h2>
        <img src="assets/VLC_logo.jpg" alt="Victoria Labour Council logo" class="logo-mark" width="600" height="300">
      </div>
      <p>&copy; 2026 Sam Holland for Oak Bay Mayor. All rights reserved.</p>
      <p class="disclaimer">Authorized by Sam Holland.</p>
    </div>
  </footer>

</body>
</html>
"""

    with OUTPUT_HTML.open("w", encoding="utf-8") as file:
        file.write(full_html)
