class AllExceptions(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"recipe-site-scraper exception: {self.message}"


class InvalidURLException(AllExceptions):
    """
    Util: Provided string is not a URL
    """
    pass

class StripURLToHomepageException(AllExceptions):
    """
    Util: Provided string cannot be stripped to a homepage URL format
    """
    pass

class ExtractDomainException(AllExceptions):
    """
    Util: URL domain name cannot be extracted from provided string
    """
    pass

class RobotParserException(AllExceptions):
    """
    Util: The robots.txt file location of the domain URL cannot be determined from provided string
    """
    pass

class SitemapScraperException(AllExceptions):
    """
    Page_scraper: unable to read sitemap of given website
    """
    def __init__(self, url, stripped_url, exception):
        message = f"Unable to read sitemap for URL {url}\n"
        + "Please check if a sitemap is available in one of the following locations:\n"
        + f"{stripped_url}robots.txt\n"
        + f"{stripped_url}sitemap.xml\n"
        + f"{stripped_url}sitemap-index.xml"
        + "---\n"
        + f"Exception: {exception}"
        super().__init__(message)

class InputException(AllExceptions):
    """
    Init: the provided input_dict or input_file do not meet the expected format
    """
    pass


    
