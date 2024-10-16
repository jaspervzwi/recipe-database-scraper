import pytest
from urllib.parse import urlparse
from recipe_database_scraper._utils import is_valid_url
from recipe_database_scraper._exceptions import InvalidURLException

def test_valid_urls():
    """Test valid URLs."""
    valid_urls = [
        "http://www.example.com",
        "https://example.com",
        "http://example.com/page.html",
        "https://subdomain.example.com",
        "http://example.com/path/to/resource?query=param",
        "https://example.com#fragment",
        "https://example.co.uk",
        "http://www.example.com:8080",
    ]

    for url in valid_urls:
        assert is_valid_url(url) is True

def test_invalid_urls():
    """Test invalid URLs."""
    invalid_urls = [
        "ftp://example.com",               # Unsupported protocol
        "example.com",                     # Missing scheme (http/https)
        "http://",                         # Missing domain
        "https://",                        # Missing domain
        "http://.com",                     # Invalid domain
        "https://example",                 # TLD too short
        "http://example..com",             # Invalid domain format
        "http://example.com?query space",  # Space in query
        "http:///example.com",             # Too many slashes
        "://example.com",                  # Missing scheme before '://'
        "http://example.com:-80",          # Invalid port number
        "http://example.com:port",         # Non-numeric port
    ]

    for url in invalid_urls:
        with pytest.raises(InvalidURLException):
            is_valid_url(url)

def test_empty_url():
    """Test that an empty URL raises an InvalidURLException."""
    with pytest.raises(InvalidURLException, match="URL is empty."):
        is_valid_url("")

def test_scheme_missing():
    """Test that missing scheme raises an assertion error."""
    with pytest.raises(InvalidURLException, match="Scheme must be set"):
        is_valid_url("www.example.com")

def test_unsupported_scheme():
    """Test that unsupported schemes raise an InvalidURLException."""
    with pytest.raises(InvalidURLException, match="Scheme must be http:// or https://"):
        is_valid_url("ftp://www.example.com")

def test_missing_domain():
    """Test that missing domain raises an InvalidURLException."""
    with pytest.raises(InvalidURLException, match="Cannot determine domain name"):
        is_valid_url("http:///path")

def test_invalid_format():
    """Test that invalid URL formats raise an InvalidURLException."""
    with pytest.raises(InvalidURLException, match="Invalid URL"):
        is_valid_url("http://example..com")

def test_invalid_characters_in_url():
    """Test URLs with invalid characters."""
    with pytest.raises(InvalidURLException, match="Invalid URL"):
        is_valid_url("http://example.com/query?invalid query")

    with pytest.raises(InvalidURLException, match="Invalid URL"):
        is_valid_url("http://example.com/invalid_path<>")