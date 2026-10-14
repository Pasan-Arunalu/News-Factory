from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.models import Article, Story
from app.utils.logger import setup_logger
from datetime import datetime, timedelta
import re

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

logger = setup_logger("clustering_grouper")

class StoryGrouper:
    def __init__(self, db: Session):
        self.db = db
        self.similarity_threshold = 0.40 # Requires decent overlap

    def cluster_extracted_articles(self):
        """
        Groups articles into stories based on title similarity.
        Uses TF-IDF + Cosine Similarity if scikit-learn is available,
        otherwise falls back to naive keyword intersection.
        """
        logger.info("Starting article clustering...")
        
        # Get unclustered articles
        articles = self.db.query(Article).filter_by(status='extracted').all()
        if not articles:
            logger.info("No extracted articles to cluster.")
            return
            
        recent_cutoff = datetime.utcnow() - timedelta(days=3)
        active_stories = self.db.query(Story).filter(Story.created_at >= recent_cutoff).all()
        
        for article in articles:
            try:
                matched_story = None
                
                if not active_stories:
                    pass
                elif HAS_SKLEARN:
                    # TF-IDF Clustering
                    corpus = [s.title for s in active_stories] + [article.title]
                    vectorizer = TfidfVectorizer(stop_words='english')
                    tfidf_matrix = vectorizer.fit_transform(corpus)
                    
                    # Compute similarity of the new article (last row) against all stories (all other rows)
                    similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1]).flatten()
                    
                    best_idx = similarities.argmax()
                    best_score = similarities[best_idx]
                    
                    if best_score >= self.similarity_threshold:
                        matched_story = active_stories[best_idx]
                        logger.debug(f"Matched '{article.title}' to '{matched_story.title}' (score: {best_score:.2f})")
                else:
                    # Fallback naive clustering
                    article_words = set(re.findall(r'\w+', article.title.lower()))
                    for story in active_stories:
                        story_words = set(re.findall(r'\w+', story.title.lower()))
                        overlap = len(article_words.intersection(story_words))
                        if overlap >= 3:
                            matched_story = story
                            break
                        
                if matched_story:
                    article.story_id = matched_story.id
                    article.status = 'clustered'
                    matched_story.importance_score += 1.0 
                    logger.info(f"Assigned Article ID {article.id} to existing Story ID {matched_story.id}")
                else:
                    new_story = Story(
                        title=article.title, 
                        category=article.source.categories.split(',')[0] if article.source and article.source.categories else 'general',
                        importance_score=1.0
                    )
                    self.db.add(new_story)
                    self.db.flush() # get ID
                    
                    article.story_id = new_story.id
                    article.status = 'clustered'
                    active_stories.append(new_story)
                    logger.info(f"Created new Story ID {new_story.id} for Article ID {article.id}")
            except Exception as e:
                logger.error(f"Error clustering article {article.id}: {e}")
                # Continue processing other articles to ensure isolation
                continue
                
        self.db.commit()
        logger.info("Clustering complete.")
