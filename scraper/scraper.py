"""
filename: scraper.py
author: Alexander DeForge
date: 05/24/2021
purpose: Scrape the website coinmarketcap.com for top N cryptocurrencies and some of their properties at the time.
  Due to the nature of web scraping, websites may change without notice, affecting the ability of a scraper to scrape.
  This scraper 'fails open' meaning it will record values it cannot parse as 'None' and continue on with the parsing.
"""

import sys
import os
import time
import re
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


CHROMEDRIVER_PATH = os.path.abspath('chromedriver')
LOG_PATH = os.path.abspath('logs/scraper.log')
URL = "https://coinmarketcap.com/"
TOP_N = 100
OUTPUT_CSV_FILENAME = "scraper.csv"
LOGGER_NAME = "scraper_app"


def setup():
    """Performs setup tasks for the program.

    Creates and configures a logger, creates and configures
    a webdriver.

    Returns:
        A Chromium based Selenium webdriver.
    """
    global logger
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler(LOG_PATH, mode='a')
    handler.setFormatter(formatter)
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    options = Options()
    options.add_argument('--headless')
    result = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)
    logger.debug("Setup complete.")
    return result

def get_hypertext(driver):
    """Retrieves hypertext from a URL.

    Performs a GET request on the URL "https://coinmarketcap.com"
    and extracts the hypertext (page source).

    Args:
        driver: a Selenium webdriver.

    Returns:
        A string variable containing hypertext (page source).
    """
    driver.get(URL)
    result = driver.page_source
    logger.debug("Get Hypertext complete.")
    return result

def get_table_with_data(html):
    """Isolates table with desired data.

    Given the hypertext of the target URL, there is a table which
    contains the data we want to scrape. This function isolates that
    table for further parsing.

    Args:
        html: the hypertext retrieved via GET request from the URL.

    Returns:
        A BeautifulSoup Tag object containing the table of interest.

    Raises:
        AttributeError: if the webpage has changed, the table might not be parsable.
    """
    soup = BeautifulSoup(html, features="html.parser")
    result = soup.find('tbody').findChildren('tr')
    logger.debug("Get Table With Data complete.")
    return result

def row_not_loaded(row):
    """Checks to see if a row has loaded.

    Some of the content at the URL is dynamically loaded. In order to
    scrape a row's contents, the row must have loaded. This function
    checks for that.

    Args:
        row: a BeautifulSoup Tag object.

    Returns:
        This function returns True if the row has NOT loaded and False
        if the row has loaded.
    """
    logger.debug("Row Not Loaded being assessed.")
    if row.has_attr('class'):
        return True
    return False

def scroll_down_page(driver):
    """Instructs the Webdriver to scroll down.

    Instructs the Webdriver to scoll down the height of the client 
    via injecting a JavaScript command. After the command is injected
    and executed, the function sleeps for half a second.

    Args:
        driver: a Selenium webdriver.
    """
    driver.execute_script("window.scrollBy(0, document.documentElement.clientHeight);")
    time.sleep(0.5)
    logger.debug("Scroll Down Page complete.")

def reload_table_rows(driver):
    """Reloads the table of data's rows.

    The hypertext retrieved from the URL updates dynamically within
    the webdriver. When this occurs, the table of data needs to 
    be retrieved again -- now with populated data.

    Args:
        driver: a Selenium webdriver.

    Returns:
        A BeautifulSoup Tag object containing the table of interest.

    Raises:
        AttributeError: if get_table_with_data raises it.
    """
    html = driver.page_source
    result = get_table_with_data(html)
    logger.debug("Reload Table Rows complete.")
    return result

def get_coin_name(columns):
    """Parses coin name.

    Parses coin name given a BeautifulSoup Tag object.

    Args:
        columns: BeautifulSoup Tag object containing columns for
        row of interest.

    Returns:
        A string containing the name of the coin for that row
        or None if parsing fails.
    """
    try:
        column = columns[2].findChildren('p')
        result = column[0].text
        logger.debug("Get Coin Name complete.")
    except IndexError:
        logger.error("Could not parse Name.")
        result = None
    return result

def get_coin_symbol(columns):
    """Parses coin symbol.

    Parses coin symbol given a BeautifulSoup Tag object.

    Args:
        columns: BeautifulSoup Tag object containing columns for
        row of interest.

    Returns:
        A string containing the symbol for the coin for that row
        or None if parsing fails.
    """
    try:
        column = columns[2].findChildren('p')
        result = column[1].text
        logger.debug("Get Coin Symbol complete.")
    except IndexError:
        logger.error("Could not parse Symbol.")
        result = None
    return result

def get_coin_price(columns):
    """Parses coin price.

    Parses coin price given a BeautifulSoup Tag object.

    Args:
        columns: BeautifulSoup Tag object containing columns for
        row of interest.

    Returns:
        A float containing the price for the coin for that row
        or None if parsing fails.
    """
    try:
        column = columns[3].find('a')
        price = column.text
        price = re.sub(r"[$|,]","",price)  # strip the '$' symbol and ',' symbols
        result = float(price)
        logger.debug("Get Coin Price complete.")
    except (ValueError, IndexError, AttributeError):
        logger.error("Could not parse Coin Price.")
        result = None
    return result

def get_coin_change24h(columns):
    """Parses coin 24h %.

    Parses coin 24h % given a BeautifulSoup Tag object.

    Args:
        columns: BeautifulSoup Tag object containing columns for
        row of interest.

    Returns:
        A float containing the 24h % for the coin for that row
        or None if parsing fails.
    """
    try:
        column = columns[4]
        change24h_sign = 1 if "up" in column.find('span').find('span')['class'][0] else -1
        change24h = column.text
        change24h = re.sub(r"[%]","",change24h)  # strip '%' symbol
        change24h = float(change24h)
        result = change24h_sign * change24h
        logger.debug("Get Coin Change24h complete.")
    except (ValueError, IndexError, AttributeError):
        logger.error("Could not parse Coin 24h %.")
        result = None
    return result

def get_coin_change7d(columns):
    """Parses coin 7d %.

    Parses coin 7d % given a BeautifulSoup Tag object.

    Args:
        columns: BeautifulSoup Tag object containing columns for
        row of interest.

    Returns:
        A float containing the 7d % of the coin for that row
        or None if parsing fails.
    """
    try:
        column = columns[5]
        change7d_sign = 1 if "up" in column.find('span').find('span')['class'][0] else -1
        change7d = column.text
        change7d = re.sub(r"[%]","",change7d)  # strip '%' symbol
        change7d = float(change7d)
        result = change7d_sign * change7d
        logger.debug("Get Coin Change7d complete.")
    except (ValueError, IndexError, AttributeError):
        logger.error("Could not parse Coin 7d %.")
        result = None
    return result

def get_coin_market_cap(columns):
    """Parses coin market cap.

    Parses coin market cap given a BeautifulSoup Tag object.

    Args:
        columns: BeautifulSoup Tag object containing columns for
        row of interest.

    Returns:
        An int containing the market cap for the coin for that row
        or None if parsing fails.
    """
    try:
        column = columns[6].findChildren('span')
        market_cap = column[-1].text
        market_cap = re.sub(r"[$|,]","",market_cap)  # strip '$' symbol and ',' symbols
        result = int(market_cap)
        logger.debug("Get Coin Market Cap complete.")
    except (ValueError, IndexError):
        logger.error("Could not parse Coin Market Cap.")
        result = None
    return result

def get_coin_volume24h(columns):
    """Parses coin Volume(24h).

    Parses coin Volume(24h) given a BeautifulSoup Tag object.

    Args:
        columns: BeautifulSoup Tag object containing columns for
        row of interest.

    Returns:
        An int containing the Volume(24h) for the coin for that row
        or None if parsing fails.
    """
    try:
        column = columns[7].find('a').find('p')
        volume24h = column.text
        volume24h = re.sub(r"[$|,]","",volume24h)  # strip '$' symbol and ',' symbols
        result = int(volume24h)
        logger.debug("Get Coin Volume24h complete.")
    except (ValueError, IndexError, AttributeError):
        logger.error("Could not parse Coin Volume (24h).")
        result = None
    return result

def get_coin_circulating_supply(columns):
    """Parses coin circulating supply.

    Parses coin circulating supply given a BeautifulSoup Tag object.

    Args:
        columns: BeautifulSoup Tag object containing columns for
        row of interest.

    Returns:
        An int containing the circulating supply for the coin for that row
        or None if parsing fails.
    """
    try:
        column = columns[8].find('p')
        circulating_supply = column.text
        circulating_supply = re.sub(r'[A-Z|\s|,]','',circulating_supply)  # strip ',' symbols, whitespace and coin symbol
        result = int(circulating_supply)
        logger.debug("Get Coin Circulating Supply complete.")
    except (ValueError, IndexError, AttributeError):
        logger.error("Could not cast Circulating Supply.")
        result = None
    return result

def write_to_csv(coin_datums):
    """Writes data to csv file.

    Writes the data collected to a csv file. The columns are:
    name, symbol, price(USD), change24h, change7d, market_cap(USD),
    volume24h(USD), circulating_supply.

    Args:
        coin_datums: list of dictionaries. Each dictionary contains
        the data for each coin.
    """
    path = os.path.abspath(str(datetime.now()) + "_" + OUTPUT_CSV_FILENAME)
    columns = coin_datums[0].keys()
    with open(path, 'a') as f:
        f.write(','.join(columns))
        f.write("\n")
        for coin_data in coin_datums:
            line = [str(coin_data[x]) for x in coin_data.keys()]
            line = ','.join(line)
            f.write(line)
            f.write("\n")
    logger.debug("Write To CSV complete.")

def get_top_n_coin_data(table_rows, driver):
    """Retrieves data for TOP_N cryptocurrency.

    Iterates over a table of data, row by row, where
    each row is parsed for specific information.

    Args:
        table_rows: a BeautifulSoup Tag object containing the
        hypertext for the table containing coin data.
        driver: a Selenium webdriver.

    Returns:
        A list of dictionaries where each dictionary
        contains data related to a single coin.
    """
    if len(table_rows) < TOP_N:
        error = "This scraper cannot scrape that many (" + str(TOP_N) + ") records. Exiting."
        print(error)
        logger.error(error)
        sys.exit(1)

    result = []
    for index in range(TOP_N):

        if row_not_loaded(table_rows[index]):
            scroll_down_page(driver)
            table_rows = reload_table_rows(driver)  # maybe AttributeError
        
        columns = table_rows[index].findChildren('td')  # maybe AttributeError, IndexError

        coin_data = {}
        coin_data["name"] = get_coin_name(columns)
        coin_data["symbol"] = get_coin_symbol(columns)
        coin_data["price(USD)"] = get_coin_price(columns)
        coin_data["change24h"] = get_coin_change24h(columns)
        coin_data["change7d"] = get_coin_change7d(columns)
        coin_data["market_cap(USD)"] = get_coin_market_cap(columns)
        coin_data["volume24h(USD)"] = get_coin_volume24h(columns)
        coin_data["circulating_supply"] = get_coin_circulating_supply(columns)
        result.append(coin_data)
    logger.debug("Get Top N Coin Data complete.")
    return result

def main():
    driver = setup()
    html = get_hypertext(driver)
    try:
        table_rows = get_table_with_data(html)
        coin_datums = get_top_n_coin_data(table_rows, driver)
        write_to_csv(coin_datums)
        # write_to_db(coin_datums)
    except (AttributeError, IndexError):
        logger.error("Could not parse table containing data. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    print("Starting...")
    main()
    print("Done.")
