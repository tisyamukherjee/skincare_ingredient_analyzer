# Write your web scraping logic.
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from ..models import db, ScrapedData
import csv

base_url = "https://www.cerave.com"
start_url = "https://www.cerave.com/skincare"

# selenium set up
driver_path = '/opt/homebrew/bin/chromedriver'
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# get urls 
categories = driver.find_elements(By.XPATH, '//*[@id="content-container"]/div/div[4]/ul/li[1]/a')  # Adjust the selector as needed
product_data = []
for category in categories:
    rel_url = category.get_attribute("href")
    full_url = requests.compat.urljoin(base_url, rel_url)
    driver.get(full_url)
    time.sleep(2)

    load_more_button = driver.find_element(By.XPATH, '//*[@id="content-container"]/div/div[5]/div/div/div[2]/button')
    load_more_button.click()
    # Wait for the button to be clickable
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "load-more-results__cta-btn"))).click()
    # Wait for new content to load (adjust the locator to match new content)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="content-container"]/div/div[5]/div/div/ul/li[14]')))

    products = driver.find_elements(By.XPATH, '//*[@id="content-container"]/div/div[5]/div/div/ul/li')
    for product in products:
        product_rel_url = product.find_element(By.XPATH, './/div/div/div/a').get_attribute("href")
        product_full_url = requests.compat.urljoin(base_url, product_rel_url)
        driver.get(product_full_url)
        time.sleep(2)

        response = requests.get(driver.current_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        sibling = driver.find_element(By.XPATH, '//*[@id="main-container"]/div[1]/div[4]/div/nav/ul/li[2]')
        title = sibling.find_element(By.XPATH, 'following-sibling::li').get_attribute("title")
        ingredients = driver.find_element(By.XPATH, '//*[@id="key-ingredients"]/details/div/p[1]/text()').split(",")
        link = driver.current_url
        name = soup.find('h1', class_="pdp-heading").text

        product_data.append({
            'name': name,
            'link': link,
            'category': title,
            'ingredients': ingredients
        })
        new_data = ScrapedData(name=name, link=link, category=title, ingredients=ingredients)
        db.session.add(new_data)
        db.session.commit()


    driver.get(full_url)
    time.sleep(2)

driver.quit()

with open('scraped_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['name', 'link', 'category', 'ingredients']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Loop through scraped data and write each item to the CSV
    for product in product_data:
        writer.writerow({
            'name': product['name'],
            'link': product['link'],
            'category': product['category'],
            'ingredients': ', '.join(product['ingredients'])  # Join list of ingredients into a single string
        })
    
