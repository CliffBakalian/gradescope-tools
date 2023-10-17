from selenium import webdriver

'''
start by setting up a logger to make sure everything runs smoothly
then we setup the driver and login to gradescope. Then get all data
'''
logging.basicConfig(filename='debug.log', level=logging.INFO)
driver = get_driver() 
