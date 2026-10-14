from bs4 import BeautifulSoup
from typing import List
from app.sources.base import BaseSource, ArticleCandidate
from app.utils.logger import setup_logger

logger = setup_logger("cnn_source")

class CNNPoliticsSource(BaseSource):
    name = "CNN Politics"
    base_url = "https://edition.cnn.com/politics"
    source_type = "news"
    domain = "cnn.com"
    country = "USA"
    region = "North America"
    category = "politics"
    categories = "politics,us"
    reliability_level = "high"
    language = "en"

    def discover_articles(self, html_content: str) -> List[ArticleCandidate]:
        candidates = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            all_headlines = soup.find_all("span", class_=lambda x: x and 'headline-text' in x)
            
            seen_links = set()
            for span in all_headlines:
                title = span.get_text(strip=True)
                if len(title) < 10:
                    continue
                    
                parent_a = span.find_parent('a')
                if parent_a:
                    link = parent_a['href']
                    if link.startswith('/'):
                        link = "https://edition.cnn.com" + link
                    
                    if link not in seen_links:
                        seen_links.add(link)
                        candidates.append(ArticleCandidate(title=title, url=link))
        except Exception as e:
            logger.error(f"Error discovering articles from CNN Politics: {e}")
            
        return candidates
