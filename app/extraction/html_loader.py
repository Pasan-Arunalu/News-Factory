import hashlib
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

from app.config.settings import settings
from app.utils.logger import setup_logger

logger = setup_logger("html_loader")

class HTMLLoader:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.cache_dir = Path(settings.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=settings.HEADLESS,
            args=["--disable-blink-features=AutomationControlled"]
        )
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def _get_cache_path(self, url: str) -> Path:
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        return self.cache_dir / f"{url_hash}.html"

    def get_html(self, url: str, force_refresh: bool = False, cache_ttl_seconds: int = 3600) -> str:
        cache_path = self._get_cache_path(url)

        if not force_refresh and cache_path.exists():
            cache_age = time.time() - cache_path.stat().st_mtime
            if cache_age <= cache_ttl_seconds:
                logger.debug(f"Cache hit for {url}")
                with open(cache_path, "r", encoding="utf-8") as f:
                    return f.read()

        logger.info(f"Fetching remote URL: {url}")
        page = self.context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=settings.PAGE_TIMEOUT_MS)
            page.wait_for_timeout(2000) # Let dynamic content load
            
            title = page.title()
            if "Just a moment" in title or "Cloudflare" in title:
                logger.warning("Cloudflare challenge detected, waiting...")
                page.wait_for_timeout(10000)
                if "Just a moment" in page.title() or "Cloudflare" in page.title():
                    raise RuntimeError("Could not bypass Cloudflare.")
            
            html = page.content()
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(html)
            return html
        finally:
            page.close()
