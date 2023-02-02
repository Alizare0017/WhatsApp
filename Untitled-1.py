from selenium import webdriver
addrs = "chromedriver.exe"
driver = webdriver.Chrome(addrs)
driver.get('https://web.whatsapp.com/')
driver.save_screenshot("screenshot.png")