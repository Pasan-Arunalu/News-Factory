import hashlib
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

def normalize_url(url: str) -> str:
    """Removes tracking parameters and normalizes the URL."""
    try:
        parsed = urlparse(url)
        # Remove common tracking parameters
        query = parse_qs(parsed.query)
        tracking_params = {'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'fbclid', 'gclid'}
        filtered_query = {k: v for k, v in query.items() if k not in tracking_params}
        
        # Reconstruct URL
        new_query = urlencode(filtered_query, doseq=True)
        # We also lower the netloc (domain)
        normalized = urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path, parsed.params, new_query, ''))
        
        # Remove trailing slash
        if normalized.endswith('/') and len(normalized) > 1:
            normalized = normalized[:-1]
            
        return normalized
    except Exception:
        return url

def generate_url_hash(url: str) -> str:
    """Generates a deterministic hash for a normalized URL."""
    normalized = normalize_url(url)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

def generate_content_hash(text: str) -> str | None:
    """Generates a hash for the article body to detect duplicates."""
    if not text:
        return None
    # Very basic normalization (strip whitespace, lowercase)
    # In a real-world scenario, you might want more advanced text normalization
    normalized_text = ' '.join(text.lower().split())
    return hashlib.sha256(normalized_text.encode('utf-8')).hexdigest()
