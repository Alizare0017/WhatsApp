from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import base64

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument("--window-size=1920,1080")
options.add_argument(f'user-agent={user_agent}')
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 30)
def login():
    driver.get("https://web.whatsapp.com/")
    element = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[3]/div[1]/div/div/div[2]/div/div")))
    element = driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[3]/div[1]')
    element.screenshot('test.png')
    print('now')
    #element = wait.until(EC.invisibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[3]/div[1]/div/div/div[2]/div/div")))


def send():
    message = """
    Salam
"""
    phone_numbers = phone_numbers = open("test-numbers.txt").read().split("\n")
    count = 0
    if len(phone_numbers) == 0:
        print("Please Add New Phone Numbers")
    else:
        for phone in phone_numbers:
            # pn = f"{phone}".replace("0", "+98", 1)
            pn = phone
            print("Sending to :", pn)
            url = f'https://web.whatsapp.com/send?phone=+98{phone[1:]}&text={message}'

            try:
                driver.get(url)
                element = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[2]/button')))
                driver.find_element(By.XPATH,
                                    '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[2]/button').click()
                sleep(2)
                count += 1
                print("Sent :", count)
                with open('sent-numbers.txt', 'a') as f:
                    f.write(phone + "\n")
            except:
                print("Couldn't send message")
