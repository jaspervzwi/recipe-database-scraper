from usp.tree import sitemap_tree_for_homepage

from ._utils import is_valid_url, strip_url_to_homepage
from ._exceptions import SitemapScraperException


class Page:
    def __init__(self, url, last_modified):
        self.page_url = url
        self.last_modified = last_modified
    
    def __str__(self):
        return f"URL: {self.page_url}, Last Modified: {self.last_modified}"

class Pages:
    def __init__(self):
        self.pages = []
    
    def __iter__(self):
        return iter(self.pages)
    
    def __len__(self):
        return len(self.pages) 

    def add(self, page: Page):
        self.pages.append(page)
    

class SitemapScraper:
    def __init__(self, homepage):
        self.homepage = homepage
        
    def scrape(self):
        ''' Retrieve a tree of AbstractSitemap subclass objects that represent the sitemap, including webpages, see https://ultimate-sitemap-parser.readthedocs.io/en/latest/usp.objects.html#module-usp.objects.sitemap '''
        stripped_homepage = strip_url_to_homepage(self.homepage)
        try:
            self.tree = sitemap_tree_for_homepage(stripped_homepage)
            self.all_pages = self.tree.all_pages()
        except Exception as e:
            raise SitemapScraperException(self.homepage, stripped_homepage, e)
        return self.all_pages

class PageScraper:
    def __init__(self, homepage):
        self.pages = Pages()
        self.homepage = homepage
    
    def scrape_domain(self):
        print(f"Retrieving sitemaps of {self.homepage} in order to fetch all webpages")
        all_pages = SitemapScraper(self.homepage).scrape()

        for p in all_pages:
            page_url = p.url
            last_modified = p.last_modified
            last_modified_str = last_modified.isoformat()

            page = Page(page_url, last_modified_str)
            self.pages.add(page)

    def scrape(self):
        if is_valid_url(self.homepage):
            self.scrape_domain()
            return self.pages
        else:
            print(f"{self.homepage} is not a valid url")
            print("Please enter the homepage url for the domain you intend to scrape, e.g. <https://example.com>")