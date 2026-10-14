import json
from app.database.connection import SessionLocal
from app.database.models import Story, Article, AIAnalysis, EditorialDraft

def verify():
    db = SessionLocal()
    
    # Get the first story that has an editorial draft
    draft = db.query(EditorialDraft).first()
    if not draft:
        print("No editorial drafts found.")
        return
        
    story = draft.story
    print(f"=== STORY: {story.title} ===")
    print(f"Category: {story.category} | Importance: {story.importance_score}")
    print(f"Number of clustered articles: {len(story.articles)}")
    
    print("\n--- 1. PARSED ARTICLES ---")
    for article in story.articles:
        print(f"URL: {article.url}")
        print(f"Title: {article.title}")
        print(f"Author: {article.author}")
        print(f"Parsed Text (first 200 chars): {article.raw_text[:200]}...")
        print("-" * 20)
        
    print("\n--- 2. AI INTELLIGENCE ANALYSIS ---")
    if story.ai_analyses:
        analysis = story.ai_analyses[0]
        parsed_json = json.loads(analysis.raw_json)
        print(json.dumps(parsed_json, indent=2))
    else:
        print("No AI analysis found.")
        
    print("\n--- 3. EDITORIAL DRAFT (Facebook) ---")
    parsed_draft = json.loads(draft.content_json)
    print(f"Headline: {parsed_draft.get('headline')}")
    print(f"Caption: {parsed_draft.get('caption')}")
    print("Key Facts:")
    for fact in parsed_draft.get('key_facts', []):
        print(f"  - {fact}")
    print(f"Why it matters: {parsed_draft.get('why_it_matters')}")
    print(f"Discussion: {parsed_draft.get('discussion_prompt')}")
    print(f"Tags: {' '.join(parsed_draft.get('tags', []))}")
    
    db.close()

if __name__ == "__main__":
    verify()
