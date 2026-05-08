"""Screenshot capture service using Selenium WebDriver."""
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


def capture_url(url: str, save_path: str, width: int = 1280, height: int = 720, timeout: int = 20):
    """
    Capture a full-page screenshot of the given URL.
    Saves to save_path as PNG.
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--window-size={width},{height}")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--disable-extensions")

    service = Service(ChromeDriverManager().install())
    driver  = webdriver.Chrome(service=service, options=options)

    try:
        driver.set_page_load_timeout(timeout)
        driver.get(url)

        # Scroll to bottom to trigger lazy-load
        total_height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(width, max(total_height, height))

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        driver.save_screenshot(save_path)
        logger.info("Screenshot saved: %s", save_path)
    finally:
        driver.quit()

    return save_path
