import requests
from bs4 import BeautifulSoup
import re


class Scrapper:

    def __init__(self, url, header, logger):
        self.url = url
        self.header = header
        self.logger = logger

    def scrape_data(self, pages_count=0):
        """
        scrape data from amazon pages

        :param pages_count: total pages to extract from amazon site
        :return: list of items
        """
        items = []
        self.logger.info(f'searching url {self.url}')
        soup = self.get_soup(self.url)
        self.logger.info('Soup Object created')

        # total pages count
        try:
            page_number = int(soup.find("span", class_='s-pagination-strip').contents[-2].text)
        except AttributeError:
            self.logger.warn("Pagination not available")
            page_number = 1
        self.logger.info(f'{page_number} pages found for keyword')

        page_number = pages_count if pages_count < page_number and pages_count > 0 else page_number

        data = soup.find_all("div", attrs={'class': "a-section a-spacing-base"})
        # global data
        in_count = 1
        self.logger.info(f'executing scrapper on {page_number} pages')
        while in_count <= page_number:
            if in_count != 1:
                page_url = self.url + f'&page={in_count}'
                soup = self.get_soup(page_url)
                data = soup.find_all("div", attrs={'class': "a-section a-spacing-base"})
            items.extend(self.scrape_info_from_page(data))
            in_count += 1

        return items

    def get_soup(self, s_url):
        """
        gets the page element of given url and returns the soup object of ut
        :param s_url: query url
        :return: soup object of url
        """

        try:
            # HTTP Request
            self.logger.info(f'scrapping data from {s_url}')
            webpage = requests.get(s_url, headers=self.header)

            # Soup Object containing all data
            return BeautifulSoup(webpage.content, "html.parser")
        except Exception:
            self.logger.error('Unable to create soup object')

    def scrape_value_from_product(self, f_value, **mapping):
        """
        scrape text using soup object

        :param f_value: beautiful soup search object string
        :param mapping: soup elements obj mapping

        :return: extracted element if element not extracted returns empty string
        """
        try:
            item = eval(f_value, mapping)
            return item
        except Exception as e:
            self.logger.error(f'Error occurs while scrapping items {e}')
            return ""

    def scrape_info_from_page(self, amz_products):
        """
        Method tries to scrap possible data from page data and
        returns the json object contains all extracted data

        :param amz_products:
        :return: list of available products
        """
        page_data = []

        # iterating over all found elements
        for product in amz_products:
            # Defined a dic object to store all scraped values
            json_data = {
                'item_description': self.scrape_value_from_product(r'product.find("h2").text', product=product),
                'item_ratings': self.scrape_value_from_product(
                    r'product.select_one(s_string)["aria-label"]', product=product,
                    s_string="span[aria-label$='5 stars']"),
                'review_count': self.scrape_value_from_product(
                    r"product.select_one(s_string).nextSibling['aria-label']",
                    product=product, s_string="span[aria-label$='5 stars']"),
                'item_price': self.scrape_value_from_product(
                    r'product.find("span", class_="a-price").next.text', product=product),
                'per_qty': self.scrape_value_from_product(
                    r'product.find(class_="a-price").parent.contents[2].text', product=product),
                'discount_offer': re.sub(r"[\(|\)]", "", self.scrape_value_from_product(
                    r'product.find(class_="a-price").parent.parent.contents[3].text', product=product))
            }

            page_data.append(json_data)

        return page_data
