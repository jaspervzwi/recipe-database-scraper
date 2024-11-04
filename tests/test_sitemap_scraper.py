import pytest
from unittest.mock import patch, MagicMock
from recipe_database_scraper._exceptions import SitemapScraperException
from recipe_database_scraper.sitemap_scraper import (
    SitemapScraper,
    Page,
    Pages,
    SITEMAP_FILTER_KEYWORDS,
    URL_FILTER_KEYWORDS,
)

# Mocked example of pages
mock_sitemap_page_1 = MagicMock(url="https://example.com/recipe/1", last_modified=None)
mock_sitemap_page_2 = MagicMock(url="https://example.com/blog/page", last_modified=None)

mock_filtered_pages = [
    MagicMock(url=f"https://example.com/page{keyword}", last_modified=None)
    for keyword in URL_FILTER_KEYWORDS
]

mock_sitemap_urls = MagicMock()
mock_sitemap_urls.all_pages.return_value = [
    mock_sitemap_page_1,
    mock_sitemap_page_2,
] + mock_filtered_pages
mock_sitemap_urls.url = "https://example.com/sitemap.xml"


@pytest.mark.sitemap
@patch("recipe_database_scraper.sitemap_scraper.sitemap_tree_for_homepage")
def test_url_filtering(mock_sitemap_tree_for_homepage):
    """Test the SitemapScraper and url filters with mocked sitemap data."""
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
mock_sub_sitemap_1.url = "https://example.com/recipes-sitemap.xml"
mock_sub_sitemap_1.all_pages.return_value = [
    MagicMock(url="https://example.com/recipes/page1", last_modified=None),
    MagicMock(url="https://example.com/recipes/page2", last_modified=None),
]

# Mocked sub-sitemaps that should be filtered based on SITEMAP keywords
mock_sub_sitemap_2 = MagicMock()
mock_sub_sitemap_2.url = (
    f"https://example.com/{list(SITEMAP_FILTER_KEYWORDS)[0]}-sub-sitemap.xml"
)
mock_sub_sitemap_2.all_pages.return_value = [
    MagicMock(url="https://example.com/sub-sitemap2/page1", last_modified=None),
    MagicMock(url="https://example.com/sub-sitemap2/page2", last_modified=None),
]

mock_sub_sitemap_3 = MagicMock()
mock_sub_sitemap_3.url = (
    f"https://example.com/{list(SITEMAP_FILTER_KEYWORDS)[1]}-sub-sitemap.xml"
)
mock_sub_sitemap_3.all_pages.return_value = [
    MagicMock(url="https://example.com/sub-sitemap3/page1", last_modified=None),
    MagicMock(url="https://example.com/sub-sitemap3/page2", last_modified=None),
]

# Mock a main sitemap that includes sub-sitemaps and non-filtered pages
mock_sitemap_sms = MagicMock()
mock_sitemap_sms.url = "https://example.com/sitemap.xml"
mock_sitemap_sms.all_pages.return_value = [
    MagicMock(url="https://example.com/blog/post1", last_modified=None)
]
mock_sitemap_sms.sub_sitemaps = [
    mock_sub_sitemap_1,
    mock_sub_sitemap_2,
    mock_sub_sitemap_3,
]


@pytest.mark.sitemap
@patch("recipe_database_scraper.sitemap_scraper.sitemap_tree_for_homepage")
def test_sub_sitemaps_filtering(mock_sitemap_tree_for_homepage):
    """Test the SitemapScraper filtering sub-sitemaps with keywords."""
    mock_sitemap_tree_for_homepage.return_value = mock_sitemap_sms

    scraper = SitemapScraper("https://example.com")
    pages, filtered_out_urls = scraper.scrape()

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


@pytest.mark.sitemap
def test_sitemap_get_pages():
    """Test the get pages logic of the SitemapScraper."""
    scraper = SitemapScraper("https://example.com")
    scraper.sitemap_tree = mock_sitemap_sms

    all_pages = scraper._get_all_pages()

    all_pages_urls = [page.url for page in all_pages]

    test_urls = [
        "https://example.com/recipes/page1",
        "https://example.com/sub-sitemap2/page1",
        "https://example.com/blog/post1",
    ]

    assert len(all_pages) == 7
    for test_url in test_urls:
        assert test_url in all_pages_urls


@pytest.mark.sitemap
def test_sitemap_scraper_url_filtering():
    """Test the filtering logic of the SitemapScraper."""
    scraper = SitemapScraper("https://example.com")
    scraper.sitemap_tree = mock_sitemap_sms

    filtered_urls = scraper._get_filter_urls()

    # Since the URL "https://example.com/sub-sitemap2/page1" should match the filter keywords, it should be filtered out
    assert "https://example.com/sub-sitemap2/page1" in filtered_urls
    assert "https://example.com/recipes/page1" not in filtered_urls


@pytest.mark.sitemap
@patch(
    "recipe_database_scraper.sitemap_scraper.sitemap_tree_for_homepage",
    side_effect=Exception("Sitemap parsing error"),
)
def test_sitemap_scraper_exception(mock_sitemap_tree_for_homepage):
    """Test the SitemapScraper handling a sitemap parsing exception."""
    scraper = SitemapScraper("https://example.com")

    with pytest.raises(SitemapScraperException, match="Sitemap parsing error"):
        scraper.scrape()


@pytest.mark.sitemap
def test_page_object():
    """Test the Page object and its string representation."""
    page = Page("https://example.com/recipe/1", "2024-10-18")
    assert str(page) == "URL: https://example.com/recipe/1, Last Modified: 2024-10-18"

    page_no_date = Page("https://example.com/recipe/1", None)
    assert (
        str(page_no_date) == "URL: https://example.com/recipe/1, Last Modified: Unknown"
    )


@pytest.mark.sitemap
def test_pages_class():
    """Test the Pages class functionality."""
    pages = Pages()
    assert len(pages) == 0

    page_1 = Page("https://example.com/recipe/1", None)
    page_2 = Page("https://example.com/recipe/2", "2024-10-18")
    pages.add_list([page_1, page_2])

    assert len(pages) == 2
    assert pages[0] == page_1
    assert list(pages) == [page_1, page_2]
