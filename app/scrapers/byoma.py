import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from app import create_app
from app.models import db, ScrapedData
import csv
import time 

base_url = "https://byoma.com/"
start_url = "https://byoma.com/product-category/product-type/"
brand = "Byoma"

# get all product links 
driver_path = '/opt/homebrew/bin/chromedriver'
service = Service(driver_path)
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 10)

driver.get(start_url)
soup = BeautifulSoup(driver.page_source, 'html.parser')

product_urls = []
#product_list = soup.find("ul", class_= "products")
product_cards = soup.find_all("li", class_= "ast-col-sm-12")
for product in product_cards:
    url = product.find("a", class_= "ast-loop-product__link")["href"]
    #print(url)
    product_urls.append(url)

product_data = []
# go through each product 
for url in product_urls:
    driver.get(url)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product_title")))
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # get name
    name = soup.find("h1", class_= "product_title entry-title").text

    # get category
    category = driver.find(By.XPATH, '//*[@id="product-108133"]/div[2]/div[2]/div[1]/div[2]/p[1]').text
    
    # press ingredients tab 
    try:
        ingredient_tab = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="heading-pa-108133-2"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", ingredient_tab)
        driver.execute_script("arguments[0].click();", ingredient_tab)
    except Exception as e:
        print(f"Error clicking 'Ingredient Tab' for product {url}: {e}")
        continue  # Skip to the next product if this fails

    # extract ingredients
    ingredients = driver.find_element(By.XPATH, '//*[@id="content-pa-108133-2"]/p[2]/text()')
    print(ingredients)

    product_data.append({
        'brand': brand,
        'name': name,
        'link': url,
        'category': category,
        'ingredients': ingredients
    })

driver.quit()

with open('byoma.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['brand', 'name', 'link', 'category', 'ingredients']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Loop through scraped data and write each item to the CSV
    for product in product_data:
        writer.writerow({
            'brand': product['brand'],
            'name': product['name'],
            'link': product['link'],
            'category': product['category'],
            'ingredients': product['ingredients']  
        })
