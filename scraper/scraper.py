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


def setup():
    logging.basicConfig(filename=LOG_PATH, level=logging.ERROR)
    options = Options()
    options.add_argument('--headless')
    result = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)
    logging.info("Setup complete.")
    return result

def get_hypertext(driver):
    driver.get(URL)
    result = driver.page_source
    logging.info("Get Hypertext complete.")
    return result

def get_table_with_data(html):
    soup = BeautifulSoup(html, features="html.parser")
    result = soup.find('tbody').findChildren('tr')  # if the table has changed, AttributeError
    logging.info("Get Table With Data complete.")
    return result

def row_not_loaded(row):
    logging.info("Row Not Loaded being assessed.")
    if row.has_attr('class'):  # by inspection
        return True
    return False

def scroll_down_page(driver):
    driver.execute_script("window.scrollBy(0, document.documentElement.clientHeight);")
    time.sleep(0.5)
    logging.info("Scroll Down Page complete.")

def reload_table_rows(driver):
    html = driver.page_source
    result = get_table_with_data(html)
    logging.info("Reload Table Rows complete.")
    return result

def get_coin_name(columns):
    try:
        column = columns[2].findChildren('p')
        result = column[0].text
        logging.info("Get Coin Name complete.")
    except IndexError:
        logging.error("Could not parse Name.")
        result = None
    return result

def get_coin_symbol(columns):
    try:
        column = columns[2].findChildren('p')
        result = column[1].text
        logging.info("Get Coin Symbol complete.")
    except IndexError:
        logging.error("Could not parse Symbol.")
        result = None
    return result

def get_coin_price(columns):
    try:
        column = columns[3].find('a')
        price = column.text
        price = re.sub(r"[$|,]","",price)  # strip the '$' symbol and ',' symbols
        result = float(price)
        logging.info("Get Coin Price complete.")
    except (ValueError, IndexError, AttributeError):
        logging.error("Could not parse Coin Price.")
        result = None
    return result

def get_coin_change24h(columns):
    try:
        column = columns[4]
        change24h_sign = 1 if "up" in column.find('span').find('span')['class'][0] else -1
        change24h = column.text
        change24h = re.sub(r"[%]","",change24h)  # strip '%' symbol
        change24h = float(change24h)
        result = change24h_sign * change24h
        logging.info("Get Coin Change24h complete.")
    except (ValueError, IndexError, AttributeError):
        logging.error("Could not parse Coin 24h %.")
        result = None
    return result

def get_coin_change7d(columns):
    try:
        column = columns[5]
        change7d_sign = 1 if "up" in column.find('span').find('span')['class'][0] else -1
        change7d = column.text
        change7d = re.sub(r"[%]","",change7d)  # strip '%' symbol
        change7d = float(change7d)
        result = change7d_sign * change7d
        logging.info("Get Coin Change7d complete.")
    except (ValueError, IndexError, AttributeError):
        logging.error("Could not parse Coin 7d %.")
        result = None
    return result

def get_coin_market_cap(columns):
    try:
        column = columns[6].findChildren('span')
        market_cap = column[-1].text
        market_cap = re.sub(r"[$|,]","",market_cap)  # strip '$' symbol and ',' symbols
        result = int(market_cap)
        logging.info("Get Coin Market Cap complete.")
    except (ValueError, IndexError):
        logging.error("Could not parse Coin Market Cap.")
        result = None
    return result

def get_coin_volume24h(columns):
    try:
        column = columns[7].find('a').find('p')
        volume24h = column.text
        volume24h = re.sub(r"[$|,]","",volume24h)  # strip '$' symbol and ',' symbols
        result = int(volume24h)
        logging.info("Get Coin Volume24h complete.")
    except (ValueError, IndexError, AttributeError):
        logging.error("Could not parse Coin Volume (24h).")
        result = None
    return result

def get_coin_circulating_supply(columns):
    try:
        column = columns[8].find('p')
        circulating_supply = column.text
        circulating_supply = re.sub(r'[A-Z|\s|,]','',circulating_supply)  # strip ',' symbols, whitespace and coin symbol
        result = int(circulating_supply)
        logging.info("Get Coin Circulating Supply complete.")
    except (ValueError, IndexError, AttributeError):
        logging.error("Could not cast Circulating Supply.")
        result = None
    return result

def write_to_csv(coin_datums):
    path = os.path.abspath(str(datetime.now()) + OUTPUT_CSV_FILENAME)
    columns = coin_datums[0].keys()
    with open(path, 'a') as f:
        f.write(','.join(columns))
        f.write("\n")
        for coin_data in coin_datums:
            line = [str(coin_data[x]) for x in coin_data.keys()]
            line = ','.join(line)
            f.write(line)
            f.write("\n")
    logging.info("Write To CSV complete.")

def get_top_n_coin_data(table_rows, driver):
    if len(table_rows) < TOP_N:
        error = "This scraper cannot scrape that many (" + str(TOP_N) + ") records. Exiting."
        print(error)
        logging.error(error)
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
        coin_data["price"] = get_coin_price(columns)
        coin_data["change24h"] = get_coin_change24h(columns)
        coin_data["change7d"] = get_coin_change7d(columns)
        coin_data["market_cap"] = get_coin_market_cap(columns)
        coin_data["volume24h"] = get_coin_volume24h(columns)
        coin_data["circulating_supply"] = get_coin_circulating_supply(columns)
        result.append(coin_data)
    
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
        logging.error("Could not parse table containing data. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    print("Starting...")
    main()
    print("Done.")
