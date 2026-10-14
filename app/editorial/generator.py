import os
from google import genai
from pydantic import ValidationError
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config.settings import settings
from app.database.models import Story, EditorialDraft
from app.schemas.editorial import FacebookPostSchema, WebArticleSchema
from app.utils.logger import setup_logger

logger = setup_logger("editorial_generator")

class EditorialGenerator:
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
    def _call_gemini(self, prompt: str, schema_class) -> str:
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema_class,
                temperature=0.4
            )
        )
        return response.text

    def _generate_draft(self, story: Story, platform: str, prompt_version: str, schema_class):
        system_prompt_template = self._load_prompt(prompt_version)
        if not system_prompt_template:
            return

        latest_analysis = story.ai_analyses[-1]
        prompt = system_prompt_template.replace("{intelligence_report}", latest_analysis.raw_json)

        try:
            json_output = self._call_gemini(prompt, schema_class)
            validated_data = schema_class.model_validate_json(json_output)
            
            status = "needs_review" if story.requires_review else "approved"
            
            draft = EditorialDraft(
                story_id=story.id,
                platform=platform,
                content_json=validated_data.model_dump_json(),
                status=status,
                prompt_version=prompt_version
            )
            
            self.db.add(draft)
            logger.info(f"Successfully generated {platform} draft for Story ID {story.id}")
            
        except ValidationError as ve:
            logger.error(f"Validation Error for {platform} Draft Story ID {story.id}: {ve}")
        except Exception as e:
            logger.error(f"Generation Error for {platform} Draft Story ID {story.id}: {e}")

    def generate_editorial_drafts(self, limit: int = 5):
        if not self.client:
            logger.error("Gemini client not initialized, skipping generation.")
            return

        stories = self.db.query(Story).filter(
            Story.status == 'analyzed',
            Story.ai_analyses.any()
        ).outerjoin(EditorialDraft, (EditorialDraft.story_id == Story.id)).filter(EditorialDraft.id == None).limit(limit).all()

        for story in stories:
            logger.info(f"Generating Editorial Drafts for Story ID: {story.id}")
            
            # Generate Facebook Draft
            self._generate_draft(story, "facebook", "facebook_post_v2", FacebookPostSchema)
            
            # Generate Web Article Draft
            self._generate_draft(story, "web", "web_article_v1", WebArticleSchema)
            
            story.status = 'draft_generated'
            self.db.commit()
