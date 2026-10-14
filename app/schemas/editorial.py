from pydantic import BaseModel, Field
from typing import List

class FacebookPostSchema(BaseModel):
    headline: str = Field(description="A catchy, short hook for the post")
    caption: str = Field(description="Main body of the Facebook post")
    key_facts: List[str] = Field(description="3-5 bullet points summarizing the event")
    why_it_matters: str = Field(description="A short sentence on why the audience should care")
    discussion_prompt: str = Field(description="A question to encourage comments")
    tags: List[str] = Field(description="Relevant hashtags")

class WebArticleSchema(BaseModel):
    seo_title: str = Field(description="SEO optimized title")
    headline: str = Field(description="H1 headline for the article")
    dek: str = Field(description="Sub-headline or short summary")
    summary: str = Field(description="Executive summary of the event")
    article_body: str = Field(description="Full text of the rewritten article in markdown format")
    key_facts: List[str] = Field(description="Bullet points for a summary box")
    background: str = Field(description="Background context explaining the history")
    timeline: List[str] = Field(description="Key dates/events")
    why_it_matters: str = Field(description="Why this event is globally significant")
    uncertainties: List[str] = Field(description="What remains unknown or disputed")
    source_references: List[str] = Field(description="List of sources used (e.g., 'According to Reuters...')")
