from pydantic import BaseModel, Field
from typing import List, Literal

class StatementProvenance(BaseModel):
    statement: str = Field(description="The factual statement or reported claim.")
    source_article_ids: List[int] = Field(description="List of article IDs that support this statement.")
    support_level: Literal["direct", "reported", "indirect", "disputed", "uncertain"] = Field(
        description="The level of support the source provides for this statement."
    )

class StoryAnalysisSchema(BaseModel):
    story_title: str = Field(description="A concise, neutral title summarizing the story event")
    category: str = Field(description="The primary category, e.g., geopolitics, diplomacy, military")
    importance_score: int = Field(description="Estimated importance from 0 to 100", ge=0, le=100)
    confidence_score: int = Field(description="Confidence in the overall narrative based on source agreement, from 0 to 100", ge=0, le=100)
    
    risk_level: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        description="Geopolitical risk level. HIGH for conflict, casualties, sanctions, etc."
    )
    risk_reasons: List[str] = Field(description="Reasons for the assigned risk level")
    
    countries: List[str] = Field(description="List of countries involved in the story")
    entities: List[str] = Field(description="Key organizations or people involved")
    
    confirmed_facts: List[StatementProvenance] = Field(description="Facts directly supported by the sources")
    reported_claims: List[StatementProvenance] = Field(description="Claims reported by sources but not objectively verified")
    disputed_claims: List[StatementProvenance] = Field(description="Claims explicitly contradicted by different sources")
    uncertain_information: List[StatementProvenance] = Field(description="Information that lacks detail or is highly uncertain")
    
    key_events: List[str] = Field(description="The main sequence of events")
    timeline: List[str] = Field(description="Chronological timeline of the story if applicable")
    context: List[str] = Field(description="Relevant background context needed to understand the story")
    why_it_matters: List[str] = Field(description="The geopolitical or global significance of these events")
    possible_angles: List[str] = Field(description="Potential editorial angles to cover")
    source_summary: List[str] = Field(description="Brief summary of how different sources are covering the story")
