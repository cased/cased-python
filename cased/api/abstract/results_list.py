import re
import urllib.parse as urlparse
from urllib.parse import parse_qs


class ResultsList:
    def __init__(self, response, resource):
        self._response = response
        self.headers = response.headers
        self.json_response = response.json()
        self.resource = resource

    @property
    def link_header(self):
        return self.headers.get("Link")

    @property
    def links(self):
        if not self.link_header:
            return {}

        link_dict = {}
        each_link = self.link_header.split(", ")
        for link in each_link:
            url, name = re.match(r'<(.*?)>; rel="(\w+)"', link).groups()
            link_dict[name] = url

        return link_dict

    @property
    def results(self):
        return self.json_response.get("results")

    @property
    def total_count(self):
        return self.json_response.get("total_count")

    @property
    def total_pages(self):
        return self.json_response.get("total_pages")

    @property
    def first_page_url(self):
        return self.links.get("first")

    @property
    def first_page(self):
        return self.page_from("first")

    @property
    def last_page_url(self):
        return self.links.get("last")

    @property
    def last_page(self):
        return self.page_from("last")

    @property
    def next_page_url(self):
        return self.links.get("next")

    @property
    def next_page(self):
        return self.page_from("next")

    def fetch_next(self):
        page = self.next_page
        return self.resource.list(page=page)

    @property
    def prev_page_url(self):
        return self.links.get("prev")

    @property
    def prev_page(self):
        return self.page_from("prev")

    def page_from(self, rel):
        url = self.links.get(rel)
        parsed = urlparse.urlparse(url)
        query_params = parse_qs(parsed.query)

        page_number = query_params.get("page")
        if page_number:
            number = page_number[0]
            return int(number)
        else:
            return None

    def page_iter(self):
        page = self

        while True:
            page = page.fetch_next()
            yield page.results

            if not page.has_more:
                break

    def has_more(self):
        if self.next_page_url:
            return True
        else:
            return False

    def __len__(self):
        return getattr(self, "result", []).__len__()
