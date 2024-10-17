import pytest
from urllib.parse import urlparse
from publicsuffix2 import get_sld, get_tld
from recipe_database_scraper._utils import domain_extractor

@pytest.mark.util
@pytest.mark.parametrize("url, expected_domain, expected_sld, expected_tld", [
    ("http://www.example.com/page.html", "example", "example.com", "com"),
    ("https://subdomain.example.co.uk", "example", "example.co.uk", "co.uk"),
    ("http://example.org/resource", "example", "example.org", "org"),
    ("https://another.subdomain.example.net", "example", "example.net", "net"),
    ("http://www.example.edu/about", "example", "example.edu", "edu"),
    ("https://example.com#fragment", "example", "example.com", "com"),
    ("https://subdomain.example.com:8080", "example", "example.com", "com"),
    ("http://another.example.io/path/to/page", "example", "example.io", "io"),
    ("https://example.co.jp", "example", "example.co.jp", "co.jp"),
    ("http://www.example.com.au", "example", "example.com.au", "com.au"),
    ("https://example.ai", "example", "example.ai", "ai"),
])
def test_domain_extractor(url, expected_domain, expected_sld, expected_tld):
    """Test that domain_extractor extracts the correct domain."""
    extracted_domain = domain_extractor(url)
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.split(':')[0] 

    # Verify the results of get_sld and get_tld from publicsuffix2
    assert get_sld(domain) == expected_sld, f"SLD extraction failed for {url}"
    assert get_tld(domain) == expected_tld, f"TLD extraction failed for {url}"

    # Verify the extracted domain matches the expected main domain
    assert extracted_domain == expected_domain, f"Domain extraction failed for {url}"