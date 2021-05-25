"""
filename: scraper.py
author: Alexander DeForge
date: 05/24/2021
purpose: Scrape the website coinmarketcap.com for top N cryptocurrencies and some of their properties at the time.
"""

import os
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


CHROMEDRIVER_PATH = os.path.abspath('chromedriver')
URL = "https://coinmarketcap.com/"
TOP_N = 100


def setup():
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

def get_coin_name(columns):
    column = columns[2].findChildren('p')
    result = column[0].text
    return result

def get_coin_symbol(columns):
    column = columns[2].findChildren('p')
    result = column[1].text
    return result

def get_coin_price(columns):
    column = columns[3].findChildren('a')
    price = column[0].text
    price = re.sub(r"[$|,]","",price)  # strip the '$' symbol and ',' symbols
    result = float(price)    # catch cast exception
    return result

def get_coin_change24h(columns):
    column = columns[4]
    change24h_sign = 1 if "up" in column.find('span').find('span')['class'][0] else -1
    change24h = column.text
    change24h = re.sub(r"[%]","",change24h)  # strip '%' symbol
    change24h = float(change24h)    # catch cast exception
    result = change24h_sign * change24h
    return result

def get_coin_change7d(columns):
    column = columns[5]
    change7d_sign = 1 if "up" in column.find('span').find('span')['class'][0] else -1
    change7d = column.text
    change7d = re.sub(r"[%]","",change7d)  # strip '%' symbol
    change7d = float(change7d)  # catch cast exception
    result = change7d_sign * change7d
    return result

def get_coin_market_cap(columns):
    column = columns[6].findChildren('span')
    market_cap = column[-1].text
    market_cap = re.sub(r"[$|,]","",market_cap)  # strip '$' symbol and ',' symbols
    result = int(market_cap)
    return result

def get_coin_volume24h(columns):
    column = columns[7].find('a').find('p')
    volume24h = column.text
    volume24h = re.sub(r"[$|,]","",volume24h)  # strip '$' symbol and ',' symbols
    result = int(volume24h)
    return result

def get_coin_circulating_supply(columns):
    column = columns[8].find('p')
    circulating_supply = column.text
    circulating_supply = re.sub(r'[A-Z|\s|,]','',circulating_supply)  # strip ',' symbols, whitespace and coin symbol
    result = int(circulating_supply)
    return result

def get_top_n_coin_data(table_rows):
    result = []
    for index, row in enumerate(table_rows):
        if index >= 2:
            break
        columns = row.findChildren('td')
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
    
    if index+1 < TOP_N:
        # log error
        pass
    
    return result

def main():
    driver = setup()
    html = get_hypertext(driver)
    table_rows = get_table_with_data(html)
    result = get_top_n_coin_data(table_rows)
    print(result)

if __name__ == "__main__":
    main()
