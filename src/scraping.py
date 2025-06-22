from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tempfile
import time
import re
import sys
import json

def slugify(dish):
    return re.sub(r'[^a-z0-9\-]', '', dish.lower().replace(' ', '-'))

dish = sys.argv[1]
location = sys.argv[2]
slug = slugify(dish)

url = f'https://www.swiggy.com/city/{location}/{slug}-dish-restaurants'

# Setup Chrome for JS rendering
temp_profile = tempfile.mkdtemp()
options = Options()
options.add_argument(f"--user-data-dir={temp_profile}")
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.get(url)

try:
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "DishItem__ImageWrapper-sc-ishzkt-5"))
    )
except:
    print(json.dumps({"error": "Timed out waiting for dish data"}))
    driver.quit()
    sys.exit()

# Parse the rendered page
soup = BeautifulSoup(driver.page_source, 'html.parser')

# 🍽️ 1. Extract restaurant names
restaurants = soup.find_all("div", class_="DishCard__ContentWrapper-sc-i11giv-3 hchWtu")
resnames = []

for res in restaurants:
    full_text = res.get_text(separator=" ").strip()
    if "•" in full_text:
        name = full_text.split("•")[0].strip()
        resnames.append(name)

# 💰 2. Extract price (just first one for now)
prices = soup.find_all("div", class_="DishItem__LineContainer-sc-ishzkt-1 lkyLCf")
price = "N/A"
if prices:
    first_price = prices[0].get_text(strip=True)
    price = first_price if first_price else "N/A"

# 🖼️ 3. Extract dish image
img = soup.find("img", class_="sc-guDLRT jsePvr DishItem__ImageWrapper-sc-ishzkt-5 dlUsJv")
image_url = ""
image_url = ""
first_img = soup.find("img", class_="sc-guDLRT jsePvr DishItem__ImageWrapper-sc-ishzkt-5 dlUsJv")
if first_img and first_img.get("src"):
    image_url = first_img["src"]

driver.quit()

# 📦 Final structured response
result = {
    "dish":dish,
    "resnames": resnames,
    "price": price,
    "image": image_url,
    "url" : url
}

print(json.dumps(result))
