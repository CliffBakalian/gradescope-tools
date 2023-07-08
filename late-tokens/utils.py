from selenium import webdriver
from dotenv import dotenv_values
import logging

'''
Just some utility functions. 
'''

def login(browser,uname,pword):
  try: 
    #find the email and password parts of the login form on graedscope's site
    browser.get('https://www.gradescope.com/login')
    logging.info("got login url")
    username=browser.find_element("id","session_email");
    logging.info("found session email")
    password=browser.find_element("id","session_password");
    logging.info("found session password")
    login=browser.find_element("name", "commit")
    logging.info("found commit")

    username.send_keys(uname);
    password.send_keys(pword);
    logging.info("about to click login")
    login.click() # login

    '''
    make sure you actually logged in. It will redirect you if your credentials
    are wrong.
    '''
    expected = "https://www.gradescope.com/account" 
    if checkPage(browser,expected):
      logging.info("Login Successful")
      return browser
    else:
      browser.close()
      logging.error("Login Failed: incorrect credentials)")
  except Exception as e:
    browser.close()
    logging.error("Could not find elements on Login page or gradescope is down")
    logging.error(e)

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
    logging.info("about to check page")
    logging.info("act: "+actual)
    logging.info("url: "+url)
    #IDK I NEED TO FIX THIS!!!!
    return True
    if actual == url or actual[:-1] == url or actual[:-2] == url:
      return True 
    else:
      logging.error("check for " + url + " failed")
      logging.error("actual   " + actual)
      logging.error("expected " + url)
      return False
  except Exception as e:
    browser.close()
    logging.error("check for " + url + " failed due to Selenium")
    logging.error(e)

