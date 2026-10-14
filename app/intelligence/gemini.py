import json
import os
from google import genai
from pydantic import ValidationError
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config.settings import settings
from app.database.models import Story, AIAnalysis
from app.schemas.intelligence import StoryAnalysisSchema
from app.utils.logger import setup_logger

logger = setup_logger("intelligence_gemini")

class IntelligenceService:
    def __init__(self, db: Session):
        self.db = db
        try:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.client = None

    def _load_prompt(self, version: str) -> str:
        prompt_path = os.path.join("app", "prompts", f"{version}.txt")
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Prompt version {version} not found.")
            return ""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def _call_gemini(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=StoryAnalysisSchema,
                temperature=0.2
            )
        )
        return response.text

    def analyze_stories(self, limit: int = 5):
        if not self.client:
            logger.error("Gemini client not initialized, skipping analysis.")
            return
            
        stories = self.db.query(Story).filter(
            Story.status == 'new', 
            Story.articles.any()
        ).limit(limit).all()
        
        prompt_version = "story_analysis_v2"
        system_prompt_template = self._load_prompt(prompt_version)
        if not system_prompt_template:
            return

        for story in stories:
            logger.info(f"Analyzing Story ID: {story.id}")
            
            # Format source material with Article IDs
            source_material = ""
            for article in story.articles:
                source_material += f"[Article ID {article.id}]:\n"
                source_material += f"Publisher: {article.source.name if article.source else 'Unknown'}\n"
                source_material += f"URL: {article.url}\n"
                source_material += f"Article Text:\n{article.raw_text}\n\n"
                
            prompt = system_prompt_template.replace("{source_material}", source_material)

            try:
                json_output = self._call_gemini(prompt)
                validated_data = StoryAnalysisSchema.model_validate_json(json_output)
                
                # Save analysis
                analysis = AIAnalysis(
                    story_id=story.id,
                    raw_json=validated_data.model_dump_json(),
                    prompt_version=prompt_version
                )
                self.db.add(analysis)
                
                # Update story with risk metrics
                story.status = 'analyzed'
                story.category = validated_data.category
                story.title = validated_data.story_title
                story.importance_score += validated_data.importance_score / 10.0
                
                story.risk_level = validated_data.risk_level
                if validated_data.risk_level == "HIGH":
                    story.requires_review = True
                
                self.db.commit()
                logger.info(f"Successfully analyzed Story ID {story.id} (Risk: {story.risk_level})")
                
            except ValidationError as ve:
                logger.error(f"Validation Error for Story ID {story.id}: {ve}")
                story.status = 'error'
                self.db.commit()
            except Exception as e:
                logger.error(f"AI Analysis Error for Story ID {story.id}: {e}")
                story.status = 'error'
                self.db.commit()
