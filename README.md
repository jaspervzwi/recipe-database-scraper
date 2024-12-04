`recipe-database-scraper` is a simple Python package that gathers all recipes from a website in order to maintain a database.

<br>

## Installation

```bash
pip install recipe-database-scraper
```

## Usage

```python
from recipe_database_scraper import scrape_site
```

## Example usage

Simple usage:

```python
from recipe_database_scraper import scrape_site

url = "https://barefeetinthekitchen.com/"
user_agent = "Hungry Scraper " + <myname>

data = scrape_site(url, user_agent)
```

Working with files:

```python
from recipe-database-scraper import scrape_site, extract_domain

url = "https://barefeetinthekitchen.com/"
user_agent = "Hungry Scraper " + <myname>
input_file = extract_domain(url) + ".json"
output_file = extract_domain(url) + "_new.json"

scrape_site(url, user_agent, input_file = input_file, output_file = output_file, batch_size = 100)
```

## Output

`recipe-database-scraper` currently only saves dicts to json files.

<br>

Every key is a webpage url scraped from the sitemap, that contains [Recipe Schema Markup](https://schema.org/Recipe).

<br>

If the output_file parameter is left empty, the scraper returns a dict containing the aforementioned url keys + an additional key "Pages without Recipe" - which contains a list of all urls that do not contain Recipe Schema Markup

<br>

If a json file is submitted as the output_file parameter, the scraper returns the url keys to that file and will also create an additional file in the same folder named "\_recipe_scraper_exclusions.json". Please note that in subsequent use of the tool, this will be looked for in the folder of the submitted "input_file"

<br>

Example output of website with 1 recipe page and 4 pages in total (in case no output_file parameter is submitted):

```json
{
  "https://example.com/recipes/something_yummy": {
    "author": "Iama Cook",
    "canonical_url": "https://example.com/recipes/something_yummy",
    "category": "yummy",
    "description": "Yummy food",
    "host": "example.com",
    "image": "https://example.com/yummy-default.jpg",
    "ingredient_groups": [
      {
        "ingredients": ["yummyness"],
        "purpose": null
      }
    ],
    "ingredients": ["yummyness"],
    "instructions": "Cook the food",
    "instructions_list": ["Step 1", "Prepare", "Step 2", "Cook"],
    "language": "en-Uk",
    "nutrients": {},
    "prep_time": null,
    "site_name": "Example",
    "title": "Yummy Food",
    "total_time": null,
    "yields": 1,
    "last_modified": "2024-12-31T59:59:59+00:00"
  },
  "Pages Without Recipe": [
    "https://example.com",
    "https://example.com/recipes",
    "https://example.com/blog"
  ]
}
```

## Acknowledgments

This package rests on the shoulders of [recipe-scrapers](https://github.com/hhursev/recipe-scrapers) and [ultimate-sitemap-parser](https://github.com/GateNLP/ultimate-sitemap-parser).

<br>

Thanks to [recipe-scrapers](https://github.com/hhursev/recipe-scrapers), this scraper can be used for scraping any website that contains recipe data. The [recipe-scrapers](https://github.com/hhursev/recipe-scrapers) package also offers a massive list of [websites with supported scrapers](https://github.com/hhursev/recipe-scraper/issues/new) for more accurate schema markup recognition. If the url you want to scrape is not on that list, please help out by suggesting the site name, as well as a recipe link to it in a [New issue on recipe-scrapers](https://github.com/hhursev/recipe-scraper/issues/new)
