from selenium import webdriver
from dotenv import dotenv_values
import logging

'''
Just some utility functions. One to setup the driver, and the other to check
that after each page change, you end up where you want to be
'''

def setup():
  try:
    fireFoxOptions = webdriver.firefox.options.Options()
    fireFoxOptions.add_argument("--headless")
    browser = webdriver.Firefox(options=fireFoxOptions)
    logging.info("Setup Successful")
    return browser
  except Exception as e:
    browser.close()
    logging.error("Setup Failed")
    logging.error(e)

def checkPage(browser,url):
  try:
    actual = browser.current_url;
    if actual == url:
      return True 
    else:
      return False
  except Exception as e:
    browser.close()
    logging.error("check for " + url + " failed due to Selenium")
    logging.error(e)
