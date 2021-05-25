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
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


CHROMEDRIVER_PATH = os.path.abspath('chromedriver')
LOG_PATH = os.path.abspath('logs/scraper.log')
URL = "https://coinmarketcap.com/"
TOP_N = 100

def setup():
    logging.basicConfig(filename=LOG_PATH, level=logging.ERROR)
    options = Options()
    options.add_argument('--headless')
    result = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)
    return result

def get_hypertext(driver):
    driver.get(URL)
    result = driver.page_source
    return result

def get_table_with_data(html):
    soup = BeautifulSoup(html, features="html.parser")
    result = soup.find('tbody').findChildren('tr')
    return result

def row_not_loaded(row):
    if row.has_attr('class'):  # by inspection
        return True
    return False

def scroll_down_page(driver):
    driver.execute_script("window.scrollBy(0, document.documentElement.clientHeight);")
    time.sleep(0.5)

def reload_table_rows(driver):
    html = driver.page_source
    result = get_table_with_data(html)
    return result

def get_coin_name(columns):
    column = columns[2].findChildren('p')
    print(column)
    result = column[0].text
    return result

def get_coin_symbol(columns):
    column = columns[2].findChildren('p')
    result = column[1].text
    return result

def get_coin_price(columns):
    column = columns[3].find('a')
    price = column.text
    price = re.sub(r"[$|,]","",price)  # strip the '$' symbol and ',' symbols
    try:
        result = float(price)
    except ValueError:
        logging.error("Could not cast Coin Price.")
        result = None
    return result

def get_coin_change24h(columns):
    column = columns[4]
    change24h_sign = 1 if "up" in column.find('span').find('span')['class'][0] else -1
    change24h = column.text
    change24h = re.sub(r"[%]","",change24h)  # strip '%' symbol
    try:
        change24h = float(change24h)
        result = change24h_sign * change24h
    except ValueError:
        logging.error("Could not cast 24h %.")
        result = None
    return result

def get_coin_change7d(columns):
    column = columns[5]
    change7d_sign = 1 if "up" in column.find('span').find('span')['class'][0] else -1
    change7d = column.text
    change7d = re.sub(r"[%]","",change7d)  # strip '%' symbol
    try:
        change7d = float(change7d)
        result = change7d_sign * change7d
    except ValueError:
        logging.error("Could not cast 7d %.")
        result = None
    return result

def get_coin_market_cap(columns):
    column = columns[6].findChildren('span')
    market_cap = column[-1].text
    market_cap = re.sub(r"[$|,]","",market_cap)  # strip '$' symbol and ',' symbols
    try:
        result = int(market_cap)
    except ValueError:
        logging.error("Could not cast Market Cap.")
        result = None
    return result

def get_coin_volume24h(columns):
    column = columns[7].find('a').find('p')
    volume24h = column.text
    volume24h = re.sub(r"[$|,]","",volume24h)  # strip '$' symbol and ',' symbols
    try:
        result = int(volume24h)
    except ValueError:
        logging.error("Could not cast Volume (24h).")
        result = None
    return result

def get_coin_circulating_supply(columns):
    column = columns[8].find('p')
    circulating_supply = column.text
    circulating_supply = re.sub(r'[A-Z|\s|,]','',circulating_supply)  # strip ',' symbols, whitespace and coin symbol
    try:
        result = int(circulating_supply)
    except ValueError:
        logging.error("Could not cast Circulating Supply.")
        result = None
    return result

def get_top_n_coin_data(table_rows, driver):
    if len(table_rows) < TOP_N:
        logging.error("This scraper cannot scrape that many (" + str(TOP_N) + ") records. Exiting.")
        sys.exit(1)

    result = []
    for index in range(TOP_N):
        if row_not_loaded(table_rows[index]):
            scroll_down_page(driver)
            table_rows = reload_table_rows(driver)
        
        columns = table_rows[index].findChildren('td')

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
    table_rows = get_table_with_data(html)
    result = get_top_n_coin_data(table_rows, driver)
    print(result)

if __name__ == "__main__":
    main()
