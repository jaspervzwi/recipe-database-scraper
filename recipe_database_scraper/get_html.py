import requests
import time
from http import HTTPStatus
from requests.exceptions import RequestException

RETRYABLE_HTTP_STATUS_CODES = {

    # Some servers return "400 Bad Request" initially but upon retry start working again, no idea why
    int(HTTPStatus.BAD_REQUEST),

    # If we timed out requesting stuff, we can just try again
    int(HTTPStatus.REQUEST_TIMEOUT),

    # If we got rate limited, it makes sense to wait a bit
    int(HTTPStatus.TOO_MANY_REQUESTS),

    # Server might be just fine on a subsequent attempt
    int(HTTPStatus.INTERNAL_SERVER_ERROR),

    # Upstream might reappear on a retry
    int(HTTPStatus.BAD_GATEWAY),

    # Service might become available again on a retry
    int(HTTPStatus.SERVICE_UNAVAILABLE),

    # Upstream might reappear on a retry
    int(HTTPStatus.GATEWAY_TIMEOUT),

    # (unofficial) 509 Bandwidth Limit Exceeded (Apache Web Server/cPanel)
    509,

    # (unofficial) 598 Network read timeout error
    598,

    # (unofficial, nginx) 499 Client Closed Request
    499,

    # (unofficial, Cloudflare) 520 Unknown Error
    520,

    # (unofficial, Cloudflare) 521 Web Server Is Down
    521,

    # (unofficial, Cloudflare) 522 Connection Timed Out
    522,

    # (unofficial, Cloudflare) 523 Origin Is Unreachable
    523,

    # (unofficial, Cloudflare) 524 A Timeout Occurred
    524,

    # (unofficial, Cloudflare) 525 SSL Handshake Failed
    525,

    # (unofficial, Cloudflare) 526 Invalid SSL Certificate
    526,

    # (unofficial, Cloudflare) 527 Railgun Error
    527,

    # (unofficial, Cloudflare) 530 Origin DNS Error
    530

}
"""HTTP status codes on which a request should be retried."""


class HTMLScraper:
    def __init__(self, max_retries=3, backoff_factor=1):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.user_agent = None

    def _get_headers(self):
        return {
            'User-Agent': self.user_agent
        }

    def _fetch_with_retry(self, url):
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                response = requests.get(url, headers=self._get_headers())

                if response.status_code == 200:
                    return response
                elif response.status_code in RETRYABLE_HTTP_STATUS_CODES:
                    retry_count += 1
                    wait_time = self.backoff_factor * (2 ** retry_count)
                    print(f"Status code {response.status_code} received for URL: '{url}'. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"Error: Status code {response.status_code} received for URL: {url}")
                    return None
            except RequestException as e:
                retry_count += 1
                wait_time = self.backoff_factor * (2 ** retry_count)
                print(f"URL '{url}' encountered exception: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        # If we exceed max retries, return None or raise an exception
        print(f"Max retries exceeded for URL: {url}")
        return None

    def scrape_page(self, url: str, user_agent: str):
        self.user_agent = user_agent
        response = self._fetch_with_retry(url)
        if response:
            return response.content
        else:
            print(f"Failed to fetch: {url}")
            return None