
import sys
from config.webdriver_config import configure_webdriver
import cv2


class QRCodeHandler:
    def __init__(self, proxy_server="localhost:7778"):
        self.driver = configure_webdriver(proxy_server)

    def perform_qr_login(self, url):
        self.driver.get(url)

        input("\033[1;32mAfter finishing QRLogin, press Enter to start FLAW DETECTION...\033[0m")
        with open('./intermediate_files/done_flag.txt', 'w') as f:
            f.write('1')

        input("\033[1;32mPress Enter to exit...\033[0m")
        self.driver.quit()

   
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print("url:", url)
        qrcode_handler = QRCodeHandler()
        qrcode_handler.perform_qr_login(url)
    else:
        print("No url argument provided.")