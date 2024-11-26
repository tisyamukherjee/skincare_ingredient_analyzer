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
from app import create_app
from app.models import db, ScrapedData
import csv

base_url = "https://www.cerave.com"
start_url = "https://www.cerave.com/skincare"

# app = create_app()

# selenium set up
driver_path = '/opt/homebrew/bin/chromedriver'
service = Service(driver_path)
driver = webdriver.Chrome(service=service)
driver.get(start_url)
time.sleep(5)

# get urls 
categories = driver.find_elements(By.CLASS_NAME, 'product-clp__list-item')
category_urls = []
# category_links = [category.find_elements(By.TAG_NAME, 'a').get_attribute('href')]
product_data = []
for category in categories:
    # get a tag
    rel_url = category.find_element(By.TAG_NAME, 'a').get_attribute("href")
    full_url = requests.compat.urljoin(base_url, rel_url)
    category_urls.append(full_url)

for url in category_urls:
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'results-grid__item'))
    )

    # load_more_button = driver.find_element(By.XPATH, '//*[@id="content-container"]/div/div[5]/div/div/div[2]/button')
    # load_more_button.click()
    # # Wait for the button to be clickable
    # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "load-more-results__cta-btn"))).click()
    # # Wait for new content to load (adjust the locator to match new content)
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="content-container"]/div/div[5]/div/div/ul/li[14]')))

    products = driver.find_elements(By.CLASS_NAME, 'results-grid__item')
    product_urls = []

    for product in products:
        try:
            banner_divs = product.find_elements(By.CLASS_NAME, 'banner')
            if not banner_divs:  # Proceed only if no 'banner' div is found
                product_rel_url = product.find_element(By.TAG_NAME, 'a').get_attribute("href")
                product_full_url = requests.compat.urljoin(base_url, product_rel_url)
                product_urls.append(product_full_url)
        except Exception as e:
            print(f"Error extracting URL: {e}")


    # for product in products:
        # product_rel_url = product.find_element(By.TAG_NAME, 'a').get_attribute("href")
        # product_full_url = requests.compat.urljoin(base_url, product_rel_url)
    for product_url in product_urls:
        try:
            driver.get(product_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'pdp-heading'))
            )
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            #title = driver.find_element(By.XPATH, '//*[@id="main-container"]/div[1]/div[4]/div/nav/ul/li[3]').get_attribute("title")
            breadcrumb_list = soup.find('ul', class_='breadcrumb__nav-list')
            title = breadcrumb_list.find_all('li')[2].get("title")

            try:
                cookie_button = driver.find_element(By.CSS_SELECTOR, 'onetrust-accept-btn-handler')
                # cookie_button = WebDriverWait(driver, 10).until(
                #      EC.element_to_be_clickable((By.CSS_SELECTOR, 'onetrust-close-btn-handler'))  
                # )
                print(cookie_button)
                # ActionChains(driver).move_to_element(cookie_button).click().perform()
                # print("Cookie banner dismissed.")
            except Exception as e:
                print("Cookie banner not found or already dismissed:", e)
           
            # try:
            #     # Ensure the button is clickable
            #     print("Waiting for the 'See Full Ingredient List' button...")
            #     WebDriverWait(driver, 10).until(
            #         EC.element_to_be_clickable((By.CLASS_NAME, 'keyIngredients-details__title'))
            #     )

            #     # Scroll the button into view and click it
            #     print("Clicking the button to expand ingredients...")
            #     expand_button = driver.find_element(By.CLASS_NAME, 'keyIngredients-details__title')
            #     driver.execute_script("arguments[0].scrollIntoView(true);", expand_button)
            #     ActionChains(driver).move_to_element(expand_button).perform()
            #     expand_button.click()

            #     # Wait for the content to load
            #     print("Waiting for the ingredient details content to load...")
            #     WebDriverWait(driver, 10).until(
            #         EC.presence_of_element_located((By.CLASS_NAME, 'keyIngredients-details__content'))
            #     )

            #     # Scrape the ingredient list
            #     print("Scraping the ingredient list...")
            #     ingredient_paragraph = driver.find_element(By.CLASS_NAME, 'keyIngredients-details__content').find_element(By.TAG_NAME, 'p')
            #     ingredients = ingredient_paragraph.text.split(",")
            #     print(f"Ingredients extracted: {ingredients}")

            # except Exception as e:
            #     print(f"Error encountered: {e}")
                #ingredients = []  # Default to empty list if an error occurs
            ingredients = []
            #ingredients = driver.find_element(By.XPATH, '//*[@id="key-ingredients"]/details/div/p[1]').text.split(",")
            link = driver.current_url
            name = soup.find('h1', class_="pdp-heading").text

            product_data.append({
                'name': name,
                'link': link,
                'category': title,
                # 'ingredients': ingredients
            })
        # Perform your scraping here
        except Exception as e:
            print(f"Error loading product page: {e}")
        
        # driver.get(product_full_url)
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'pdp-heading')))

        

        # new_data = ScrapedData(name=name, link=link, category=title, ingredients=ingredients)
        # db.session.add(new_data)
        # db.session.commit()

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
            # 'ingredients': ', '.join(product['ingredients'])  # Join list of ingredients into a single string
        })
    
