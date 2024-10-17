import pytest
from urllib.parse import urlparse
from recipe_database_scraper._utils import is_valid_url
from recipe_database_scraper._exceptions import InvalidURLException

@pytest.mark.util
@pytest.mark.parametrize("url", [
    "http://www.example.com",
    "https://example.com",
    "http://example.com/page.html",
    "https://subdomain.example.com",
    "http://example.com/path/to/resource?query=param",
    "https://example.com#fragment",
    "https://example.co.uk",
    "http://www.example.com:8080",
])
def test_valid_urls(url):
    assert is_valid_url(url) is True

@pytest.mark.util
@pytest.mark.parametrize("url", [
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
])
def test_invalid_urls(url):
    with pytest.raises(InvalidURLException):
        is_valid_url(url)

@pytest.mark.util
@pytest.mark.parametrize("url,expected_message", [
    ("", "URL is empty."),
    ("www.example.com", "Scheme must be set"),
    ("ftp://www.example.com", "Scheme must be http:// or https://"),
    ("http:///path", "Cannot determine domain name"),
    ("http://example..com", "Invalid URL"),
    ("http://example.com/query?invalid query", "Invalid URL"),
    ("http://example.com/invalid_path<>", "Invalid URL"),
])
def test_invalid_schemes_and_formats(url, expected_message):
    """Test that various invalid schemes and formats raise the expected InvalidURLException."""
    with pytest.raises(InvalidURLException, match=expected_message):
        is_valid_url(url)