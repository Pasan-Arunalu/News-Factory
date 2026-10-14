import newspaper
from typing import Optional, Dict, Any
from app.utils.logger import setup_logger

logger = setup_logger("article_parser")

class ArticleParser:
    @staticmethod
    def parse(url: str, html_content: str) -> Optional[Dict[str, Any]]:
        """
        Uses newspaper3k to parse HTML content and extract text, author, and date.
        """
        try:
            article = newspaper.Article(url)
            article.download(input_html=html_content)
            article.parse()
            
            # Additional cleanup or validation could go here
            if not article.text or len(article.text.strip()) < 50:
                logger.warning(f"Parsed article text is too short or empty for URL: {url}")
                return None
                
            return {
                "title": article.title,
                "author": ", ".join(article.authors) if article.authors else None,
                "published_at": article.publish_date,
                "text": article.text,
                "top_image": article.top_image,
                "summary": article.summary if article.summary else None
            }
        except Exception as e:
            logger.error(f"Failed to parse article {url}: {e}")
            return None
