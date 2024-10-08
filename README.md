`recipe-database-scraper` is a simple Python package designed for gathering recipes from a website in order to maintain a database.

<br>

## Usage

```python
from recipe-database-scraper import scrape_site
```

## Example usage

Simple usage:
```python
from recipe-database-scraper import scrape_site

url = "https://barefeetinthekitchen.com/"
user_agent = "Hungry Scraper " + <myname>

data = scrape_site(url, user_agent)
```

Working with files:
```python
from recipe-database-scraper import scrape_site, extract_domain

url = "https://barefeetinthekitchen.com/"
user_agent = "Hungry Scraper " + <myname>
input_file = extract_domain + ".json"
output_file = extract_domain + "_new.json"

data = scrape_site(url, user_agent, input_file = input_file, output_file = output_file, batch_size = 100)
```

## Output

`recipe-database-scraper` currently only creates simple json dictionaries.
Every key is a webpage url scraped from the sitemap, that contains [Recipe Schema Markup](https://schema.org/Recipe)
With the exception of the last key - "Pages without Recipe" - which contains a list of all urls that do not contain Recipe Schema Markup

```json
{"https://example.com/recipes/something_yummy": {"author": "ItsaMe Mario", "canonical_url":"https://example.com/recipes/something_yummy","category":"yummy", "description": "Yummy food", "host": "example.com", "image": "https://example.com/yummy-default.jpg", "ingredient_groups": [{"ingredients": ["yummyness"], "purpose": null}], "ingredients": ["yummyness"], "instructions": "Cook the food", "instructions_list": ["Step 1", "Prepare", "Step 2", "Cook"], "language": "en-Uk", "nutrients": {}, "prep_time": null, "site_name": "Example", "title": "Yummy Food", "total_time": null, "yields": 1, "last_modified": "2024-12-31T59:59:59+00:00"},"Pages Without Recipe":["https://example.com", "https://example.com/recipes", "https://example.com/blog"]}
```


## Acknowledgments 
This package rests on the shoulders of [recipe-scrapers](https://github.com/hhursev/recipe-scrapers) and [ultimate-sitemap-parser](https://github.com/GateNLP/ultimate-sitemap-parser).
Thanks to [recipe-scrapers](https://github.com/hhursev/recipe-scrapers), this scraper can be used for scraping any website that contains recipe data. The [recipe-scrapers](https://github.com/hhursev/recipe-scrapers) package also offers a massive list of websites with supported scrapers for more accurate schema markup recognition. If the url you want to scrape is not on that list, please help out by reporting this as a feature.