# E-commerce web-scraper


## Description
Assumptions:
* The website to be scraped contains an search all item page with a pagination 
highlighting the last page number available
* The website has not encrypted the CSS data and contains searchable keywords for scraping

## Local Execution
To execute the locally scraper one can run the following command:
```bash
python main.py --config_file target.json
```
The scraper will first identify some product category data, then the number of pages to be scraped containing 
product data. Once the scraping is complete it will dump the data to `../data/`  directory. 

```bash
|-- scraper
|   |-- __init__.py
|   |-- data
|   |   `-- 2020-08-13_products_target.json
|   `-- run.py
|-- README.MD
|-- TARGET.json
|-- main.py
|-- requirements.txt
`-- setup.py
```


### Performance
* To increase performance we can do asynchrounous requests (maybe use `grequest` f.i.)
* To increase performance we can change backend engine on beautifulsoup4 from `html.parser` to `lxml` 
[stackoverflow-question](https://stackoverflow.com/questions/41047795/python-beautifulsoup-parsing-speed-improvement)
* By designing data integration step outside the scraper we can save some time

### Modularity  & Configurability

The configuration file contains both functional scraper settings (maximum number of requests, time between requests etc)
, but also data target tags. The tags are generic CSS tags, but some keyword may be kolonial specific.
```json5
{
  "REQUEST_HEADER": {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.5.4333.199 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
  },
  "LIMIT_NUMBER_OF_REQUESTS": 1,
  "MAX_REQUESTS_PER_SESSION": 2,
  "BACKEND_SCRAPER": "html.parser",
  "TIME_BETWEEN_REQUESTS": [
    1,
    3
  ],
  "TARGET": "SECRET",
  "START_URL": "https://SECRET.no/",
  "SEARCH_URL": "https://SECRET.no/sok/?q=%27",
  "product_category_tags": "NA",
  "product_tags": "MG",
  "PAGINATION_TAGS": {
    "name": "ul",
    "attrs": {
      "class": "pagination"
    }
  },
  "PRODUCT_SCHEMA": {
    "PRODUCT_NAME": {
      "type": "str",
      "description": "Scraped product name"
    },
    "PRODUCT_LABEL_PRICE": {
      "type": "str",
      "description": "Scraped label price"
    },
    "PRODUCT_UNIT_PRICE": {
      "type": "str",
      "description": "Scraped unit price"
    }
  },
  "PRODUCT_CATEGORY_TAGS": {
    "PRODUCT_CATEGORY": {
      "name": "span",
      "attrs": {
        "class": "category-name"
      }
    },
    "PRODUCT_CATEGORY_COUNT": {
      "name": "span",
      "attrs": {
        "class": "item-count"
      }
    }
  },
  "PRODUCT_TAGS": {
    "PRODUCT_NAME": {
      "name": "h3",
      "attrs": {
        "class": "name"
      }
    },
    "PRODUCT_LABEL_PRICE": {
      "name": "p",
      "attrs": {
        "class": "price label label-price"
      }
    },
    "PRODUCT_UNIT_PRICE": {
      "name": "p",
      "attrs": {
        "class": "unit-price"
      }
    }
  }
}
```
### Good Citizen

Different mechanisms can be implemented to ensure client server side is protected against DDOS o
* Limit number of `get` requests per scrape
* Limit the time between each `get` request
* Limit the scraping depth (don't regex all `href` flags)
* Identify the scraper within the `header`
* Schedule the scraping outside peak hours


## External libraries
* `beautifulsoup` : used for parsing html objects
* `requests : used for generating http requests`
* `re` : used for regex
 

## TODOs
* Product items that (1) have a discount or (2) is unavailable is not currently scraped
* Containerization of the application for ease of deployment to cloud
* Deployment scripts
* Application cli arguments (currently only config file)


