import pytest
from unittest.mock import patch, MagicMock
from recipe_database_scraper._exceptions import SitemapScraperException
from recipe_database_scraper.sitemap_scraper import SitemapScraper, Page, Pages, SITEMAP_FILTER_KEYWORDS, URL_FILTER_KEYWORDS

# Mocked example of pages
mock_sitemap_page_1 = MagicMock(url="https://example.com/recipe/1", last_modified=None)
mock_sitemap_page_2 = MagicMock(url="https://example.com/blog/page", last_modified=None)


mock_filtered_pages = [
    MagicMock(url=f"https://example.com/page{keyword}", last_modified=None)
    for keyword in URL_FILTER_KEYWORDS
]

mock_sitemap_urls = MagicMock()
mock_sitemap_urls.all_pages.return_value = [mock_sitemap_page_1, mock_sitemap_page_2] + mock_filtered_pages
mock_sitemap_urls.url = "https://example.com/sitemap.xml"


@pytest.mark.sitemap
@patch("recipe_database_scraper.sitemap_scraper.sitemap_tree_for_homepage")
def test_url_filtering(mock_sitemap_tree_for_homepage):
    """Test the SitemapScraper with mocked sitemap data."""
    mock_sitemap_tree_for_homepage.return_value = mock_sitemap_urls

    scraper = SitemapScraper("https://example.com")
    pages, filtered_out_urls = scraper.scrape()

    assert len(pages) == 2  # Only the non-filtered pages should be included
    assert any(page.page_url == "https://example.com/recipe/1" for page in pages)
    assert any(page.page_url == "https://example.com/blog/page" for page in pages)

    for page in mock_filtered_pages:
        assert page.url in filtered_out_urls

    assert len(filtered_out_urls) == len(mock_filtered_pages)


# Mocked sub-sitemap that should not be filtered
mock_sub_sitemap_1 = MagicMock()
mock_sub_sitemap_1.url = f"https://example.com/recipes-sitemap.xml"
mock_sub_sitemap_1.all_pages.return_value = [
    MagicMock(url="https://example.com/recipes/page1", last_modified=None),
    MagicMock(url="https://example.com/recipes/page2", last_modified=None)
]

# Mocked sub-sitemaps that should be filtered based on SITEMAP keywords
mock_sub_sitemap_2 = MagicMock()
mock_sub_sitemap_2.url = f"https://example.com/{list(SITEMAP_FILTER_KEYWORDS)[0]}-sub-sitemap.xml"
mock_sub_sitemap_2.all_pages.return_value = [
    MagicMock(url="https://example.com/sub-sitemap2/page1", last_modified=None),
    MagicMock(url="https://example.com/sub-sitemap2/page2", last_modified=None)
]

mock_sub_sitemap_3 = MagicMock()
mock_sub_sitemap_3.url = f"https://example.com/{list(SITEMAP_FILTER_KEYWORDS)[1]}-sub-sitemap.xml"
mock_sub_sitemap_3.all_pages.return_value = [
    MagicMock(url="https://example.com/sub-sitemap3/page1", last_modified=None),
    MagicMock(url="https://example.com/sub-sitemap3/page2", last_modified=None)
]

# Mock a main sitemap that includes sub-sitemaps and non-filtered pages
mock_sitemap_sms = MagicMock()
mock_sitemap_sms.url = "https://example.com/sitemap.xml"
mock_sitemap_sms.all_pages.return_value = [
    MagicMock(url="https://example.com/blog/post1", last_modified=None)
]
mock_sitemap_sms.sub_sitemaps = [mock_sub_sitemap_1, mock_sub_sitemap_2, mock_sub_sitemap_3]

@pytest.mark.sitemap
@patch("recipe_database_scraper.sitemap_scraper.sitemap_tree_for_homepage")
def test_sub_sitemaps_filtering(mock_sitemap_tree_for_homepage):
    """Test the SitemapScraper filtering sub-sitemaps with keywords."""
    mock_sitemap_tree_for_homepage.return_value = mock_sitemap_sms

    scraper = SitemapScraper("https://example.com")
    pages, filtered_out_urls = scraper.scrape()

    print("found pages:")
    for page in pages:
        print(page)

    print("filtered out:")
    for p in filtered_out_urls:
        print(p)

    # Check that the main sitemap's non-filtered pages are included
    assert len(pages) == 3  # Main sitemap's page + mock_sub_sitemap_1 pages
    assert any(page.page_url == "https://example.com/blog/post1" for page in pages)
    assert any(page.page_url == "https://example.com/recipes/page1" for page in pages)

    # Check that all URLs from the sub-sitemaps with keywords are filtered out
    for sub_sitemap in [mock_sub_sitemap_2, mock_sub_sitemap_3]:
        for page in sub_sitemap.all_pages():
            assert page.url in filtered_out_urls

    # Verify the number of filtered URLs matches the expected count from both sub-sitemaps
    assert len(filtered_out_urls) == 4  # 2 pages from each of the filtered sub-sitemaps

