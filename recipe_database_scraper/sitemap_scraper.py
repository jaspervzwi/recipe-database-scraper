from usp.tree import sitemap_tree_for_homepage

from ._utils import is_valid_url, strip_url_to_homepage
from ._exceptions import SitemapScraperException

SITEMAP_FILTER_KEYWORDS = {
    
    #All variations of advertisement indicators. Short keywords like 'ad' or 'ads' are specified with common adjacent characters in order not to accidently skip relevant sub-sitemaps
    "ad-sitemap",
    "-ad-",
    "/ad-",
    "ads-sitemap",
    "-ads-",
    "/ads-",
    "advertise",
    "adgroup",

    #All variations of sitetags. Short keywords like 'tag' are specified with common adjacent characters in order not to accidently skip relevant sub-sitemaps
    "/tag-",
    "-tag-",
    "tag-sitemap",

    "asset",

    "categor",

    "event",

    "image",

    "news",

    "video"

}
"""Sub-sitemap word combinations that commonly do not contain recipe pages"""

URL_FILTER_KEYWORDS = {
    #all image extensions
    ".png", ".apng", ".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".svg", ".webp", ".ico", ".cur", ".tif", ".tiff", ".bmp", ".xbm",

    #all video extensions
    ".webm",".mkv", ".flv", ".vob", ".ogv", ".ogg", ".rrc", ".gifv", ".mng", ".mov", ".avi", ".qt", ".wmv", ".yuv", ".rm", ".asf", ".amv", ".mp4", ".m4p", ".m4v", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".m4v", ".svi", ".3gp", ".3g2", ".mxf", ".roq", ".nsv", ".flv", ".f4v", ".f4p", ".f4a", ".f4b", ".mod",
    
    ".gif",
    
    ".pdf"
}
"""Url extensions for pages in the sitemap that should not be crawled"""


class Page:
    def __init__(self, url, last_modified):
        self.page_url = url
        self.last_modified = last_modified
    
    def __str__(self):
        last_modified_value = "Unknown" if self.last_modified is None else self.last_modified
        return f"URL: {self.page_url}, Last Modified: {last_modified_value}"

class Pages:
    def __init__(self):
        self.pages = []
    
    def __iter__(self):
        return iter(self.pages)
    
    def __len__(self):
        return len(self.pages) 
    
    def add_list(self, page_list: list):
        self.pages.extend(page_list)
    
class SitemapScraper:
    def __init__(self, homepage):
        self.homepage = homepage
        self.pages = Pages()
        self.filtered_out_urls = []
        self.sitemap_tree = None

    def scrape_sitemap(self):
        ''' Retrieve a tree of AbstractSitemap subclass objects that represent the sitemap, including webpages, see https://ultimate-sitemap-parser.readthedocs.io/en/latest/usp.objects.html#module-usp.objects.sitemap '''
        stripped_homepage = strip_url_to_homepage(self.homepage)
        try:
            self.sitemap_tree = sitemap_tree_for_homepage(stripped_homepage)
        except Exception as e:
            raise SitemapScraperException(self.homepage, stripped_homepage, e)
    
    
    def get_filter_urls(self) -> list:
        '''Return a list of urls filtered from the sitemap pages for specified keywords.'''
        def filter_out_pages(sitemap):
            """Recursively extract page objects from the sitemap that match unwanted URLs or sitemaps.
            The all_pages() iterator also captures pages of sub-sitemaps. Therefore, loop through the sub-sitemaps and dedouble the urls at the end"""

            filter_page_urls = []

            if any(word in sitemap.url.lower() for word in SITEMAP_FILTER_KEYWORDS):
                filter_page_urls.extend(
                    [page.url for page in sitemap.all_pages()]
                )
            else:
                filter_page_urls.extend(
                    [page.url for page in sitemap.all_pages() if any(word in page.url.lower() for word in URL_FILTER_KEYWORDS)]
                )
            
            # Sitemaps can contain sub_sitemaps. Recursively extract URLs from sub-sitemaps
            for sub_sitemap in getattr(sitemap, 'sub_sitemaps', []):
                filter_page_urls.extend(filter_out_pages(sub_sitemap))
            
            return filter_page_urls

        # Remove potential duplicate filtered pages
        urls_dedoubled = set(filter_out_pages(self.sitemap_tree))
        url_list = list(urls_dedoubled)

        return url_list
    
    
    def scrape_domain(self):
        '''Populate self.pages with Page objects of url & last modified date for filtered pages & populate self.filtered_out_urls list with all other urls'''
        self.scrape_sitemap()
        all_pages = [page for page in self.sitemap_tree.all_pages()]
        all_pages_dedoubled = list(set(all_pages)) # Remove duplicates and reset type to list for list comprehension

        self.filtered_out_urls = self.get_filter_urls()
        filter_urls_set = set(self.filtered_out_urls) # Convert list of urls to set for faster membership checking

        filtered_page_list = [
            Page(
                p.url, 
                getattr(p.last_modified, "isoformat", lambda: None)() #Fallback to None in case sitemaps do not capture last modified dates
            ) 
            for p in all_pages_dedoubled
            if p.url not in filter_urls_set
        ]

        self.pages.add_list(filtered_page_list)

        
    def scrape(self) -> tuple[Pages,list]:
        if is_valid_url(self.homepage):
            print(f"Retrieving sitemaps of {self.homepage} in order to fetch all webpages")
            self.scrape_domain()

            return self.pages, self.filtered_out_urls
        else:
            print(f"{self.homepage} is not a valid url")
            print("Please enter the homepage url for the domain you intend to scrape, e.g. <https://example.com>")