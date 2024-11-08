import re
import os
from publicsuffix2 import get_sld, get_tld
from urllib.parse import urlparse, urlunparse
import robots
import json

from ._exceptions import InvalidURLException, RobotParserException


def is_valid_url(url: str) -> bool:
    """
    Check whether input string is a valid URL

    :param url: string to check for URL, e.g. "http://www.example.com/page.html".
    """
    if not url:
        raise InvalidURLException("URL is empty.")

    try:
        parsed_url = urlparse(url)
    except Exception as ex:
        raise InvalidURLException(f"Unable to parse URL {url}: {ex}")

    if not parsed_url.scheme:
        raise InvalidURLException(
            "Scheme must be set. Please prefix http:// or https://"
        )

    if parsed_url.scheme.lower() not in ["http", "https"]:
        raise InvalidURLException("Scheme must be http:// or https://")

    if not parsed_url.netloc:
        raise InvalidURLException(f"Cannot determine domain name from {url}")

    regex_url = re.compile(
        r"^(https?):\/\/"  # http, https protocols
        r"(\w+(\-\w+)*\.)+[a-z]{2,}"  # domain name (example.com, etc.)
        r"(:[0-9]{1,5})?"  # optional port (e.g., :8080)
        r"(\/[\w\-]*)*"  # optional path (e.g. /something)
        r"(\.[a-zA-Z0-9]{1,5})?"  # optional file extension like .html, .jpg, etc.
        r"(\?\S*)?"  # optional query parameters
        r"(#\S*)?$",  # optional fragment
        re.IGNORECASE,
    )

    if re.match(regex_url, url):
        return True
    else:
        raise InvalidURLException(f"Invalid URL: {url}")


def domain_extractor(url: str) -> str:
    """
    Extract the domain name from a url

    :param url: URL to strip, e.g. "http://www.example.com/page.html".
    :return: Stripped URL domain name, e.g. "example"
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.split(":")[0]  # Strip port if present
    full_domain = get_sld(domain)
    tld = get_tld(domain)
    if full_domain and tld:
        main_domain = full_domain.replace(f".{tld}", "")
        return main_domain.split(".")[-1]  # Get the last part (SLD) without subdomains
    else:
        return full_domain


def strip_url_to_homepage(url: str) -> str:
    """
    Strip URL to its homepage.

    :param url: URL to strip, e.g. "http://www.example.com/page.html".
    :return: Stripped homepage URL, e.g. "http://www.example.com/"
    """

    parsed_url = urlparse(url)
    parsed_url = (
        parsed_url.scheme,
        parsed_url.netloc,
        "/",  # path
        "",  # params
        "",  # query
        "",  # fragment
    )
    url = urlunparse(parsed_url)

    return url


def robots_parser(url: str) -> object:
    """
    Check robots.txt file for allowed/disallowed pages to crawl & crawl conditions

    :param url: URL to check for, e.g. "http://www.example.com/page.html".
    :return: robot parser object
    """

    stripped_domain_url = strip_url_to_homepage(url)
    robots_file = stripped_domain_url + "robots.txt"
    try:
        parser = robots.RobotsParser.from_uri(robots_file)
    except Exception as ex:
        raise RobotParserException(
            f"Cannot find robots.txt file for {url}\nPlease check if {robots_file} exists.\nError: {ex}"
        )

    return parser


class FileHandler:
    """
    Handle opening & writing of files
    """

    def __init__(self, filename):
        self.filename = filename

    def load_exclusion_json_file(self):
        """Look for _recipe_scraper_exclusions.json file in same directory is as the input file and load its content"""
        input_dir = (
            os.path.dirname(self.filename)
            if os.path.dirname(self.filename)
            else os.getcwd()
        )

        exclusion_file = os.path.join(input_dir, "_recipe_scraper_exclusions.json")

        if os.path.isfile(exclusion_file):
            print(f"INFO: Found exclusion file: {exclusion_file}")
            exclusion_file_content = self.load_json_file(filename=exclusion_file)
            return exclusion_file_content
        else:
            print(
                "WARNING: No file found with the name '_recipe_scraper_exclusions.json' in the input directory."
            )

    def write_exclusion_json_file(self, data: dict):
        """Write or append to the recipe scraper exclusion list file. If it does not exist, create it"""
        output_dir = (
            os.path.dirname(self.filename)
            if os.path.dirname(self.filename)
            else os.getcwd()
        )

        exclusion_file = os.path.join(output_dir, "_recipe_scraper_exclusions.json")

        # Extract the single key-value pair from the provided data dict
        if len(data) != 1:
            raise ValueError(
                "Provided data dictionary must contain exactly one key-value pair."
            )

        key, value = next(iter(data.items()))

        if os.path.isfile(exclusion_file):
            exclusion_file_content = self.load_json_file(filename=exclusion_file)
        else:
            exclusion_file_content = {}

        exclusion_file_content[key] = value

        self.write_json_file(exclusion_file_content, filename=exclusion_file)

    def load_json_file(self, *, filename: str | None = None):
        """Return the content of the given json file. Unless specified otherwise, this method uses the class's input filename"""
        json_file = filename if filename else self.filename
        with open(json_file) as my_file:
            data = my_file.read()

        content = json.loads(data)
        return content

    def write_json_file(self, data, *, filename: str | None = None):
        """Return the content of the given json file. Unless specified otherwise, this method uses the class's input filename"""
        json_file = filename if filename else self.filename
        with open(json_file, "w") as my_file:
            json.dump(data, my_file)
