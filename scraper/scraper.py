import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(executable_path=os.path.abspath('chromedriver'), options=options)

URL = "https://coinmarketcap.com/"
driver.get(URL)
html = driver.page_source

soup = BeautifulSoup(html, features="html.parser")
rows = soup.find('tbody').findChildren('tr')

result = []

for row in rows:
    columns = row.findChildren('td')

    column = columns[2].findChildren('p')
    name = column[0].text
    symbol = column[1].text

    column = columns[3].findChildren('a')
    price = column[0].text

    column = columns[4]
    change24h_sign = 1 if "up" in column.find('span').find('span')['class'][0] else -1
    change24h = column.text

    column = columns[5]
    change7d_sign = 1 if "up" in column.find('span').find('span')['class'][0] else -1
    change7d = column.text

    column = columns[6].findChildren('span')
    market_cap = column[-1].text

    column = columns[7].find('a').find('p')
    volume24h = column.text

    column = columns[8].find('p')
    circulating_supply = column.text

    print(name)
    print(symbol)
    print(price)
    print(change24h_sign)
    print(change24h)
    print(change7d_sign)
    print(change7d)
    print(market_cap)
    print(volume24h)
    print(circulating_supply)

    break
    
# import json
# import requests
# from bs4 import BeautifulSoup

# URL = "https://coinmarketcap.com/"
# html = requests.get(URL).text

# parsed_html = BeautifulSoup(html, features="html.parser")

# json_data = parsed_html.find("script", id="__NEXT_DATA__", type="application/json").string  # by inspection from using the 'curl' command on the URL 'https://coinmarketcap.com/'
# json_data = json.loads(json_data)

# top_cryptocurriencies = json_data["props"]["initialState"]["cryptocurrency"]["listingLatest"]["data"]

# bitcoin_price = top_cryptocurriencies[0]["quotes"][-1]["price"]  # the price of one bitcoin in USD, the pricees of other cryptocurrencies are a multiplier of this value

# for index, crypto in enumerate(top_cryptocurriencies):
#     if index >= 2:
#         break
#     print(str(index+1))
#     print(crypto)
#     print(crypto["name"])  # name
#     print(crypto["symbol"])  # symbol
#     print(crypto["quotes"][0]["price"] * bitcoin_price)  # Price X
#     print(crypto["quotes"][0]["percentChange24h"])  # 24h %
#     print(crypto["quotes"][0]["percentChange7d"])  # 7d %
#     print(crypto["quotes"][0]["marketCap"] * bitcoin_price)  # Market Cap X
#     print(crypto["quotes"][0]["volume24h"])  # Volume 24h X
#     print(crypto["circulatingSupply"])  # Circulating Supply
#     print()
