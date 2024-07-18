from urllib.parse import urlparse
from components.polling_manager import PollingManager
from components.qrcode_manager import QRCodeManager
from components.app_flow_manager import AppFlowManager


class Components:
    def __init__(self, url, logger):
        self.url = url
        self.domain = ".".join(urlparse(url).netloc.split(":")[0].split(".")[-2:])    
        
        self.polling_manager = PollingManager()
        self.qrcode_manager = QRCodeManager(logger)   # including generation request for QR code
        self.app_flow_manager = AppFlowManager()
