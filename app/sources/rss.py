import feedparser
from typing import List, Optional
from app.sources.base import BaseSource, ArticleCandidate
from app.utils.logger import setup_logger

logger = setup_logger("rss_source")

class RSSSource(BaseSource):
    type = "rss"

    def fetch_candidates(self, html_content: Optional[str] = None) -> List[ArticleCandidate]:
        # We ignore html_content and fetch the RSS feed directly
        return self.discover_articles("")

    def discover_articles(self, _html_content: str) -> List[ArticleCandidate]:
        candidates = []
        try:
            feed = feedparser.parse(self.base_url)
            if feed.bozo:
                logger.warning(f"Feedparser returned bozo exception for {self.name}: {feed.bozo_exception}")

            for entry in feed.entries:
                if hasattr(entry, 'title') and hasattr(entry, 'link'):
                    candidates.append(ArticleCandidate(
                        title=entry.title,
                        url=entry.link
                    ))
        except Exception as e:
            logger.error(f"Error discovering articles from {self.name} RSS: {e}")
            raise e
        return candidates

class ReutersWorldRSS(RSSSource):
    name = "Reuters World"
    base_url = "https://www.reutersagency.com/feed/?best-topics=world-news&post_type=best"
    domain = "reuters.com"
    country = "UK"
    region = "Europe"
    category = "world"
    categories = "world,geopolitics"
    reliability_level = "high"
    language = "en"

class BBCWorldRSS(RSSSource):
    name = "BBC World"
    base_url = "http://feeds.bbci.co.uk/news/world/rss.xml"
    domain = "bbc.com"
    country = "UK"
    region = "Europe"
    category = "world"
    categories = "world,geopolitics"
    reliability_level = "high"
    language = "en"

class AlJazeeraRSS(RSSSource):
    name = "Al Jazeera"
    base_url = "https://www.aljazeera.com/xml/rss/all.xml"
    domain = "aljazeera.com"
    country = "Qatar"
    region = "Middle East"
    category = "world"
    categories = "world,geopolitics"
    reliability_level = "high"
    language = "en"

class DWRSS(RSSSource):
    name = "DW News"
    base_url = "https://rss.dw.com/rdf/rss-en-world"
    domain = "dw.com"
    country = "Germany"
    region = "Europe"
    category = "world"
    categories = "world,geopolitics"
    reliability_level = "high"
    language = "en"

class France24RSS(RSSSource):
    name = "France 24"
    base_url = "https://www.france24.com/en/rss"
    domain = "france24.com"
    country = "France"
    region = "Europe"
    category = "world"
    categories = "world,geopolitics"
    reliability_level = "high"
    language = "en"

class UNNewsRSS(RSSSource):
    name = "UN News"
    base_url = "https://news.un.org/feed/subscribe/en/news/all/rss.xml"
    domain = "un.org"
    country = "International"
    region = "Global"
    category = "world"
    categories = "world,geopolitics,un"
    reliability_level = "high"
    language = "en"
