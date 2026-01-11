import os
import sqlite3
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load Environment Variables
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Setup AI Client
client = genai.Client(api_key=GEMINI_KEY)


def rewrite_article(original_body):
    system_instr = """
        You are a professional content rewriter.   
        Task:
        Rewrite the following articles in clear, original language while preserving the original meaning, facts, and intent.      
        Rules:
        - Do NOT copy phrases or sentence structures from the original text.
        - Keep all factual information accurate and unchanged.
        - Improve clarity, flow, and readability.
        - Use natural, human-like writing (not robotic or repetitive).
        - Avoid adding opinions, assumptions, or new information.
        - Do NOT mention that the text was rewritten or AI-generated.
        - Maintain the same overall length (±10%).
        
        Style:
        - Neutral and informative tone
        - Simple, professional English
        - Well-structured paragraphs
        
        Output only the rewritten article.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=original_body,
            config=types.GenerateContentConfig(
                system_instruction=system_instr,
                temperature=0.8,
            )
        )
        return response.text
    except Exception as e:
        print(f"[-] AI Generation Error: {e}")
        return None


def run_ai_pipeline():
    conn = sqlite3.connect('news_data.db')
    cursor = conn.cursor()

    # Find articles that haven't been rewritten yet
    cursor.execute("SELECT id, body FROM articles WHERE status = 'new' LIMIT 5")
    rows = cursor.fetchall()

    if not rows:
        print("[!] No new articles to process.")
        return

    for art_id, body in rows:
        print(f"[*] Rewriting Article ID: {art_id}...")

        rewritten_text = rewrite_article(body)

        if rewritten_text:
            # Update the SQL entry with the new text and status
            cursor.execute('''
                UPDATE articles 
                SET body = ?, status = 'rewritten' 
                WHERE id = ?
            ''', (rewritten_text, art_id))
            print(f"[+] Successfully transformed article {art_id}")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    run_ai_pipeline()