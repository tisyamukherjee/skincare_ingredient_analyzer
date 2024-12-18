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
from selenium.common.exceptions import TimeoutException
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

    # while True:
    #     try:
    #         # Wait for the 'View More' button to be clickable
    #         load_more_button = WebDriverWait(driver, 10).until(
    #             EC.element_to_be_clickable((By.CLASS_NAME, "load-more-results__cta-btn"))
    #         )

    #         # Scroll the button into view
    #         driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)

    #         # Click the 'View More' button
    #         ActionChains(driver).move_to_element(load_more_button).click().perform()
    #         print("Clicked 'View More' to load additional products.")

    #         # Optional: Wait for additional products to load (or button to disappear)
    #         WebDriverWait(driver, 10).until(
    #             EC.invisibility_of_element_located((By.CLASS_NAME, "load-more-results__cta-btn"))
    #         )
    #         # Wait for the button to become clickable again after new products load
    #         WebDriverWait(driver, 10).until(
    #             EC.element_to_be_clickable((By.CLASS_NAME, "load-more-results__cta-btn"))
    #         )

    #     except Exception as e:
    #         print(f"No more products to load or encountered an error: {e}")
    #         break


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

    #print(len(product_urls))

    for product_url in product_urls:
        try:
            driver.get(product_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'pdp-heading'))
            )
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            breadcrumb_list = soup.find('ul', class_='breadcrumb__nav-list')
            #title = breadcrumb_list.find_all('li')[2].get("title")

            # Handle the cookie banner
            try:
                cookie_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".onetrust-close-btn-handler"))
                )
                cookie_button.click()
                print("Cookie banner closed.")
            except Exception as e:
                print("Cookie banner not clickable or not found:")


            # Wait for the 'See Full Ingredient List' button and click it
            expand_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'summary.keyIngredients-details__title'))
            )

            # Scroll the button into view and click it
            driver.execute_script("arguments[0].scrollIntoView(true);", expand_button)
            ActionChains(driver).move_to_element(expand_button).click().perform()

            # Wait for the ingredient content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'keyIngredients-details__content'))
            )

            # Scrape the ingredient list
            ingredients = soup.find('div', class_="richtext keyIngredients-details__content").text
            link = driver.current_url
            name = soup.find('h1', class_="pdp-heading").text

            product_data.append({
                'brand': "CeraVe",
                'name': name,
                'link': link,
                #'category': title,
                'ingredients': ingredients
            })
        # Perform your scraping here
        except Exception as e:
            print(f"Error loading product page: {e}")

        # new_data = ScrapedData(name=name, link=link, category=title, ingredients=ingredients)
        # db.session.add(new_data)
        # db.session.commit()

    driver.get(full_url)
    time.sleep(2)

driver.quit()

with open('cerave.csv', 'w', newline='', encoding='utf-8') as csvfile:
    # fieldnames = ['brand', 'name', 'link', 'category', 'ingredients']
    fieldnames = ['brand', 'name', 'link', 'ingredients']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Loop through scraped data and write each item to the CSV
    for product in product_data:
        writer.writerow({
            'brand': product['brand'],
            'name': product['name'],
            'link': product['link'],
            #'category': product['category'],
            'ingredients': product['ingredients']  
        })
    
