import time
import schedule
import sqlite3
import logging

from rewriter import rewrite_article
from news_scraper import scrape_news, save_to_sql

# 1. Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("factory.log"),  # Saves logs to a file
        logging.StreamHandler()  # prints to terminal
    ]
)


def run_news_factory():
    logging.info("Hourly Factory Cycle Started")

    # STEP 1: Scrape and Discover
    # Headlines already in DB are skipped via UNIQUE constraint in save_to_sql
    logging.info("[1/3] Scraping news...")
    try:
        raw_news = scrape_news()
        if raw_news:
            save_to_sql(raw_news)
    except Exception as e:
        logging.error(f"Scraper Error: {e}")

    # STEP 2: Selection (Individual Skip Logic)
    # skips anything already rewritten
    conn = sqlite3.connect('news_data.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, body FROM articles 
        WHERE status = 'new' 
        ORDER BY id DESC 
        LIMIT 10
    """)
    pending_articles = cursor.fetchall()

    if not pending_articles:
        logging.info("[!] No new articles found. Everything is already processed.")
        conn.close()
        return

    # STEP 3: Individual AI Transformation
    logging.info(f"[2/3] Processing {len(pending_articles)} fresh articles...")

    for art_id, title, body in pending_articles:
        logging.info(f"[*] AI Rewriting: {title[:50]}...")

        rewritten_text = rewrite_article(body)

        if rewritten_text:
            # Atomic update: once status is 'rewritten', it's never picked by Step 2 again
            cursor.execute("""
                UPDATE articles 
                SET body = ?, status = 'rewritten' 
                WHERE id = ?
            """, (rewritten_text, art_id))
            conn.commit()
            logging.info(f"    Successfully transformed.")
        else:
            logging.warning(f"    AI failed for Article {art_id}.")

    conn.close()
    logging.info("Cycle Complete. Waiting for next hour.")


if __name__ == "__main__":
    logging.info("System Initializing...")

    run_news_factory()

    schedule.every(1).hours.do(run_news_factory)

    logging.info("Factory is LIVE. Automation scheduled every 60 minutes.")

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("System shutting down gracefully...")