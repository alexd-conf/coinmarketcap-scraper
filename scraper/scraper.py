import json
import requests
from bs4 import BeautifulSoup

URL = "https://coinmarketcap.com/"
html = requests.get(URL).text

parsed_html = BeautifulSoup(html, features="html.parser")

json_data = parsed_html.find("script", id="__NEXT_DATA__", type="application/json").string  # by inspection from using the 'curl' command on the URL 'https://coinmarketcap.com/'
print("JSON_DATA")
print(json_data)
json_data = json.loads(json_data)

print(json_data)

