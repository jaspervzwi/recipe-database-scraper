import datetime

from recipe_scrapers import scrape_html, scraper_exists_for

from .sitemap_scraper import SitemapScraper
from .get_html import HTMLScraper
from ._utils import FileHandler, robots_parser, is_valid_url


class Recipe:
    def __init__(self, recipe_dict: dict):
        self.recipe_dict = recipe_dict

    def structure(self):
        self.url = self.recipe_dict["page_url"]
        self.last_modified_date = self.recipe_dict["last_modified"]
        self.canonical_url = self.recipe_dict["canonical_url"]
        self.site_name = self.recipe_dict["site_name"]
        self.host = self.recipe_dict["host"]
        self.language = self.recipe_dict["language"]
        self.title = self.recipe_dict["title"]
        self.author = self.recipe_dict["author"]
        self.ingredients = self.recipe_dict["ingredients"]
        self.ingredient_groups = self.recipe_dict["ingredient_groups"]
        self.instructions_list = self.recipe_dict["instructions_list"]
        self.category = self.recipe_dict["category"]
        self.yields = self.recipe_dict["yields"]
        self.total_time = self.recipe_dict["total_time"]
        self.cook_time = self.recipe_dict["cook_time"]
        self.prep_time = self.recipe_dict["prep_time"]
        self.ratings = self.recipe_dict["ratings"]
        self.ratings_count = self.recipe_dict["ratings_count"]
        self.nutrients = self.recipe_dict["nutrients"]
        self.image = self.recipe_dict["image"]


class Recipes:
    def __init__(self):
        self.recipes = {}
        self.pages_without_recipe = []

    def add_recipe(self, page_url, recipe: Recipe):
        self.recipes[page_url] = recipe.recipe_dict

    def add_non_recipe_page(self, page_url: str):
        self.pages_without_recipe.append(page_url)

    def add_non_recipe_page_list(self, page_list: list):
        self.pages_without_recipe.extend(page_list)

    def to_json(self):
        if len(self.pages_without_recipe) > 0:
            self.recipes["Pages without Recipe"] = self.pages_without_recipe
        return self.recipes


class RecipeScraper:
    def __init__(self, url, user_agent):
        self.url = url
        self.user_agent = user_agent
        self.recipes = Recipes()
        self.website_supported = False
        self._recipe_scraper_supported()
        self.batch_buffer = 0
        try:
            self.robots_parser = robots_parser(self.url)
        except Exception:
            print("Cannot find robots.txt ")
            self.robots_parser = None

    def _recipe_scraper_supported(self) -> bool:
        """Check if website is supported by recipe-scrapers lib. If not, return value"""
        website_supported = scraper_exists_for(self.url)
        if website_supported:
            self.website_supported = website_supported
        else:
            print(
                f"The website '{self.url}' is not supported by default in the parent library: recipe-scrapers!\n"
                + "---\n"
                + "Scraper will still pull the data from pages with Recipe schema, but without the use of a prepared data format\n"
                + "Please verify if output contains all expected features\n"
                + "---\n"
                + "For supported scrapers, please see: https://github.com/hhursev/recipe-scrapers\n"
                + "If you have time to help us out, please report this as a feature\n"
                + "More information on: https://github.com/hhursev/recipe-scrapers?tab=readme-ov-file#if-you-want-a-scraper-for-a-new-site-added\n"
                + "---"
            )

    def _handle_exclusions_list(self, exclusions_list: list, input_dict: dict):
        """Return pages that should be excluded from def scrape_to_json. Either:
        - 'Pages without Recipe' key values from input_dict (in case of manual dict input)
        - 'exclusion_list' file content pulled from input_file location
        """
        if input_dict and len(exclusions_list) == 0:
            input_location = "input dict"
            exclusions_list = input_dict.pop("Pages without Recipe", [])
        else:
            input_location = "_recipe_scraper_exclusions.json file"

        if len(exclusions_list) > 0:
            print(f"Found {len(exclusions_list)} pages to exclude in {input_location}")

        return exclusions_list

    def _handle_input_dict(self, input_dict: dict):
        """Check input_dict for:
        - 'Pages without Recipe' key to exclude in def scrape_to_json
        - Entries in input_dict that are not valid urls
        - Entries in input_dict that are missing the 'last_modified' key
        """
        invalid_urls = []
        if input_dict:
            input_dict.pop("Pages without Recipe", None)  # in case of manual dict input
            print(f"Found {len(input_dict)} pages with recipe in input dict")

            for url in input_dict:
                try:
                    is_valid_url(url)
                    # Check if the url contains a last_modified key, which is required for matching in def _url_in_input_data
                    input_dict[url]["last_modified"]

                except Exception as e:
                    print("Input key error: " + url + ": " + str(type(e)) + str(e))
                    invalid_urls.append(url)

            if len(invalid_urls) > 0:
                print(
                    "\n---\n"
                    + f"WARNING: Found {str(len(invalid_urls))} invalid urls in input dict.\n"
                    + "Please check if urls are valid and follow the format: 'url': {'author' : 'Name Author' , ... , 'last_modified': 'xxxx-xx-xxTxx:xx:xx-xx:xx'}\n"
                    + "Scraper will continue without checking input dict for following urls:\n"
                    + str(invalid_urls)
                    + "\n---\n"
                )
                for url in invalid_urls:
                    input_dict.pop(url)
        return input_dict

    def _url_in_input_data(self, page, input_dict):
        """Check if page URL exists in input_dict and compare last_modified dates"""
        try:
            input_recipe = input_dict.get(page.page_url)
            if input_recipe and page.last_modified == input_recipe["last_modified"]:
                return input_recipe
        except (KeyError, TypeError):
            pass
        return None

    def _scrape_recipe_page(self, page_url, last_modified):
        """Retrieve html of webpage, then use recipe-scrapers.scrape_html module for determining if recipe schema is available, and retrieving it"""
        try:
            html = HTMLScraper().scrape_page(page_url, self.user_agent)
            scraper = scrape_html(html, page_url, supported_only=self.website_supported)
            scraper.title()  # Check if recipe schema is available by pulling standard recipe schema field from recipe_scrapers.scrape_html
            recipe_json = scraper.to_json()
            recipe_json["last_modified"] = last_modified
            return Recipe(recipe_json)
        except (
            TypeError,
            NotImplementedError,
        ):  # NoneType found for scraper.title() OR title not present in recipe-scraper object
            print(f"Exception: No Recipe Schema found at {page_url}")
        except Exception as e:
            print(e)
        return None

    def _write_batch(self, batch_size, output_file):
        self.batch_buffer += 1
        if self.batch_buffer >= batch_size:
            recipes_json = self.recipes.to_json()
            FileHandler(output_file).write_json_file(recipes_json)
            self.batch_buffer = 0

    def scrape_to_json(
        self,
        *,
        input_dict: dict | None = None,
        exclusions_list: list | None = [],
        output_file: str | None = None,
        batch_size: int | None = None,
    ):

        pages_without_recipe = self._handle_exclusions_list(exclusions_list, input_dict)

        input_dict = self._handle_input_dict(input_dict)

        scraped_pages, filtered_out_urls = SitemapScraper(self.url).scrape()

        len_scraped_pages = len(scraped_pages)
        len_filtered_out_urls = len(filtered_out_urls)
        len_sitemap_pages = len_scraped_pages + len_filtered_out_urls

        scraped_pages.drop_url_list(pages_without_recipe)

        len_pages_to_scrape = len(scraped_pages)
        len_pages_without_recipe = len(pages_without_recipe)

        print(f"Found {str(len_sitemap_pages)} pages in sitemap")
        print(
            f"Found {str(len_filtered_out_urls)} pages in sitemap that should not contain recipes."
            f"Ignoring {str(len_filtered_out_urls + len_pages_without_recipe)} pages. Continuing with remaining {str(len_pages_to_scrape)} pages"
        )

        if len_filtered_out_urls > 0:
            self.recipes.add_non_recipe_page_list(filtered_out_urls)

        if len_pages_without_recipe > 0:
            self.recipes.add_non_recipe_page_list(pages_without_recipe)

        for scrape_count, p in enumerate(scraped_pages, start=1):
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
            status_message = f"{current_time} INFO [{str(scrape_count)}/{str(len_pages_to_scrape)}]: "

            # Proceed if robots.txt allows fetching the url or robots.txt isn't found
            if self.robots_parser is None or self.robots_parser.can_fetch(
                self.user_agent, self.url
            ):

                input_data = (
                    self._url_in_input_data(p, input_dict) if input_dict else None
                )

                if input_data:
                    recipe = Recipe(input_data)
                    print(
                        status_message
                        + f"Recipe data up-to-date, fetching from input file URL: {p.page_url}"
                    )
                else:
                    print(status_message + f"Scraping {p}")
                    recipe = self._scrape_recipe_page(p.page_url, p.last_modified)

                if recipe:
                    self.recipes.add_recipe(p.page_url, recipe)
                else:
                    self.recipes.add_non_recipe_page(p.page_url)

            else:
                print(
                    f"Robots.txt does not allow user agent '{self.user_agent}' to scrape URL: {p}"
                )

            if batch_size:
                self._write_batch(batch_size, output_file)

        recipes_json = self.recipes.to_json()
        return recipes_json
