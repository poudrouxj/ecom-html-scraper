import json
import requests
from bs4 import BeautifulSoup as bs
from time import sleep
from datetime import date
from random import randint
import re
import os


"""
E-commerce grocery store scraper:

Assumptions:
[1] Its possible to navigate to a 'search on all existing products' page  within the e-commerce site
[2] Within the 'all products search result' page a typical JSS pageination can be leveraged in returning the final page
number 
[3] Particular product TAGs are defined for the e-commerce within a configuration file


How to:
[1] run script 'python main.py --config_file TARGET.json


Author: Jean-Michael Poudroux
Date 2020-08-12
"""


class HTMLScraper:
    def __init__(self, **kwargs):

        # Default SYSTEM initialization
        self.TARGET = None
        self.START_URL = None
        self.SEARCH_URL = None
        self.MAXIMUM_PAGE_NUMBERS = None
        self.PRODUCT_CATEGORY_TAGS = None
        self.PRODUCT_TAGS = None
        self.PAGINATION_TAGS = None

        # Default SCRAPER initialization
        self.LIMIT_NUMBER_OF_REQUESTS = True
        self.MAX_REQUESTS_PER_SESSION = 5
        self.BACKEND_SCRAPER = 'html.parser'
        self.TIME_BETWEEN_REQUESTS = [2, 9]
        self.REQUEST_HEADER = None

        # Default DATA initialization
        self.PRODUCT_CATEGORY = []
        self.PRODUCT_CATEGORY_COUNT = []
        self.PRODUCT_SCHEMA = None
        self.PRODUCT_NAME = []
        self.PRODUCT_UNIT_PRICE = []
        self.PRODUCT_LABEL_PRICE = []


        # kwargs initialization
        self.__dict__.update(**kwargs)


    def get_number_of_seconds_between_request(self):
        """Generate a random number of seconds in a given range to stall request calls to server."""
        return randint(self.TIME_BETWEEN_REQUESTS[0],
                       self.TIME_BETWEEN_REQUESTS[1])

    def get_url_product_search_page_number(self, page_number: str):
        """Create the url for the next page to be scraped."""
        url_page = self.SEARCH_URL + '&page=' + page_number
        return url_page

    def get_last_page_number(self, soup: bs):
        """Find pagination part of a beautifulsoup object and return the last page number in string format."""
        result = soup.find_all(**self.PAGINATION_TAGS)[0].text.split()

        try:
            assert(len(result) != 0)
        except:
            raise AssertionError('Unexpected result when attempting to find the last page number')

        # Clean the scrape and identify the highest number within the pagination, thus suggesting the last page number
        result_cleaned = [x for x in result if x.isdigit()]
        last_page_number = max(result_cleaned)

        self.MAXIMUM_PAGE_NUMBERS = last_page_number

        return last_page_number

    def get_all_product_category_and_count(self, soup :bs):
        """Scrape the first page to get all categories and product counts."""

        category_schema = self.PRODUCT_CATEGORY_TAGS
        result = {}

        for category_type, category_tag in category_schema.items():
            result[category_type] = [x.text for x in soup.find_all(**category_tag)]

        self.PRODUCT_CATEGORY.extend(result['PRODUCT_CATEGORY'])
        self.PRODUCT_CATEGORY_COUNT.extend(result['PRODUCT_CATEGORY_COUNT'])

        return result

    def get_product_data_for_current_page(self, current_soup: bs):
        """Identifies PRODUCT data for the current HTML page. Data is appended to self."""
        product_data = self.PRODUCT_TAGS
        result = {}

        def remove_multiple_spaces(mystr: list):
            """Remove occurences of multiple spaces within a given string."""
            return [re.sub(' +', ' ', x.text.replace('\n',' ')).lstrip().rstrip() for x in mystr]

        for field, product in product_data.items():
            result[field] = remove_multiple_spaces(current_soup.find_all(**product))

        # update object with data points
        self.PRODUCT_NAME.extend(result['PRODUCT_NAME'])
        self.PRODUCT_LABEL_PRICE.extend(result['PRODUCT_LABEL_PRICE'])
        self.PRODUCT_UNIT_PRICE.extend(result['PRODUCT_UNIT_PRICE'])

        return result

    def get_product_category_data(self):
        """Return a dict with product category data."""
        category_data = {}
        category_data['PRODUCT_CATEGORY'] = self.PRODUCT_CATEGORY
        category_data['PRODUCT_CATEGORY_COUNT'] = self.PRODUCT_CATEGORY_COUNT

        return category_data

    def get_product_data(self):
        """Return a dict with all product data."""
        product_data = {}
        product_data['PRODUCT_NAME'] = self.PRODUCT_NAME
        product_data['PRODUCT_LABEL_PRICE'] = self.PRODUCT_LABEL_PRICE
        product_data['PRODUCT_UNIT_PRICE'] = self.PRODUCT_UNIT_PRICE

        return product_data

    def calculate_number_of_scraped_datapoints(self):
        """Return tuple containing the scraped category and product datapoints."""

        products = self.get_product_data()
        categories = self.get_product_category_data()

        return sum(len(x) for x in products.values()), sum(len(y) for y in categories.values())

    def dump_data_scrape_to_json(self, output='data/'):
        """Dump all data to json file"""

        product = self.get_product_data()
        category = self.get_product_category_data()

        data = {**product, **category}
        ts = date.today().strftime('%Y-%m-%d')

        # Get proper directory path
        path = os.path.dirname(__file__) + '/' + output

        data['timestamp'] = [ts]
        data['LIMITED_SCRAPE'] = [(1 == self.LIMIT_NUMBER_OF_REQUESTS)]
        filename = ts + '_products_'+  self.TARGET +'.json'
        filename_with_path= path + filename
        try:

            if os.path.exists(filename_with_path):
                print(f"File {filename} already exists, deleting..")
                os.remove(filename_with_path)
                print(f"File {filename} deleted.")

            with open(filename_with_path, 'w', encoding='utf-8') as outfile:
                json.dump(data, outfile, ensure_ascii=False, indent=4)

            if os.path.exists(filename_with_path):
                print(f"File {filename} has been created")
        except:
            print("Could not dump data to file..")


def run_scraper(args):

    print('-------------------------')
    print('Initializing HTML Scraper')
    HS = HTMLScraper(**args)
    print('Scraper OBJECT initaliazed')
    print('-------------------------')

    print('Attempting to scrape: ', HS.START_URL)


    # 1 generate request
    try:
        r = requests.get(HS.SEARCH_URL,
                         HS.REQUEST_HEADER)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    # 2 Setup BS4 object
    soup = bs(r.text, HS.BACKEND_SCRAPER)

    # 3 Identify categories
    HS.get_all_product_category_and_count(soup)

    number_of_categories = len(HS.PRODUCT_CATEGORY)

    #TODO: product item category count is not a unique count as not all categories are unique
    number_of_products = sum([int(x) for x in HS.PRODUCT_CATEGORY_COUNT])

    print(f'Scraped first page and identified {number_of_categories} number of product categories')

    # 4 identify maximum number of pages, this will be equal to the number of requests if its not limited

    if HS.LIMIT_NUMBER_OF_REQUESTS:
        last_page_number = HS.MAX_REQUESTS_PER_SESSION
        print('-------------------------')
        print(f"INFO: Scraping is limited to {last_page_number} request calls.")
        print('-------------------------')

    else:
        last_page_number = int(HS.get_last_page_number(soup))
        print('-------------------------')
        print(f"INFO: Scraping is not limited, will attempt to run all {last_page_number} requests")
        print('-------------------------')

    current_page = 1
    # 5 Get product data

    HS.get_product_data_for_current_page(soup)

    second_page = current_page + 1

    print("First page scrape complete!")
    print(f"Attempting to scrape remaining {last_page_number} pages")
    for page in range(second_page, last_page_number+1):

        # Perform a sleep to reduce load on server side
        sleep(HS.get_number_of_seconds_between_request())

        # Create the next URL
        next_url = HS.get_url_product_search_page_number(str(page))

        # Attempt to run a GET and update HS object with new data
        try:
            r = requests.get(next_url,
                             HS.REQUEST_HEADER)
            r.raise_for_status()

            # parse the request object
            soup = bs(r.text, HS.BACKEND_SCRAPER)

            # update HS object with new data
            HS.get_product_data_for_current_page(soup)

            print(f"Page {page}  / {last_page_number} successfully scraped")

        except requests.exceptions.HTTPError as err:
            print(f"Something went wrong in the scraping, status_code : {r.status_code} ")
            continue

    # 5 dump data to json files
    HS.dump_data_scrape_to_json()

    print('-------------------------')
    print(f"Scrape completed!")
    print('-------------------------')
    n_scraped_category_datapoints, n_scraped_product_item_datapoints = HS.calculate_number_of_scraped_datapoints()
    print(f"Retrieved {n_scraped_category_datapoints} number of category datapoints")
    print(f"Retrieved {n_scraped_product_item_datapoints} number of product datapoints")
