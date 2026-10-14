from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Source(Base):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    base_url = Column(String, nullable=False)
    type = Column(String, nullable=False) # e.g. 'rss', 'html'
    
    # New Phase 2 Fields
    domain = Column(String, nullable=True)
    country = Column(String, nullable=True)
    region = Column(String, nullable=True)
    language = Column(String, default="en")
    source_type = Column(String, nullable=True) # news, wire, broadcast, government
    categories = Column(String, nullable=True) # comma separated
    
    reliability_level = Column(String)
    enabled = Column(Boolean, default=True)
    
    # Source Health Fields
    last_success_at = Column(DateTime, nullable=True)
    last_failure_at = Column(DateTime, nullable=True)
    consecutive_failures = Column(Integer, default=0)
    total_articles = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    articles = relationship("Article", back_populates="source")

class Story(Base):
    __tablename__ = 'stories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    category = Column(String)
    importance_score = Column(Float, default=0.0)
    status = Column(String, default='new')
    
    # Phase 5 Fields
    risk_level = Column(String, default='LOW') # LOW, MEDIUM, HIGH
    requires_review = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    articles = relationship("Article", back_populates="story")
    ai_analyses = relationship("AIAnalysis", back_populates="story")
    editorial_drafts = relationship("EditorialDraft", back_populates="story")

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    story_id = Column(Integer, ForeignKey('stories.id'), nullable=True)
    
    url = Column(String, unique=True, nullable=False)
    canonical_url = Column(String, nullable=True)
    url_hash = Column(String, unique=True, nullable=False)
    content_hash = Column(String, nullable=True)
    
    title = Column(String, nullable=False)
    author = Column(String, nullable=True)
    published_at = Column(DateTime, nullable=True)
    raw_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    
    status = Column(String, default='discovered') # discovered, extracted, failed, clustered
    scraped_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    source = relationship("Source", back_populates="articles")
    story = relationship("Story", back_populates="articles")

class AIAnalysis(Base):
    __tablename__ = 'ai_analyses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    story_id = Column(Integer, ForeignKey('stories.id'), nullable=False)
    raw_json = Column(Text, nullable=False)
    prompt_version = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    story = relationship("Story", back_populates="ai_analyses")

class EditorialDraft(Base):
    __tablename__ = 'editorial_drafts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    story_id = Column(Integer, ForeignKey('stories.id'), nullable=False)
    platform = Column(String, nullable=False) # e.g. 'facebook', 'web'
    content_json = Column(Text, nullable=False)
    status = Column(String, default='pending_review') # pending_review, needs_review, approved, published
    prompt_version = Column(String, nullable=True) # Added for Phase 5
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    story = relationship("Story", back_populates="editorial_drafts")

class PipelineRun(Base):
    __tablename__ = 'pipeline_runs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, unique=True, nullable=False)
    status = Column(String, default='running') # running, success, failed
    
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Metrics
    sources_checked = Column(Integer, default=0)
    articles_discovered = Column(Integer, default=0)
    articles_extracted = Column(Integer, default=0)
    articles_failed = Column(Integer, default=0)
    duplicates_removed = Column(Integer, default=0)
    stories_created = Column(Integer, default=0)
    stories_analyzed = Column(Integer, default=0)
    ai_failures = Column(Integer, default=0)
    drafts_generated = Column(Integer, default=0)
    high_risk_stories = Column(Integer, default=0)
