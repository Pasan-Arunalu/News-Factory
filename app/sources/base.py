from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ArticleCandidate:
    title: str
    url: str

class BaseSource:
    name: str
    base_url: str
    type: str = "html"          # e.g., 'html', 'rss'
    source_type: str = "news"   # e.g., 'news', 'wire'
    domain: str = ""
    country: str = ""
    region: str = ""
    category: str = ""
    categories: str = ""
    reliability_level: str = "medium"
    language: str = "en"
    
    def fetch_candidates(self, html_content: Optional[str] = None) -> List[ArticleCandidate]:
        """
        Main entry point for discovery. Subclasses can override this if they don't need the html_content
        from the default HTMLLoader (e.g., RSS feeds).
        """
        if html_content is None:
            return []
        return self.discover_articles(html_content)

    def discover_articles(self, html_content: str) -> List[ArticleCandidate]:
        """
        Parses the homepage/feed and returns a list of candidate articles.
        """
        raise NotImplementedError("Must implement discover_articles or fetch_candidates")
