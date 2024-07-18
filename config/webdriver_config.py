# selenium/webdriver_config.py

from selenium import webdriver

def configure_webdriver(proxy_server="localhost:7778"):
    options = webdriver.ChromeOptions()
    options.add_argument(f"--proxy-server={proxy_server}")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--ignore-certificate-errors')
    options.page_load_strategy = 'none'

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    
    return driver
