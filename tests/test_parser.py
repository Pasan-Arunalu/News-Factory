import pytest
from app.extraction.parser import ArticleParser

def test_article_parser_empty_content():
    # Provide essentially empty HTML
    html = "<html><body><p>Too short.</p></body></html>"
    url = "https://example.com"
    
    result = ArticleParser.parse(url, html)
    # The parser enforces a minimum length of 50 chars for text
    assert result is None

def test_article_parser_valid_content():
    html = """
    <html>
        <head>
            <title>Test Title</title>
            <meta name="author" content="John Doe">
        </head>
        <body>
            <h1>Test Title</h1>
            <p>This is a sufficiently long paragraph to pass the length check. 
            It contains more than fifty characters easily.
            We need to make sure newspaper3k can extract it.</p>
        </body>
    </html>
    """
    url = "https://example.com"
    
    result = ArticleParser.parse(url, html)
    assert result is not None
    assert result["title"] == "Test Title"
    assert "sufficiently long paragraph" in result["text"]
