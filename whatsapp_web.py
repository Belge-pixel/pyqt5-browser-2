import time
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


WHATSAPP_URL = "https://web.whatsapp.com"
CHROME_PROFILE_PATH = "./whatsapp_profile"


def create_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--user-data-dir=./")
    options.add_argument(f"--profile-directory={CHROME_PROFILE_PATH}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1400,1000")

    driver = webdriver.Chrome(options=options)
    driver.get(WHATSAPP_URL)
    return driver


def wait_for_login(driver, timeout: int = 180) -> None:
    selector = (By.XPATH, "//div[@data-testid='app']")
    WebDriverWait(driver, timeout).until(
        lambda d: "web.whatsapp.com" in d.current_url and d.execute_script("return document.readyState") == "complete"
    )
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, "//div[@data-testid='chat-list']"))
    )
    print("Connexion WhatsApp Web OK")


def open_chat(driver, contact_name: str) -> None:
    search_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true' and @role='textbox']"))
    )
    search_box.clear()
    search_box.send_keys(contact_name)
    time.sleep(2)

    contact_xpath = f"//span[@title='{contact_name}']"
    contact = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, contact_xpath))
    )
    contact.click()


def send_message(driver, contact_name: str, message: str) -> None:
    open_chat(driver, contact_name)

    input_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true' and @data-tab='6']"))
    )
    input_box.send_keys(message)
    input_box.send_keys(Keys.ENTER)
    print(f"Message envoyé à {contact_name}: {message}")


def listen_for_new_messages(driver, callback):
    while True:
        try:
            messages = driver.find_elements(By.XPATH, "//div[contains(@class, 'message-in')]")
            if messages:
                last_message = messages[-1].text
                callback(last_message)
            time.sleep(2)
        except Exception:
            time.sleep(2)


if __name__ == "__main__":
    driver = create_driver()
    wait_for_login(driver)
    print("WhatsApp Web prêt")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Fermeture du navigateur")
        driver.quit()
