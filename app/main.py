import argparse
from app.database.connection import init_db
from app.services.pipeline import PipelineRunner
from app.utils.logger import setup_logger

logger = setup_logger("main")

def main():
    parser = argparse.ArgumentParser(description="NewsScraper V2 CLI")
    parser.add_argument('command', choices=['init', 'ingest', 'extract', 'cluster', 'analyze', 'generate', 'run', 'health'],
                        help='The pipeline step to run')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized.")
        return

    runner = PipelineRunner()
    try:
        if args.command == 'ingest':
            runner.run_ingestion()
        elif args.command == 'extract':
            runner.run_extraction()
        elif args.command == 'cluster':
            runner.run_clustering()
        elif args.command == 'analyze':
            runner.run_intelligence()
        elif args.command == 'generate':
            runner.run_editorial()
        elif args.command == 'run':
            runner.run_full()
        elif args.command == 'health':
            runner.get_health_stats()
    finally:
        runner.close()

if __name__ == "__main__":
    main()
