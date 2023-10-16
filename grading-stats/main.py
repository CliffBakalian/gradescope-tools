import logging
from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By

from update import *
from utils import *

config = dotenv_values(".env")
username = config["USERNAME"]
password = config["PASSWORD"]
TEST_COURSE = config['TEST_COURSE']
TEST_ASSIGNMENT = config['TEST_ASSIGNMENT']
TEST_QUESTION = config['TEST_QUESTION']

'''
start by setting up a logger to make sure everything runs smoothly
then we setup the driver and login to gradescope. Then get all data
'''
logging.basicConfig(filename='debug.log', level=logging.INFO)
driver = login(setup(),username,password)
do_it_all(driver)
