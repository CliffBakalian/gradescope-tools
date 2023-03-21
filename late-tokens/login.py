from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from dotenv import dotenv_values

import logging

config = dotenv_values(".env")

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

def login(browser):
  try: 
    browser.get('https://www.gradescope.com/login')
    username=browser.find_element("id","session_email");
    password=browser.find_element("id","session_password");
    login=browser.find_element("name", "commit")

    username.send_keys(config["USERNAME"]);
    password.send_keys(config["PASSWORD"]);
    login.click()

    expected = "https://www.gradescope.com/account" 
    actual = browser.current_url;
    if actual == expected:
      logging.info("Login Successful")
      return browser
    else:
      browser.close()
      logging.error("Login Failed: incorrect credentials)")
  except Exception as e:
    browser.close()
    logging.error("Login failed due to Selenium")
    logging.error(e)

def getCourse(browser):
  try:
    target = "https://www.gradescope.com/course/"+COURSE
    browser.get(target)
    actual = browser.current_url;
    if actual == target:
      logging.info("Course Found")
      return browser
    else:
      browser.close()
      logging.error("Course Not Found: check course ID")
  except Exception as e:
    browser.close()
    logging.error("Course lookup failed due to Selenium")
    logging.error(e)

logging.basicConfig(filename='debug.log', level=logging.INFO)
login(setup())
