from flask import Flask, render_template, request, redirect, url_for, flash
import requests, os, random, datetime, json

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "globalbuzzsecret")

API_KEY = "eb0a2d45fb254a229e0ff2364ec65d15"
NEWS_API_TOP = "https://newsapi.org/v2/top-headlines"
NEWS_API_EVERYTHING = "https://newsapi.org/v2/everything"
CATEGORIES = ["business", "entertainment", "general", "health", "science", "sports", "technology"]

def fetch_news(keyword=None, category=None, page_size=20):
    """Fetch news from NewsAPI with optional keyword or category."""
    endpoint = NEWS_API_TOP
    params = {
        "language": "en",
        "pageSize": page_size,
        "apiKey": API_KEY
    }
    if keyword:
        endpoint = NEWS_API_EVERYTHING
        params.update({"q": keyword, "sortBy": "publishedAt"})
    elif category in CATEGORIES:
        params.update({"category": category})
    try:
        r = requests.get(endpoint, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("articles", [])
    except Exception as e:
        print("NewsAPI error:", e)
        return None  # trigger fallback

# --- Fallback AI generator ---
FAKE_TOPICS = [
    ("Global Tech Breakthrough", "A groundbreaking innovation promises to change the world of {sector}."),
    ("Market Surges", "Stocks rallied today after unexpected news in the {sector} sector."),
    ("Celebrity Headlines", "{name} surprises fans with a brand‑new announcement."),
    ("Sports Upset", "{team} stuns their rivals in a dramatic finish."),
]

SECTORS = ["AI", "renewable energy", "cryptocurrency", "space travel", "biotech"]
NAMES = ["Elon Musk", "Taylor Swift", "Cristiano Ronaldo", "Satoshi Nakamoto"]
TEAMS = ["Dynamo FC", "Thunder Cats", "Rocket Hawks", "Steel Lions"]

def generate_fake_articles(n=10):
    articles = []
    for _ in range(n):
        template_title, template_desc = random.choice(FAKE_TOPICS)
        title = template_title
        desc = template_desc
        # quick substitution
        if "{sector}" in title or "{sector}" in desc:
            sector = random.choice(SECTORS)
            title = title.replace("{sector}", sector)
            desc = desc.replace("{sector}", sector)
        if "{name}" in title or "{name}" in desc:
            name = random.choice(NAMES)
            title = title.replace("{name}", name)
            desc = desc.replace("{name}", name)
        if "{team}" in title or "{team}" in desc:
            team = random.choice(TEAMS)
            title = title.replace("{team}", team)
            desc = desc.replace("{team}", team)
        articles.append({
            "title": title,
            "description": desc,
            "url": "#",
            "urlToImage": "https://source.unsplash.com/random/800x600?news",
            "source": {"name": "GlobalBuzz AI"},
            "publishedAt": datetime.datetime.utcnow().isoformat()
        })
    return articles

@app.route("/", methods=["GET"])
def index():
    keyword = request.args.get("q")
    category = request.args.get("category")
    articles = fetch_news(keyword=keyword, category=category)
    if not articles:
        # fallback
        flash("NewsAPI not reachable – showing AI generated news.", "warning")
        articles = generate_fake_articles()
    return render_template("index.html", articles=articles, current_category=category, keyword=keyword, categories=CATEGORIES)

@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email")
    if email and "@" in email:
        with open("subscribers.txt", "a") as f:
            f.write(email.strip() + "\n")
        flash("Thanks for subscribing!", "success")
    else:
        flash("Please enter a valid email address.", "danger")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)
