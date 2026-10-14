import pytest
from app.utils.hashing import normalize_url, generate_content_hash

def test_normalize_url():
    url1 = "https://edition.cnn.com/politics/article.html?utm_source=twitter"
    url2 = "https://edition.cnn.com/politics/article.html"
    
    assert normalize_url(url1) == url2
    
    # Trailing slash
    assert normalize_url("https://example.com/test/") == "https://example.com/test"
    
    # Multiple params
    url3 = "http://example.com/page?utm_medium=social&v=123"
    assert normalize_url(url3) == "http://example.com/page?v=123"
    
    # Domain case
    assert normalize_url("HTTPS://EXAMPLE.COM/page") == "https://example.com/page"

def test_generate_content_hash():
    text1 = "This is a test article.   It has some spaces."
    text2 = "this is a test article. it has some spaces."
    
    # Should be the same due to whitespace and lowercase normalization
    assert generate_content_hash(text1) == generate_content_hash(text2)
    
    text3 = "This is a completely different article."
    assert generate_content_hash(text1) != generate_content_hash(text3)
