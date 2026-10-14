import time
import uuid
from datetime import datetime
from app.database.connection import SessionLocal
from app.database.models import PipelineRun, Article, Story, AIAnalysis, EditorialDraft, Source
from app.sources.cnn import CNNPoliticsSource
from app.sources.rss import (
    ReutersWorldRSS, BBCWorldRSS, AlJazeeraRSS, 
    DWRSS, France24RSS, UNNewsRSS
)
from app.extraction.html_loader import HTMLLoader
from app.ingestion.discovery import DiscoveryService
from app.extraction.processor import ExtractionProcessor
from app.clustering.grouper import StoryGrouper
from app.intelligence.gemini import IntelligenceService
from app.editorial.generator import EditorialGenerator
from app.utils.logger import setup_logger

logger = setup_logger("pipeline")

class PipelineRunner:
    def __init__(self):
        self.db = SessionLocal()
        self.sources = [
            CNNPoliticsSource,
            ReutersWorldRSS,
            BBCWorldRSS,
            AlJazeeraRSS,
            DWRSS,
            France24RSS,
            UNNewsRSS
        ]
        self.current_run = None

    def start_run(self):
        run_id = str(uuid.uuid4())
        self.current_run = PipelineRun(run_id=run_id, status='running')
        self.db.add(self.current_run)
        self.db.commit()
        logger.info(f"Started Pipeline Run ID: {run_id}")

    def finish_run(self, success=True):
        if not self.current_run:
            return
            
        self.current_run.finished_at = datetime.utcnow()
        self.current_run.duration_seconds = (self.current_run.finished_at - self.current_run.started_at).total_seconds()
        self.current_run.status = 'success' if success else 'failed'
        
        # Calculate some simple stats
        # For simplicity, we just log the time it took. 
        # In a real system, you'd increment these inside the services or query the DB by time range.
        self.db.commit()
        logger.info(f"Finished Pipeline Run ID: {self.current_run.run_id} in {self.current_run.duration_seconds:.2f}s")

    def run_ingestion(self):
        logger.info("--- Phase 1: Ingestion ---")
        with HTMLLoader() as loader:
            discovery_service = DiscoveryService(self.db, loader)
            for source_cls in self.sources:
                try:
                    discovery_service.run_discovery(source_cls)
                    if self.current_run:
                        self.current_run.sources_checked += 1
                except Exception as e:
                    logger.error(f"Ingestion failed completely for {source_cls.name}: {e}")
                    self.db.rollback()
        if self.current_run:
            self.db.commit()

    def run_extraction(self):
        logger.info("--- Phase 2: Extraction ---")
        with HTMLLoader() as loader:
            extractor = ExtractionProcessor(self.db, loader)
            extractor.process_pending_articles()
            # Update metrics if needed

    def run_clustering(self):
        logger.info("--- Phase 3: Clustering ---")
        grouper = StoryGrouper(self.db)
        grouper.cluster_extracted_articles()

    def run_intelligence(self):
        logger.info("--- Phase 4: Intelligence ---")
        intelligence_service = IntelligenceService(self.db)
        intelligence_service.analyze_stories()

    def run_editorial(self):
        logger.info("--- Phase 5: Editorial Generation ---")
        generator = EditorialGenerator(self.db)
        generator.generate_editorial_drafts()

    def run_full(self):
        logger.info("Starting Full Pipeline Execution")
        self.start_run()
        try:
            self.run_ingestion()
            self.run_extraction()
            self.run_clustering()
            self.run_intelligence()
            self.run_editorial()
            self.finish_run(success=True)
        except Exception as e:
            logger.error(f"Pipeline crashed: {e}")
            self.finish_run(success=False)
        logger.info("Full Pipeline Execution Complete")
        
    def get_health_stats(self):
        sources = self.db.query(Source).all()
        for source in sources:
            logger.info(f"Source: {source.name} | Enabled: {source.enabled} | Total Articles: {source.total_articles}")
            logger.info(f"  Last Success: {source.last_success_at} | Last Error: {source.last_error}")
            
        last_run = self.db.query(PipelineRun).order_by(PipelineRun.started_at.desc()).first()
        if last_run:
            logger.info(f"Last Pipeline Run: {last_run.run_id} | Status: {last_run.status} | Duration: {last_run.duration_seconds}s")
            
    def close(self):
        self.db.close()
