# coinmarketcap-scraper
Web scraper for the website coinmarketcap.com

## Clone Repository
Navigate to a directory of your choice and run either of the following commands.  
Clone via https  
`git clone https://github.com/alexd-conf/coinmarketcap-scraper.git`  
Clone via ssh  
`git clone git@github.com:alexd-conf/coinmarketcap-scraper.git`
## Install Google Chrome
Whether you are using a system with or without a desktop environment, please still install Google Chrome if not already installed. The scraping program will run in headless mode, regardless of the presence of a desktop environment on your system.  
## Download Chromedriver
Check the version of your Google Chrome installation and download the appropriate 'chromedriver' file from this link https://chromedriver.chromium.org/downloads.  
Once you have done so, please copy the 'chromedriver' file into this project's 'coinmarketcap-scraper/scraper/' directory. The final filepath for the 'chromedriver' file in this project's directory tree should be 'coinmarketcap-scraper/scraper/chromedriver'.
## Run the Script
This script requires Python version 3.x.
### Install Dependencies
It is recommended that you use a Python virtual environment (virtualenv) when installing dependencies.  
Open a terminal and navigate to the 'coinmarketcap-scraper/' directory in this project's directory tree. Run the command  
`pip3 install -r requirements.txt`  
or equivalent for your system in order to install the dependencies listed in the file 'requirements.txt'.
### Execute the Script
In order to run the script, after you have installed the dependencies, navigate to the 'coinmarketcap-scraper/scraper/' directory in this project's directory tree using a terminal and then run the command  
`python3 scraper.py`
## Run the Tests
Open a terminal and navigate to the 'coinmarketcap-scraper/' directory in this project's directory tree. Run the command  
`python3 -m unittest`
