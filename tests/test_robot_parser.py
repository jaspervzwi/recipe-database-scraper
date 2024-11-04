import pytest
import robots
from unittest.mock import patch
from recipe_database_scraper._utils import robots_parser
from recipe_database_scraper._exceptions import RobotParserException

robots_mock_content = """
User-agent: *
Disallow: /private/
Disallow: /admin/
Allow: /public/
Allow: /recipe/

User-agent: Googlebot
Disallow: /no-google/

User-agent: Bingbot
Disallow: /no-bing/
"""


@pytest.mark.util
@patch("recipe_database_scraper._utils.robots.RobotsParser.from_uri")
def test_robot_parser(mock_from_uri):
    """Test the robot_parser function with mocked robots.txt data."""
    mock_parser = robots.RobotsParser.from_string(robots_mock_content)
    mock_from_uri.return_value = mock_parser

    url = "https://www.allrecipes.com/recipe/12345/"
    parser = robots_parser(url)

    mock_from_uri.assert_called_once_with("https://www.allrecipes.com/robots.txt")

    assert parser.can_fetch(
        "*", "/public/"
    ), "Expected /public/ to be allowed for any user-agent"
    assert parser.can_fetch(
        "*", "/shop/"
    ), "Expected /shop/ to be allowed for any user-agent"
    assert not parser.can_fetch(
        "*", "/private/"
    ), "Expected /private/ to be disallowed for any user-agent"
    assert parser.can_fetch(
        "Itsame Mario", "/public/"
    ), "Expected /public/ to be allowed for a specific user-agent"
    assert not parser.can_fetch(
        "Itsame Mario", "/private/"
    ), "Expected /private/ to be disallowed for a specific user-agent"
    assert parser.can_fetch(
        "Googlebot", "/public/"
    ), "Expected /public/ to be allowed for Googlebot"
    assert not parser.can_fetch(
        "Googlebot", "/no-google/"
    ), "Expected /no-google/ to be disallowed for Googlebot"
    assert not parser.can_fetch(
        "Bingbot", "/no-bing/"
    ), "Expected /no-bing/ to be disallowed for Bingbot"
    assert parser.can_fetch(
        "Bingbot", "/recipe/"
    ), "Expected /recipe/ to be allowed for Bingbot"


@pytest.mark.util
@patch(
    "recipe_database_scraper._utils.robots.RobotsParser.from_uri",
    side_effect=Exception("404 Not Found"),
)
def test_robot_parser_no_robots_file(mock_from_uri):
    """Test the robot_parser function when robots.txt file is missing."""
    url = "https://www.allrecipes.com/recipe/12345/"
    with pytest.raises(
        RobotParserException, match=f"Cannot find robots.txt file for {url}"
    ):
        robots_parser(url)
