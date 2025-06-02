# scraper.py

import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

INDEX_FILE = "index.json"

def load_index():
    if not os.path.exists(INDEX_FILE):
        return {"links": set(), "images": set()}
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {
        "links": set(data.get("links", [])),
        "images": set(data.get("images", []))
    }

def save_index(index_data):
    serializable = {
        "links": sorted(list(index_data["links"])),
        "images": sorted(list(index_data["images"]))
    }
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(serializable, f, indent=2)
    print(f"Index saved to {INDEX_FILE}.")

def fetch_html(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"[!] Error fetching {url}: {e}")
        return None

def extract_links_and_images(soup, base_url):
    links = set()
    images = set()

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        abs_link = urljoin(base_url, href)
        parsed = urlparse(abs_link)
        if parsed.scheme in ('http', 'https'):
            links.add(abs_link)

    for img in soup.find_all('img', src=True):
        src = img['src']
        abs_img = urljoin(base_url, src)
        parsed = urlparse(abs_img)
        if parsed.scheme in ('http', 'https'):
            images.add(abs_img)

    return links, images

def search_index(query, index_data):
    print(f"\nSearching for '{query}' in links:")
    for url in sorted(index_data["links"]):
        if query.lower() in url.lower():
            print("  -", url)
    print(f"\nSearching for '{query}' in images:")
    for url in sorted(index_data["images"]):
        if query.lower() in url.lower():
            print("  -", url)

if __name__ == '__main__':
    target = input("Enter the URL to scrape: ").strip()
    index = load_index()
    before_links = len(index["links"])
    before_images = len(index["images"])

    # Fetch & parse
    soup = fetch_html(target)
    if not soup:
        print("Could not fetch the page. Exiting.")
        exit(1)
    found_links, found_images = extract_links_and_images(soup, target)

    # Merge into index
    index["links"].update(found_links)
    index["images"].update(found_images)

    # Save and report
    save_index(index)
    new_links = len(index["links"]) - before_links
    new_images = len(index["images"]) - before_images
    print(f"Added {new_links} new link(s) and {new_images} new image(s).")
    print(f"Total in index → {len(index['links'])} links; {len(index['images'])} images.")

    # Optional: simple search
    choice = input("Search the index now? (y/N): ").strip().lower()
    if choice == 'y':
        q = input("Enter search term: ").strip()
        search_index(q, index)
