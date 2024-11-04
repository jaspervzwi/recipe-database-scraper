import pytest
from urllib.parse import urlparse
from recipe_database_scraper._utils import strip_url_to_homepage


@pytest.mark.util
@pytest.mark.parametrize(
    "url,expected_homepage",
    [
        ("http://www.example.com/page.html", "http://www.example.com/"),
        ("https://example.com", "https://example.com/"),
        (
            "http://subdomain.example.com/resource?query=param",
            "http://subdomain.example.com/",
        ),
        ("https://example.co.uk/path/to/page", "https://example.co.uk/"),
        ("http://www.example.org#fragment", "http://www.example.org/"),
        ("https://blog.example.com/another-page", "https://blog.example.com/"),
        ("http://sub.subdomain.example.com/path", "http://sub.subdomain.example.com/"),
        (
            "https://example.com/path/to/resource?query=param#fragment",
            "https://example.com/",
        ),
        ("https://www.example.edu/about", "https://www.example.edu/"),
        ("http://example.net/contact", "http://example.net/"),
        (
            "https://another.subdomain.example.co.uk/page.html",
            "https://another.subdomain.example.co.uk/",
        ),
        ("https://example.com:8080/path", "https://example.com:8080/"),
    ],
)
def test_strip_url_to_homepage(url, expected_homepage):
    """Test stripping URLs to their homepage."""
    assert strip_url_to_homepage(url) == expected_homepage


@pytest.mark.util
@pytest.mark.parametrize(
    "url",
    [
        "http://www.example.com/page.html",
        "http://sub.subdomain.example.com/path",
        "http://localhost:8000/path/to/resource",
    ],
)
def test_urlparse(url):
    """Test if urlparse library behaves as expected, specifically 'scheme' and 'netloc'"""
    parsed_url = urlparse(url)
    expected_homepage = f"{parsed_url.scheme}://{parsed_url.netloc}/"
    assert strip_url_to_homepage(url) == expected_homepage
