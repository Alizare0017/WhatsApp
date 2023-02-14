from selenium.webdriver.common.by import By
from selenium import webdriver
from time import sleep

driver = webdriver.Chrome()

driver.get('chrome://settings/clearBrowserData')
sleep(3)
print(driver.find_element(By.XPATH,"//*[@id='checkbox']"))