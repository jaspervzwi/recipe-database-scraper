import datetime
import requests

from recipe_scrapers import scrape_html, scraper_exists_for

from .page_scraper import PageScraper
from ._utils import FileHandler, robot_parser, is_valid_url

class Recipe:
    def __init__(self, recipe_dict: dict):
        self.recipe_dict = recipe_dict
    
    def structure(self):
        self.url = self.recipe_dict['page_url']
        self.last_modified_date = self.recipe_dict['last_modified']
        self.canonical_url = self.recipe_dict['canonical_url']
        self.site_name = self.recipe_dict['site_name']
        self.host = self.recipe_dict['host']
        self.language = self.recipe_dict['language']
        self.title = self.recipe_dict['title']
        self.author = self.recipe_dict['author']
        self.ingredients = self.recipe_dict['ingredients']
        self.ingredient_groups = self.recipe_dict['ingredient_groups']
        self.instructions_list = self.recipe_dict['instructions_list']
        self.category = self.recipe_dict['category']
        self.yields = self.recipe_dict['yields']
        self.total_time = self.recipe_dict['total_time']
        self.cook_time = self.recipe_dict['cook_time']
        self.prep_time = self.recipe_dict['prep_time']
        self.ratings = self.recipe_dict['ratings']
        self.ratings_count = self.recipe_dict['ratings_count']
        self.nutrients = self.recipe_dict['nutrients']
        self.image = self.recipe_dict['image']

class Recipes:
    def __init__(self):
        self.recipes = {}
        self.pages_without_recipe = []

    def add_recipe(self, page_url, recipe: Recipe):
        self.recipes[page_url] = recipe.recipe_dict

    def add_non_recipe_page(self, page_url):
        self.pages_without_recipe.append(page_url)
    
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
        self.pages_without_recipe = []
        self.batch_buffer = 0
        try: 
            self.rp = robot_parser(self.url)
        except Exception:
            print("Cannot find robots.txt ")
            self.rp = None

    def _recipe_scraper_supported(self) -> bool:
        '''Check if website is supported by recipe-scrapers lib. If not, return value '''
        website_supported = scraper_exists_for(self.url)
        if not website_supported:
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
        return 
    
    def _handle_input_dict(self, input_dict: dict):
        '''Check input_dict for:
            - 'Pages without Recipe' key to exclude in def scrape_to_json
            - Entries in input_dict that are not valid urls
            - Entries in input_dict that are missing the 'last_modified' key
        '''
        invalid_urls = []
        if input_dict:
            self.pages_without_recipe = input_dict.pop("Pages without Recipe", [])
            print(f"Found {len(input_dict)} pages with recipe in input dict")
            if len(self.pages_without_recipe) > 0:
                print(f"Found {len(self.pages_without_recipe)} pages without recipe in input dict")

            for url in input_dict:
                try:
                    is_valid_url(url)
                    last_modified = input_dict[url]["last_modified"] #check if the url contains a last_modified key, which is required for matching in def _url_in_input_data
                    datetime.datetime.fromisoformat(last_modified)
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
        '''Check if page URL exists in input_dict and compare last_modified dates '''
        try:
            input_recipe = input_dict.get(page.page_url)
            if input_recipe and page.last_modified == input_recipe["last_modified"]:
                return input_recipe
        except (KeyError, TypeError):
            pass
        return None
    
    def _scrape_recipe_page(self, page_url, last_modified):
        '''Retrieve html of webpage, then use recipe-scrapers.scrape_html module for determining if recipe schema is available, and retrieving it'''
        try:
            html = requests.get(page_url, headers={"User-Agent": self.user_agent}).content
            scraper = scrape_html(html, page_url, supported_only = self.website_supported)
            scraper.title() #check if recipe schema is available by pulling standard recipe schema field from recipe_scrapers.scrape_html
            recipe_json = scraper.to_json()
            recipe_json["last_modified"] = last_modified
            return Recipe(recipe_json)
        except (TypeError, NotImplementedError): #NoneType found for scraper.title() OR title not present in recipe-scraper object
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
            output_file: str | None = None,
            batch_size: int | None = None
        ):
        self.website_supported = self._recipe_scraper_supported()

        input_dict = self._handle_input_dict(input_dict)

        scraped_pages = PageScraper(self.url).scrape()
        len_scraped_pages = len(scraped_pages)
        print(f"Found {str(len_scraped_pages)} pages")

        for scrape_count, p in enumerate(scraped_pages, start=1):
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
            status_message = f"{current_time} INFO [{str(scrape_count)}/{str(len_scraped_pages)}]: "

            # Proceed if robots.txt allows fetching the url or robots.txt isn't found 
            if self.rp is None or self.rp.can_fetch(self.user_agent, self.url):

                is_in_pages_without_recipe = p.page_url in self.pages_without_recipe
                
                if is_in_pages_without_recipe:
                    self.recipes.add_non_recipe_page(p.page_url)
                else:
                    input_data = self._url_in_input_data(p, input_dict) if input_dict else None

                    if input_data:
                        recipe = Recipe(input_data)
                        print(status_message + f"Recipe data up-to-date, fetching from input file URL: {p.page_url}")
                    else:
                        print(status_message + f"Scraping {p}")
                        recipe = self._scrape_recipe_page(p.page_url, p.last_modified)
                        
                    if recipe:
                        self.recipes.add_recipe(p.page_url, recipe)
                    else:
                        self.recipes.add_non_recipe_page(p.page_url)

            else:
                print(f"Robots.txt does not allow user agent '{self.user_agent}' to scrape URL: {p}")
            
            if batch_size:
                self._write_batch(batch_size, output_file)
        
        recipes_json = self.recipes.to_json()
        return recipes_json

