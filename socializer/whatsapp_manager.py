from selenium import webdriver
from urllib.parse import quote

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WhatsAppManager:
    PAGE_LOAD_TIMEOUT_SECONDS = 100

    def __init__(self):
        options = Options()
        options.binary_location = (
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        )
        driver_path = "/usr/local/bin/chromedriver"
        self.driver = webdriver.Chrome(options=options, executable_path=driver_path)

    def sendwhatmsg(self, phone_no, message):
        parsedMessage = quote(message)
        self.driver.get(
            "https://web.whatsapp.com/send?phone=" + phone_no + "&text=" + parsedMessage
        )

        button_xpath = '//*[@id="main"]/footer/div[1]/div[3]/button'
        button = WebDriverWait(
            driver=self.driver, timeout=self.PAGE_LOAD_TIMEOUT_SECONDS
        ).until(EC.presence_of_element_located((By.XPATH, button_xpath)))
        button.send_keys(Keys.RETURN)