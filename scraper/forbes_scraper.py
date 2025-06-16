import requests
import json
import os
import re
import trafilatura
from textblob import TextBlob
import textstat
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

SERPAPI_KEY = os.getenv("nH8QWDSrdus1cUW2BnPrAXxR")  #setting up api key.
searchkey = "nH8QWDSrdus1cUW2BnPrAXxR"
HEADERS = {"User-Agent": "Mozilla/5.0"}
ABOUT_PATHS = ["about", "about-us", "company/about", "who-we-are", "our-company"]
#list of company names to look for, along with the sectors.
COMPANIES = [
    {"name": "Apple", "sector": "Technology"},
    {"name": "Amazon", "sector": "Retail"},
    {"name": "ExxonMobil", "sector": "Energy"},
    {"name": "Walmart", "sector": "Retail"},
    {"name": "Toyota", "sector": "Automotive"},
    {"name": "Microsoft", "sector": "Technology"},
    {"name": "Pfizer", "sector": "Healthcare"},
    {"name": "Shell", "sector": "Energy"},
    {"name": "Alphabet", "sector": "Technology"},
    {"name": "Meta", "sector": "Technology"},
    {"name": "JPMorgan Chase", "sector": "Finance"},
    {"name": "Saudi Aramco", "sector": "Energy"},
    {"name": "ICBC", "sector": "Finance"},
    {"name": "China Construction Bank", "sector": "Finance"},
    {"name": "Agricultural Bank of China", "sector": "Finance"},
    {"name": "Bank of America", "sector": "Finance"},
    {"name": "Chevron", "sector": "Energy"},
    {"name": "Samsung Electronics", "sector": "Technology"},
    {"name": "UnitedHealth Group", "sector": "Healthcare"},
    {"name": "Ping An Insurance", "sector": "Insurance"},
    {"name": "Wells Fargo", "sector": "Finance"},
    {"name": "PetroChina", "sector": "Energy"},
    {"name": "HSBC", "sector": "Finance"},
    {"name": "TotalEnergies", "sector": "Energy"},
    {"name": "Verizon", "sector": "Telecom"},
    {"name": "Citigroup", "sector": "Finance"},
    {"name": "China Mobile", "sector": "Telecom"},
    {"name": "China Merchants Bank", "sector": "Finance"},
    {"name": "BP", "sector": "Energy"},
    {"name": "Volkswagen", "sector": "Automotive"},
    {"name": "Morgan Stanley", "sector": "Finance"},
    {"name": "Allianz", "sector": "Insurance"},
    {"name": "Royal Bank of Canada", "sector": "Finance"},
    {"name": "Johnson & Johnson", "sector": "Healthcare"},
    {"name": "Deutsche Telekom", "sector": "Telecom"},
    {"name": "Mercedes-Benz Group", "sector": "Automotive"},
    {"name": "TD Bank", "sector": "Finance"},
    {"name": "TSMC", "sector": "Semiconductors"},
    {"name": "Reliance Industries", "sector": "Conglomerate"},
    {"name": "BMW Group", "sector": "Automotive"},
    {"name": "LVMH", "sector": "Luxury Goods"},
    {"name": "AXA", "sector": "Insurance"},
    {"name": "Banco Santander", "sector": "Finance"},
    {"name": "Nestlé", "sector": "Food & Beverage"},
    {"name": "Goldman Sachs", "sector": "Finance"},
    {"name": "BNP Paribas", "sector": "Finance"},
    {"name": "Tencent", "sector": "Technology"},
    {"name": "Oracle", "sector": "Technology"},
    {"name": "PepsiCo", "sector": "Food & Beverage"},
    {"name": "AbbVie", "sector": "Pharmaceuticals"},
]

# defining the function to get the official website of a company using SERPAPI.
def get_website(name):
    try:
        params = {
            'engine': 'google',        # search engine
            'q': f"{name} official site",     # your search query
            'location': 'Austin, Texas, United States',  # optional location
            'hl': 'en',                # language
            'gl': 'us',                # country
            'api_key': searchkey         # API Key
        }
        r = requests.get("https://searchapi.io/api/v1/search", params)

        if r.status_code == 200:
            return r.json()["organic_results"][0]["link"]
        else:
            print("Error:", r.status_code, r.text)
        
    except:
        return None

# defining the function to find the about page URL of a company.
def find_about_url(base_url):
    for path in ABOUT_PATHS:
        url = urljoin(base_url + "/", path)
        try:
            r = requests.get(url, headers=HEADERS, timeout=5)
            if r.ok and 'html' in r.headers.get("Content-Type", ""):
                return url
        except:
            continue
    return None

# cleaning and analyzing the text extracted from the about page.
def clean_text(text):
    words = re.findall(r'\b\w+\b', text.lower())
    return [w for w in words if len(w) > 2]

def analyze(text):
    tokens = clean_text(text)
    blob = TextBlob(text)
    return {
        "keywords": Counter(tokens).most_common(15),
        "sentiment_polarity": blob.sentiment.polarity,
        "sentiment_subjectivity": blob.sentiment.subjectivity,
        "readability": {
            "flesch_reading_ease": textstat.flesch_reading_ease(text),
            "smog_index": textstat.smog_index(text),
            "gunning_fog": textstat.gunning_fog(text)
        }
    }

# Main function to process each company.
def process_company(c):
    homepage = get_website(c["name"])
    if not homepage: return None
    about = find_about_url(homepage)
    if not about: return None
    extracted = trafilatura.extract(trafilatura.fetch_url(about))
    if not extracted or len(extracted) < 100: return None
    return {
        "name": c["name"],
        "sector": c["sector"],
        "base_url": homepage,
        "about_url": about,
        "text": extracted,
        "nlp": analyze(extracted)
    }

# run and scrape all companies.
def scrape_all():
    results = []
    with ThreadPoolExecutor(max_workers=1) as pool:
        for res in pool.map(process_company, COMPANIES):
            if res:
                print(f"✓ {res['name']}")
                results.append(res)
    with open("about_pages_nlp.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    scrape_all()
