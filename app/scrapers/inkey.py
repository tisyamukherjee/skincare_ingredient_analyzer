import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from app import create_app
from app.models import db, ScrapedData
import csv
import time

def popup(driver):
    try:
        # Locate the popup close button using its unique ID or attributes
        close_button = driver.find_element(By.ID, "closeIconContainer")
        
        # Click the close button
        close_button.click()
        print("Popup closed successfully.")
    except NoSuchElementException:
        print("Popup close button not found. Skipping popup handling.")

def check_next_page():
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Next Page"]')
        return next_button
    except NoSuchElementException:
        return None

base = "https://www.theinkeylist.com/"
start = "https://www.theinkeylist.com/collections/skin"
brand = "The Inkey List"


driver_path = '/opt/homebrew/bin/chromedriver'
service = Service(driver_path)
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 5)

product_urls = []

driver.get(start)
soup = BeautifulSoup(driver.page_source, 'html.parser')
time.sleep(5)

while True:
    popup(driver)
    products = soup.find_all("div", class_= "boost-pfs-filter-product-item")
    for product in products:
        url = product.find("a")["href"]
        url = requests.compat.urljoin(base, url)
        product_urls.append(url)
    
    next_button = check_next_page()
    if next_button:
        try:
            next_button.click()
            time.sleep(3)  # Wait for the next page to load
        except TimeoutException:
            print("Failed to load next page. Exiting.")
            break
    else:
        print("No more pages found.")
        break

