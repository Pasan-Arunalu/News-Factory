from datetime import datetime
from sqlalchemy.orm import Session
from app.sources.base import BaseSource
from app.extraction.html_loader import HTMLLoader
from app.database.models import Article, Source
from app.utils.hashing import generate_url_hash, normalize_url
from app.utils.logger import setup_logger

logger = setup_logger("ingestion_discovery")

class DiscoveryService:
    def __init__(self, db: Session, html_loader: HTMLLoader):
        self.db = db
        self.loader = html_loader

    def get_or_create_source(self, source_cls: type[BaseSource]) -> Source:
        source = self.db.query(Source).filter_by(name=source_cls.name).first()
        if not source:
            source = Source(
                name=source_cls.name,
                base_url=source_cls.base_url,
                type=source_cls.type,
                domain=source_cls.domain,
                country=source_cls.country,
                region=source_cls.region,
                language=source_cls.language,
                source_type=source_cls.source_type,
                categories=source_cls.categories,
                reliability_level=source_cls.reliability_level,
                enabled=True
            )
            self.db.add(source)
            self.db.commit()
            self.db.refresh(source)
        return source

    def run_discovery(self, source_cls: type[BaseSource]):
        logger.info(f"Starting discovery for source: {source_cls.name}")
        
        # 1. Ensure source exists in DB
        db_source = self.get_or_create_source(source_cls)
        
        if not db_source.enabled:
            logger.info(f"Source {db_source.name} is disabled. Skipping.")
            return

        # 2. Fetch homepage/feed
        try:
            source_instance = source_cls()
            if source_instance.type == "rss":
                # Let the RSS source handle its own fetching
                html = None
            else:
                html = self.loader.get_html(source_cls.base_url, force_refresh=True)
                
            db_source.last_success_at = datetime.utcnow()
            db_source.consecutive_failures = 0
            db_source.last_error = None
        except Exception as e:
            logger.error(f"Failed to fetch base URL {source_cls.base_url}: {e}")
            db_source.last_failure_at = datetime.utcnow()
            db_source.consecutive_failures += 1
            db_source.last_error = str(e)
            self.db.commit()
            return
            
        # 3. Discover candidates
        try:
            candidates = source_instance.fetch_candidates(html)
        except Exception as e:
            logger.error(f"Failed to discover candidates for {source_cls.name}: {e}")
            db_source.last_failure_at = datetime.utcnow()
            db_source.consecutive_failures += 1
            db_source.last_error = str(e)
            self.db.commit()
            return
            
        logger.info(f"Found {len(candidates)} candidate articles for {source_cls.name}")
        
        # 4. Filter and insert new articles
        new_count = 0
        seen_hashes = set()
        for candidate in candidates:
            norm_url = normalize_url(candidate.url)
            url_hash = generate_url_hash(norm_url)
            
            if url_hash in seen_hashes:
                continue
                
            existing = self.db.query(Article).filter_by(url_hash=url_hash).first()
            if existing:
                continue
                
            seen_hashes.add(url_hash)
            
            new_article = Article(
                source_id=db_source.id,
                url=candidate.url,
                canonical_url=norm_url,
                url_hash=url_hash,
                title=candidate.title,
                status='discovered'
            )
            self.db.add(new_article)
            new_count += 1
            
        if new_count > 0:
            db_source.total_articles += new_count
            self.db.commit()
            
        logger.info(f"Discovery complete for {source_cls.name}. Saved {new_count} new articles.")
