from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def get_station_id(driver, placemarker):
    logger = logging.getLogger()
    logger.debug("Getting station ID for placemarker.")
    try:
        placemarker.click()
        time.sleep(5)  # Wait for click action to take effect
        
        # Wait for the station-detail element to appear
        station_detail = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, 'station-detail'))
        )
        
        # Extract the station ID from the href attribute
        station_info = station_detail.find_element(By.XPATH, './/a[contains(@href, "/station/")]')
        station_id = station_info.get_attribute('href').split('/station/')[1].split('?')[0]
        station_name = station_info.text.strip()
        logger.debug("Station ID and name extracted: %s, %s", station_id, station_name)
        return station_id, station_name
    except Exception as e:
        logger.error("An error occurred while getting the station ID: %s", e)
        return None, None
