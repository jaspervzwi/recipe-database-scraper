import re
from publicsuffix2 import get_sld, get_tld
from urllib.parse import urlparse, urlunparse
import urllib.robotparser
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
        raise InvalidURLException("Unable to parse URL {}: {}".format(url, ex))
    
    assert parsed_url.scheme, "Scheme must be set. Please prefix http:// or https://"
    assert parsed_url.scheme.lower() in ['http', 'https'], "Scheme must be http:// or https://"
    assert parsed_url.netloc, f"Cannot determine domain name from {url}"
    
    regex_url = re.compile(
        r'^(https?|ftp):\/\/'           # http, https, ftp protocols
        r'(\w+(\-\w+)*\.)+[a-z]{2,}'    # domain name (example.com, etc.)
        r'(\/[\w\-]*)*'                 # optional path (e.g. /something)
        r'(\?\S*)?'                     # optional query parameters
        r'(#\S*)?$',                    # optional fragment
        re.IGNORECASE
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
    domain = parsed_url.netloc
    full_domain = get_sld(domain)
    tld = get_tld(domain)
    if full_domain and tld:
        main_domain = full_domain.replace(f".{tld}", "")
        return main_domain.split('.')[-1]  # Get the last part (SLD) without subdomains
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
        '/',  # path
        '',  # params
        '',  # query
        '',  # fragment
    )
    url = urlunparse(parsed_url)

    return url

def robot_parser(url: str) -> object:
    """
    Check robots.txt file for allowed/disallowed pages to crawl & crawl conditions

    :param url: URL to check for, e.g. "http://www.example.com/page.html".
    :return: robot parser object
    """

    stripped_domain_url = strip_url_to_homepage(url)
    try:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(stripped_domain_url)
        rp.read()
    except:
        raise RobotParserException(f"Cannot find robots.txt file for {url}\nPlease check if {stripped_domain_url}/robots.txt exists")

    return rp


class FileHandler():
    """
    Handle opening & writing of files
    """
    def __init__(self, filename):
        self.filename = filename

    def load_json_file(self):
        with open(self.filename) as my_file:
            data = my_file.read()

        content = json.loads(data)
        return content
    
    def write_json_file(self, data):
        with open(self.filename, 'w') as my_file:
            json.dump(data, my_file)