import random
import time
from sqlalchemy.orm import Session
from app.extraction.html_loader import HTMLLoader
from app.extraction.parser import ArticleParser
from app.database.models import Article
from app.utils.hashing import generate_content_hash
from app.utils.logger import setup_logger

logger = setup_logger("extraction_processor")

class ExtractionProcessor:
    def __init__(self, db: Session, html_loader: HTMLLoader):
        self.db = db
        self.loader = html_loader

    def process_pending_articles(self, limit: int = 20):
        articles = self.db.query(Article).filter_by(status='discovered').limit(limit).all()
        
        if not articles:
            logger.info("No discovered articles to extract.")
            return

        for article in articles:
            logger.info(f"Extracting article ID {article.id}: {article.url}")
            try:
                # Add jitter
                time.sleep(random.uniform(1.0, 3.0))
                
                html = self.loader.get_html(article.url, force_refresh=False)
                parsed_data = ArticleParser.parse(article.url, html)
                
                if not parsed_data:
                    article.status = 'failed'
                    logger.warning(f"Failed to parse data for {article.url}")
                    self.db.commit()
                    continue
                
                content_hash = generate_content_hash(parsed_data["text"])
                
                # Check for content duplicates
                existing_content = self.db.query(Article).filter(
                    Article.content_hash == content_hash, 
                    Article.id != article.id
                ).first()
                
                if existing_content:
                    logger.info(f"Article ID {article.id} is a content duplicate of ID {existing_content.id}. Marking as duplicate.")
                    article.status = 'duplicate'
                    self.db.commit()
                    continue
                
                # Update article
                article.author = parsed_data["author"]
                article.published_at = parsed_data["published_at"]
                article.raw_text = parsed_data["text"]
                article.summary = parsed_data["summary"]
                article.image_url = parsed_data["top_image"]
                article.content_hash = content_hash
                article.status = 'extracted'
                
                self.db.commit()
                logger.info(f"Successfully extracted article ID {article.id}")
                
            except Exception as e:
                logger.error(f"Error extracting article ID {article.id}: {e}")
                article.status = 'error'
                self.db.commit()
