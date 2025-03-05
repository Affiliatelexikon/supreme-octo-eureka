from flask import Flask, render_template, request, redirect, url_for
import openai
import tweepy
import smtplib
import requests
import json
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
import schedule
import time

app = Flask(__name__)

# Temporärer Speicher für Zugangsdaten & mehrere Accounts
config = {
    "openai_api_key": "",
    "wp_url": "",
    "wp_username": "",
    "wp_password": "",
    "smtp_server": "",
    "email_address": "",
    "email_password": "",
    "affiliate_links": [],  # Liste für Affiliate-Links
    "google_trends_api_key": "",
    "ad_budget": "",  # Budget für bezahlte Werbung
    "social_media_accounts": {
        "twitter": [],
        "facebook": [],
        "instagram": [],
        "pinterest": [],
        "tiktok": [],
        "youtube": []
    }
}

@app.route('/')
def home():
    return render_template('index.html', config=config)

@app.route('/save_config', methods=['POST'])
def save_config():
    for key in config.keys():
        if key == "social_media_accounts":
            for platform in config["social_media_accounts"].keys():
                accounts = request.form.getlist(platform + "_accounts")
                config["social_media_accounts"][platform] = accounts
        elif key == "affiliate_links":
            affiliate_links = request.form.get("affiliate_links", "")
            config["affiliate_links"] = [link.strip() for link in affiliate_links.split(",") if link.strip()]
        else:
            config[key] = request.form.get(key, '')
    return redirect(url_for('home'))

# Google Trends: Aktuelle Themen abrufen
def get_trending_topics():
    url = "https://trends.google.com/trends/api/dailytrends?hl=en-US&tz=-240&geo=US"
    response = requests.get(url)
    if response.status_code == 200:
        trends_data = json.loads(response.text[5:])  # Google Trends API gibt JSON mit Präfix zurück
        trending_topics = [trend['title'] for trend in trends_data['default']['trendingSearchesDays'][0]['trendingSearches']]
        return trending_topics[:5]  # Top 5 Trends
    return []

# OpenAI: Nischen- & Produktauswahl basierend auf Trends
def find_profitable_niche():
    openai.api_key = config["openai_api_key"]
    trending_topics = get_trending_topics()
    if trending_topics:
        prompt = f"Finde eine profitable Affiliate-Nische basierend auf diesen aktuellen Trends: {', '.join(trending_topics)}"
    else:
        prompt = "Finde eine profitable Affiliate-Nische."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# Automatische Werbe-Strategie mit KI
def create_ad_campaign(platform, content):
    budget = config.get("ad_budget", "0")
    print(f"Erstelle Werbekampagne auf {platform} mit Budget {budget} EUR: {content}")
    # Hier könnte eine API-Integration für Facebook Ads, Google Ads oder TikTok Ads erfolgen

# Automatisierte Hauptfunktion
def run_automation():
    niche = find_profitable_niche()
    blog_content = f"Hier ist ein neuer Blogpost über {niche}."  # KI-generierter Inhalt
    print(f"Automatisch generierter Content: {blog_content}")
    for platform in config["social_media_accounts"].keys():
        print(f"Poste auf {platform}: {blog_content}")
    print("Automatisierung abgeschlossen.")

# Automatische Planung mit Schedule
schedule.every().day.at("08:00").do(run_automation)

def scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    import threading
    threading.Thread(target=scheduler).start()
    app.run(debug=True)
