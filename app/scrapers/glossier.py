import requests
from bs4 import BeautifulSoup
import requests.compat
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from app import create_app
from app.models import db, ScrapedData
import csv

def handle_ingredient_button(driver, wait):
    try:
        # Wait for the button to be present
        ingredient_button = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.collapsible-content__acc-btn'))
        )
        
        # Check if the button is already open
        if "active" not in ingredient_button.get_attribute("class"):
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", ingredient_button)
            
            try:
                # Attempt to click the button
                ingredient_button.click()
                print("Clicked the button to reveal the ingredients.")
            except ElementClickInterceptedException:
                print("Popup detected. Attempting to close the popup.")
                try:
                    # Find and close the popup
                    #popup_close_button = driver.find_element(By.CSS_SELECTOR, '.klaviyo-close-form')
                    popup_close_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.klaviyo-close-form')))
                    popup_close_button.click()
                    print("Popup closed. Retrying click.")
                    
                    # Retry clicking the ingredient button
                    ingredient_button.click()
                    print("Clicked the button to reveal the ingredients after closing the popup.")
                except NoSuchElementException:
                    print("No popup close button found. Unable to proceed.")
        else:
            print("Button is already open.")

    except NoSuchElementException:
        print("Ingredient button or related element not found on the page.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

base = "https://www.glossier.com/"
start = "https://www.glossier.com/collections/skincare?parent_collection=skincare"
brand = "Glossier"

driver_path = '/opt/homebrew/bin/chromedriver'
service = Service(driver_path)
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 10)

driver.get(start)
soup = BeautifulSoup(driver.page_source, 'html.parser')

products = soup.find_all("li", class_= "collection__item")

urls = []
for product in products:
    url = product.find("a")["href"]
    url = requests.compat.urljoin(base, url)
    urls.append(url)

# scrape each product 
product_data = []
for url in urls:
    driver.get(url)

    handle_ingredient_button(driver, wait)

    # click to get full ingredients
    try:
        # Wait for the Ingredients tab to be clickable
        ingredient_tab = driver.find_element(By.CLASS_NAME, "btn.js-modal-trigger")
        
        # Scroll the element into view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", ingredient_tab)
        
        # Click the Ingredients tab
        driver.execute_script("arguments[0].click();", ingredient_tab)
        print(f"Successfully clicked the Ingredients tab on {url}")
    
    except TimeoutException:
        print(f"Timeout: Ingredients tab not found or clickable on {url}")
        continue  # Skip to the next URL
    
    except Exception as e:
        print(f"An error occurred on {url}: {e}")
        continue  # Skip to the next URL
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    ingedients = soup.find("div", id= "js-modal-body").get_text()
    name = soup.find("h1", class_= "pv-header__title").get_text()

    product_data.append({
                'brand': brand,
                'name': name.strip(),
                'link': url,
                'ingredients': ingedients.strip()
            })
    
driver.quit()

with open('glossier.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['brand', 'name', 'link', 'ingredients']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Loop through scraped data and write each item to the CSV
    for product in product_data:
        writer.writerow({
            'brand': product['brand'],
            'name': product['name'],
            'link': product['link'],
            'ingredients': product['ingredients']  
        })

