import pytest
from unittest.mock import patch, MagicMock
from recipe_scrapers import get_supported_urls
from recipe_database_scraper.recipe_scraper import Recipe, Recipes, RecipeScraper
from recipe_database_scraper.sitemap_scraper import Pages

# Mock data for testing
MOCK_RECIPE_DICT = {
    "page_url": "https://example.com/recipe",
    "last_modified": "2000-01-01",
    "canonical_url": "https://example.com/recipe",
    "site_name": "Example Site",
    "host": "example.com",
    "language": "en",
    "title": "Test Recipe",
    "author": "Itsame Mario",
    "ingredients": ["green mushroom", "green turtle shell"],
    "ingredient_groups": [],
    "instructions_list": ["Hit box", "Jump on turtle"],
    "category": "Dinner",
    "yields": "4 servings",
    "total_time": "1 hour",
    "cook_time": "30 minutes",
    "prep_time": "30 minutes",
    "ratings": 5,
    "ratings_count": 100,
    "nutrients": {"calories": 200},
    "image": "https://example.com/image.jpg",
}


# ---- Tests for Recipe class ----


@pytest.mark.recipe
def test_recipe_structure():
    """Test that Recipe class correctly stores recipe data."""
    recipe = Recipe(MOCK_RECIPE_DICT)
    recipe.structure()
    assert recipe.url == MOCK_RECIPE_DICT["page_url"]
    assert recipe.title == MOCK_RECIPE_DICT["title"]
    assert recipe.author == MOCK_RECIPE_DICT["author"]
    assert recipe.ingredients == MOCK_RECIPE_DICT["ingredients"]


# ---- Tests for Recipes class ----


@pytest.mark.recipe
def test_recipes_add_recipe():
    """Test that Recipes class can add a recipe."""
    recipes = Recipes()
    recipe = Recipe(MOCK_RECIPE_DICT)
    recipes.add_recipe(recipe.recipe_dict["page_url"], recipe)
    assert recipe.recipe_dict["page_url"] in recipes.recipes
    assert (
        recipes.recipes[recipe.recipe_dict["page_url"]]["title"]
        == recipe.recipe_dict["title"]
    )


@pytest.mark.recipe
def test_recipes_add_non_recipe_page():
    """Test that Recipes class can track non-recipe pages."""
    recipes = Recipes()
    recipes.add_non_recipe_page("https://example.com/non-recipe-page")
    recipes.add_non_recipe_page_list(
        [
            "https://example.com/definitely_not_a_recipe",
            "https://example.com/absolutely_not_a_recipe",
        ]
    )
    assert "https://example.com/non-recipe-page" in recipes.pages_without_recipe
    assert "https://example.com/definitely_not_a_recipe" in recipes.pages_without_recipe
    assert "https://example.com/absolutely_not_a_recipe" in recipes.pages_without_recipe


@pytest.mark.recipe
def test_recipes_to_json():
    """Test that Recipes class outputs data in JSON format."""
    recipes = Recipes()
    recipe = Recipe(MOCK_RECIPE_DICT)
    recipes.add_recipe(recipe.recipe_dict["page_url"], recipe)
    recipes.add_non_recipe_page("https://example.com/non-recipe-page")
    output = recipes.to_json()
    assert "Pages without Recipe" in output
    assert "https://example.com/non-recipe-page" in output["Pages without Recipe"]
    assert recipe.recipe_dict["page_url"] in output


# ---- Tests for RecipeScraper class ----


@pytest.fixture
def mock_recipe_scraper():
    """Fixture to create a RecipeScraper with mocked dependencies."""
    scraper = RecipeScraper("https://example.com", "test-agent")
    return scraper


@pytest.mark.recipe
@patch("recipe_database_scraper.recipe_scraper.robots_parser")
def test_recipe_scraper_initialization(mock_robots_parser, mock_recipe_scraper):
    """Test initialization of RecipeScraper and robots_parser loading."""
    mock_robots_parser.return_value = MagicMock()
    assert mock_recipe_scraper.url == "https://example.com"
    assert mock_recipe_scraper.user_agent == "test-agent"
    assert mock_recipe_scraper.robots_parser is not None


@pytest.mark.recipe
@patch("recipe_database_scraper.recipe_scraper.scraper_exists_for", return_value=True)
def test_recipe_scraper_supported(mock_scraper_exists_for):
    """Test that the recipe scraper checks that a website is supported."""
    supported_urls = get_supported_urls()
    supported_url = list(supported_urls)[0]
    scraper = RecipeScraper(supported_url, "test-agent")
    result = scraper.website_supported
    assert result is True
    mock_scraper_exists_for.assert_called_once_with(scraper.url)


@pytest.mark.recipe
def test_recipe_scraper_not_supported(mock_recipe_scraper):
    """Test that the recipe scraper checks that a website is not supported."""
    result = mock_recipe_scraper.website_supported
    assert result is False


mock_input_dict = {
    "https://example.com/recipe": MOCK_RECIPE_DICT,
    "Pages without Recipe": [
        "https://example.com/non-recipe",
        "https://example.com/non-recipe-2",
    ],
}


@pytest.mark.recipe
@pytest.mark.parametrize(
    "exclusions_list, input_dict, expected_output, expected_location",
    [
        (
            [],
            mock_input_dict,
            ["https://example.com/non-recipe", "https://example.com/non-recipe-2"],
            "input dict",
        ),
        (
            ["https://example.com/page1"],
            {},
            ["https://example.com/page1"],
            "_recipe_scraper_exclusions.json file",
        ),
        ([], {}, [], "_recipe_scraper_exclusions.json file"),
        (
            ["https://example.com/page1"],
            mock_input_dict,
            [
                "https://example.com/page1",
                "https://example.com/non-recipe",
                "https://example.com/non-recipe-2",
            ],
            "_recipe_scraper_exclusions.json file & input file",
        ),
    ],
)
def test_handle_exclusions_list(
    mock_recipe_scraper,
    exclusions_list,
    input_dict,
    expected_output,
    expected_location,
    capsys,
):
    """Test _handle_exclusions_list for different exclusion sources and outputs."""
    handled_list = mock_recipe_scraper._handle_exclusions_list(
        exclusions_list, input_dict
    )

    assert sorted(handled_list) == sorted(
        expected_output
    ), f"Expected {sorted(expected_output)} but got {sorted(handled_list)}"

    captured = capsys.readouterr()
    if expected_output:
        assert (
            f"Found {len(expected_output)} pages to exclude in {expected_location}"
            in captured.out
        )
    else:
        assert "Found" not in captured.out  # Ensure no print for empty lists


@pytest.mark.recipe
def test_handle_input_dict(mock_recipe_scraper):
    """Test handling of input dict to identify pages without recipes and invalid URLs."""
    handled_dict = mock_recipe_scraper._handle_input_dict(mock_input_dict)
    assert "Pages without Recipe" not in handled_dict
    assert handled_dict["https://example.com/recipe"] == MOCK_RECIPE_DICT


@pytest.mark.recipe
def test_url_in_input_data(mock_recipe_scraper):
    """Test checking if a page URL exists in input data and has matching last_modified date."""
    page_mock = MagicMock()
    page_mock.page_url = "https://example.com/recipe"
    page_mock.last_modified = "2024-10-15"
    input_dict = {"https://example.com/recipe": {"last_modified": "2024-10-15"}}
    result = mock_recipe_scraper._url_in_input_data(page_mock, input_dict)
    assert result == input_dict["https://example.com/recipe"]


@pytest.mark.recipe
@patch("recipe_database_scraper.recipe_scraper.HTMLScraper")
@patch("recipe_database_scraper.recipe_scraper.scrape_html")
def test_scrape_recipe_page(mock_scrape_html, mock_html_scraper, mock_recipe_scraper):
    """Test scraping a recipe page for valid schema data."""
    mock_html_scraper().scrape_page.return_value = "<html></html>"
    mock_scrape_html.return_value.to_json.return_value = MOCK_RECIPE_DICT
    recipe = mock_recipe_scraper._scrape_recipe_page(
        "https://example.com/recipe", "2000-01-01"
    )
    assert recipe.recipe_dict == MOCK_RECIPE_DICT


@pytest.mark.recipe
@patch("recipe_database_scraper.recipe_scraper.FileHandler")
def test_write_batch(mock_file_handler, mock_recipe_scraper):
    """Test that _write_batch writes to file and handles exclusions after reaching batch size."""
    mock_file_handler_instance = mock_file_handler.return_value
    # mock_file_handler.return_value = MagicMock()
    mock_recipe_scraper.url = "https://example.com"
    mock_recipe_scraper.batch_buffer = 3
    mock_recipe_scraper.recipes = MagicMock()
    mock_recipe_scraper.recipes.to_json.return_value = mock_input_dict

    mock_recipe_scraper._write_batch(3, "test_output.json")

    expected_json_output = {"https://example.com/recipe": MOCK_RECIPE_DICT}
    mock_file_handler.return_value.write_json_file.assert_called_once_with(
        expected_json_output
    )

    expected_exclusion_dict = {
        "https://example.com": [
            "https://example.com/non-recipe",
            "https://example.com/non-recipe-2",
        ]
    }
    mock_file_handler_instance.write_exclusion_json_file.assert_called_once_with(
        expected_exclusion_dict
    )

    assert mock_recipe_scraper.batch_buffer == 0


@pytest.mark.recipe
@patch("recipe_database_scraper.recipe_scraper.RecipeScraper._scrape_recipe_page")
@patch("recipe_database_scraper.recipe_scraper.SitemapScraper")
def test_scrape_to_json(
    mock_sitemap_scraper, mock_scrape_recipe_page, mock_recipe_scraper
):
    """Test the scrape_to_json main flow, ensuring output JSON structure."""
    pages_obj = Pages()
    mock_page = MagicMock()
    mock_page.page_url = "https://example.com/recipe"
    mock_page.last_modified = "2000-01-01"
    mock_non_recipe_page = "https://example.com/not-a-recipe"

    pages_obj.add_list([mock_page])

    mock_sitemap_scraper.return_value.scrape.return_value = (
        pages_obj,
        [mock_non_recipe_page],
    )
    mock_scrape_recipe_page.return_value = Recipe(
        {"title": "Test Soup Recipe", "ingredients": ["Food", "Water"]}
    )
    json_output = mock_recipe_scraper.scrape_to_json()

    assert "https://example.com/recipe" in json_output
    assert "Pages without Recipe" in json_output
    assert "https://example.com/not-a-recipe" in json_output["Pages without Recipe"]
    assert "https://example.com/recipe" not in json_output["Pages without Recipe"]
