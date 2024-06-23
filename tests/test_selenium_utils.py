import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def initialize_driver():
    service = Service('/usr/local/bin/geckodriver')
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(service=service, options=options)
    return driver

def validate_url(url):
    if "tempestwx.com/map/" not in url:
        raise ValueError("Invalid URL format. Please provide a valid TempestWX URL.")
    return url

def extract_coordinates(url):
    parts = url.split('/')
    if len(parts) >= 7:
        latitude = parts[-3]
        longitude = parts[-2]
        zoom = parts[-1]
        return latitude, longitude, zoom
    else:
        raise ValueError("URL does not contain valid coordinates.")

def get_station_id_from_url(url):
    parts = url.split('/')
    if len(parts) >= 7 and parts[-4].isdigit():
        return parts[-4]
    return None

def get_placemarkers(driver, url):
    try:
        driver.get(url)
        time.sleep(5)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[title]'))
        )
        placemarkers = driver.find_elements(By.CSS_SELECTOR, 'div[title]')
        if len(placemarkers) > 50:
            print("Too many markers found. Please zoom in closer and try again.")
            return [], []
        placemarker_titles = [placemarker.get_attribute('title').strip() for placemarker in placemarkers]
        return placemarker_titles, placemarkers
    except Exception as e:
        print(f"An error occurred while getting placemarkers: {e}")
        return [], []

def select_placemarker(placemarker_titles):
    if len(placemarker_titles) == 1:
        print(f"Only one placemarker found: {placemarker_titles[0]}")
        return 0
    elif len(placemarker_titles) == 0:
        print("No placemarkers found.")
        return -1
    else:
        print("Multiple placemarkers found:")
        for idx, title in enumerate(placemarker_titles):
            print(f"{idx + 1}: {title}")
        while True:
            try:
                selection = int(input("Enter the number of the placemarker you want to select: ")) - 1
                if 0 <= selection < len(placemarker_titles):
                    return selection
                else:
                    print(f"Please enter a number between 1 and {len(placemarker_titles)}.")
            except ValueError:
                print("Please enter a valid number.")

def get_station_id(driver, placemarker):
    try:
        placemarker.click()
        time.sleep(5)
        station_detail = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, 'station-detail'))
        )
        station_info = station_detail.find_element(By.XPATH, './/a[contains(@href, "/station/")]')
        station_id = station_info.get_attribute('href').split('/station/')[1].split('?')[0]
        return station_id
    except Exception as e:
        print(f"An error occurred while getting the station ID: {e}")
        return None
