import sqlite3
import requests
from bs4 import BeautifulSoup
import newspaper


def get_article_body(url):
    try:
        # newspaper.article(url) is a shortcut that downloads and parses
        article = newspaper.article(url)
        return article.text
    except Exception as e:
        print(f"[-] Could not extract body for {url}: {e}")
        return None


def scrape_news():
    url = "https://edition.cnn.com/politics"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    all_headlines = soup.find_all("span", class_=lambda x: x and 'headline-text' in x)

    extracted_data = []
    seen_links = set()

    for span in all_headlines:
        title = span.get_text(strip=True)
        if len(title) < 10: continue

        parent_a = span.find_parent('a')
        if parent_a:
            link = parent_a['href']
            if link.startswith('/'):
                link = "https://edition.cnn.com" + link

            if link not in seen_links:
                print(f"[+] Found: {title}")
                body_text = get_article_body(link)

                if body_text:
                    extracted_data.append((title, link, body_text))
                    seen_links.add(link)

    return extracted_data


def save_to_sql(news_items):
    conn = sqlite3.connect('news_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE,
            link TEXT,
            body TEXT,
            status TEXT DEFAULT 'new'
        )
    ''')

    for title, link, body in news_items:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO articles (title, link, body) 
                VALUES (?, ?, ?)
            ''', (title, link, body))
        except Exception as e:
            print(f"Error saving: {e}")

    conn.commit()
    conn.close()
    print("[!] Database updated with full article bodies!")


# --- TESTING BLOCK ---
if __name__ == "__main__":
    print("Starting Scraper Test...")

    # 1. Run the scraper
    scraped_news = scrape_news()

    if scraped_news:
        print(f"Successfully scraped {len(scraped_news)} articles.")

        # 2. Save to SQL
        save_to_sql(scraped_news)

        # 3. Verification: Query the DB to see if data is actually there
        conn = sqlite3.connect('news_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT title, SUBSTR(body, 1, 100) FROM articles LIMIT 3")
        rows = cursor.fetchall()

        print("\n--- DATABASE CHECK (First 3 Rows) ---")
        for row in rows:
            print(f"TITLE: {row[0]}")
            print(f"BODY PREVIEW: {row[1]}...")
            print("-" * 30)
        conn.close()
    else:
        print("Scraper returned 0 results. Check your CSS classes or connection.")