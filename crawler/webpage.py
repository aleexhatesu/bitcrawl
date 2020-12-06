import urllib.parse
import requests

import validators

import link_utils
import parsing
import robots

class Webpage:
    def __init__(self, url):
        self.url = url
        self.response = None
        self.soup = None
        self.links = None
        self.same_site_links = None
        self.content_type = None
        self.charset = None
        self.allowed_by_robots = None

    def __str__(self):
        return str({
            'url': self.url,
            'content_type': self.content_type
        })

    @classmethod
    def fetch(cls, url, **requests_kwargs):
        if not requests_kwargs:
            requests_kwargs = {}
        try:
            return requests.get(url, **requests_kwargs)
        except Exception as e:
            # TODO logging
            raise e

    @classmethod
    def parse_content_type(cls, content_type_header):
        if content_type_header:
            split_content_type = content_type_header.split(";")
            if len(split_content_type) >= 2:
                return split_content_type[:2]
            elif len(split_content_type) == 1:
                content_type = split_content_type[0]
                return content_type, None
        return None, None

    @classmethod
    def _resolve_relative_links(cls, original_url, links):
        links = [
            urllib.parse.urljoin(original_url, link)
            if link_utils.is_relative(link) else link for link in links]
        return links

    @classmethod
    def _remove_cross_site_links(cls, original_url, links):
        same_site_links = []
        for link in links:
            if link_utils.is_same_host(link, original_url):
                same_site_links.append(link)
        return same_site_links


    @classmethod
    def get_same_site_links(cls, original_url, links):
        return cls._remove_cross_site_links(original_url, links)

    @classmethod
    def get_links(cls, url, soup):
        discovered_links = soup.get_links()

        # Append base url to relative links
        base_url = link_utils.get_base_url(url)
        resolved_links = cls._resolve_relative_links(
            base_url, discovered_links)

        # Remove invalid links
        valid_urls = [url for url in resolved_links if validators.url(url)]
        return valid_urls

    def crawl_page(
            self,
            user_agent,
            request_kwargs=None,
            respect_robots=True,
            reppy=None,
            reppy_cache_kwargs=None,
            reppy_robots_kwargs=None):

        if not request_kwargs:
            request_kwargs = {}
        if respect_robots:
            if not reppy:
                reppy = RobotParser(
                    cache_kwargs=reppy_cache_kwargs,
                    request_kwargs=reppy_robots_kwargs)
            self.allowed_by_robots = reppy.allowed_by_robots(self.url)

        # Only False should prevent crawling (None should allow.)
        if self.allowed_by_robots != False:
            self.response = self.fetch(self.url, **request_kwargs)
            if self.response and self.response.ok:
                self.content_type, self.charset = (
                    self.parse_content_type(
                        self.response.headers.get('content-type')))

                if self.content_type == 'text/html':
                    self.soup = parsing.HtmlParser(self.response.text)
                    self.links = self.get_links(self.url, self.soup)
                    self.same_site_links = (
                        self.get_same_site_links(self.url, self.links))
        return self
