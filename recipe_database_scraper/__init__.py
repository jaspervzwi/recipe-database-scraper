__all__ = ["scrape_site", "extract_domain", "strip_url_to_homepage"]

from .recipe_scraper import RecipeScraper
from ._utils import is_valid_url, domain_extractor, strip_url, FileHandler
from ._exceptions import (
    ExtractDomainException,
    StripURLToHomepageException,
    InputException,
)


def scrape_site(
    url: str,
    user_agent: str,
    *,
    input_dict: list | None = None,
    input_file: str | None = None,
    output_file: str | None = None,
    batch_size: int | None = None,
) -> RecipeScraper:

    try:
        is_valid_url(url)
    except Exception as ex:
        raise Exception(f"{ex}\nPlease adhere to URL format, e.g. https://example.com")

    stripped_url = strip_url(url)

    if input_file and input_dict:
        raise InputException(
            "Unable to determine whether to use input_file or input_dict. Please use only 1 input option"
        )

    if input_file and not input_file.endswith(".json"):
        raise InputException("Input file must be of json format, e.g. 'example.json'")

    if input_file:
        input_dict = FileHandler(input_file).load_json_file()

        all_exclusions_dict = FileHandler(input_file).load_exclusion_json_file()

    exclusions_list = (
        all_exclusions_dict.get(stripped_url, []) if all_exclusions_dict else []
    )

    if all_exclusions_dict and len(exclusions_list) == 0:
        print(
            "WARNING: URL not found in _recipe_scraper_exclusions.json file. Please ignore this warning if this is the first time scraping the URL"
        )

    if input_dict and not isinstance(input_dict, dict):
        raise InputException(
            f"Provided input_{"file content" if input_file else "dict"} is not a valid dict"
        )

    if output_file and not output_file.endswith(".json"):
        raise Exception("Output file must be of json format, e.g. 'example.json'")

    if batch_size and batch_size <= 0:
        raise ValueError("Batch size must be a positive integer.")

    if batch_size and not output_file:
        raise Exception("Writing batches requires having an output file to write to")

    recipes_json = RecipeScraper(stripped_url, user_agent).scrape_to_json(
        input_dict=input_dict,
        exclusions_list=exclusions_list,
        output_file=output_file,
        batch_size=batch_size,
    )

    if output_file:
        FileHandler(output_file).write_json_file(recipes_json)
    else:
        return recipes_json


def extract_domain(url: str) -> str:
    """
    Extract the domain name from a url

    :param url: URL to strip, e.g. "http://www.example.com/page.html".
    :return: Stripped URL domain name, e.g. "example"
    """
    try:
        is_valid_url(url)
    except Exception as ex:
        raise ExtractDomainException(
            f"{ex}\nPlease adhere to URL format, e.g. https://example.com"
        )

    extracted_domain = domain_extractor(url)

    return extracted_domain


def strip_url_to_homepage(url: str) -> str:
    """
    Strip URL to its homepage.

    :param url: URL to strip, e.g. "http://www.example.com/page.html".
    :return: Stripped homepage URL, e.g. "http://www.example.com/"
    """
    try:
        is_valid_url(url)
    except Exception as ex:
        raise StripURLToHomepageException(
            f"{ex}\nPlease adhere to URL format, e.g. https://example.com"
        )

    stripped_url = strip_url(url)

    return stripped_url
