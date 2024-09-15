
import sys
from config.webdriver_config import configure_webdriver
import cv2
from pyzbar.pyzbar import decode
from utils import extract_para


class QRCodeHandler:
    def __init__(self, proxy_server="localhost:7778"):
        self.driver = configure_webdriver(proxy_server)
        self.screenshot_path = "./intermediate_files/screenshot.png"


    def capture_screenshot(self, url):
        try:
            self.driver.get(url)
            input("\033[1;32mWhen QR Code appears on the screen, press Enter to continue...\033[0m")
            
            window_handles = self.driver.window_handles
            self.driver.switch_to.window(window_handles[-1])
            
            self.driver.save_screenshot(self.screenshot_path)
            print(f"Screenshot captured: {self.screenshot_path}")

            input("\033[1;32mAfter finishing QRLogin, press Enter to start FLAW DETECTION...\033[0m")
            with open('./intermediate_files/done_flag.txt', 'w') as f:
                f.write('1')

            input("\033[1;32mPress Enter to exit...\033[0m")
            self.driver.quit()

        except Exception as e:
            print(f"Error when capturing screenshot: {e}")


    @staticmethod
    def decode_qrcode(screenshot_path):
        print(f"File {screenshot_path} prepared for decoding")

        image = cv2.imread(screenshot_path)
        decoded_objects = decode(image)
        params = {}

        if not decoded_objects:
            print("pyzbar did not detect any QR codes")
        else:
            for obj in decoded_objects:
                print(f"Type: {obj.type}, Data: {obj.data}")

            largest_qr = max(decoded_objects, key=lambda x: x.rect[2] * x.rect[3])
            decoded_data = largest_qr.data.decode("utf-8")
            print(f"Decoded data of the largest QR code: {decoded_data}")

            params = extract_para(decoded_data)
            print(f"Extracted parameters: {params}\n\n")

        if not decoded_objects:
            decoded_objects = cv2.QRCodeDetector().detectAndDecode(image)
            if decoded_objects[0] != '':
                decoded_data = decoded_objects[0]
                print(f"Decoded data of the largest QR code: {decoded_data}")
                params = extract_para(decoded_data)
                print(f"Extracted parameters: {params}")
            else:
                print("opencv detectAndDecode did not detect any QR codes")

        return params

    

    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print("url:", url)
        qrcode_handler = QRCodeHandler()
        qrcode_handler.capture_screenshot(url)
    else:
        print("No url argument provided.")