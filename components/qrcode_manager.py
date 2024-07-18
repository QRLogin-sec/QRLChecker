import os

from qrcode_handler import QRCodeHandler
from utils import *


class QRCodeManager:
    def __init__(self, logger):
        self.logger = logger

        self.qrcode_params = {}
        self.qrid = {} 
        self.newqrid = {}  
        self.qrid_name_in_creation = ""  
        self.qrid_name_in_poll = ""
        self.request_cookie_url = ""

        self.create_qrcode_flow_info = None  
        self.create_qrcode_flow_replay = None  

        self.screenshot_path = "./intermediate_files/screenshot.png"

    def set_qrid(self, key, value):
        self.qrid[key] = value
    
    def clear_qrid(self):
        self.qrid = {}

    def set_new_qrid(self, key, value):
        self.newqrid[key] = value

    def set_qrcode_params(self, params):
        self.qrcode_params = params
    
    def set_qrid_name_in_poll(self, qrid_name):
        self.qrid_name_in_poll = qrid_name
    
    def set_qrid_name_in_creation(self, qrid_name):
        self.qrid_name_in_creation = qrid_name
    
    def set_create_qrcode_flow_info(self, flow_info):
        self.create_qrcode_flow_info = flow_info

    def get_qrid(self):
        return self.qrid
    
    def get_qrid_value(self):
        return list(self.qrid.values())[0]
    
    def get_qrid_name(self):
        return list(self.qrid.keys())[0]
    
    def get_newqrid(self):
        return self.newqrid

    def get_newqrid_value(self):
        return list(self.newqrid.values())[0]
    
    def get_newqrid_name(self):
        return list(self.newqrid.keys())[0]
    
    def get_create_qrcode_flow_info(self):
        return self.create_qrcode_flow_info

    


    def decode_qrcode(self):
        """
        Decodes the QR code from screenshot
        """
        if not self.qrcode_params and os.path.exists(self.screenshot_path):
            self.qrcode_params = QRCodeHandler.decode_qrcode(self.screenshot_path)
            self.logger.info(f"Decoded qrcode_params: {self.qrcode_params}")


    def filter_qrcode_params(self):
        """
        Filter out irrelevant fields from qrcode_params
        """
        self.qrcode_params = flatten_nested_dict(self.qrcode_params)
        keys_to_delete = []
        for key, value in self.qrcode_params.items():
            if is_english_phrase(str(value)) or len(str(value)) <= 2 or str(value) == 'zh-CN':
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del self.qrcode_params[key]
        self.logger.info(f"Filtered qrcode_params: {self.qrcode_params}")


    def match_qrcode_params_with_flow(self, flow):
        """
        Match qrcode_params with a given flow
        """
        match_field_cnt = 0
        for key, value in self.qrcode_params.items():
            qrid_name = str(search(flow, "request", str(value)))
            if qrid_name:
                match_field_cnt += 1
                self.set_qrid(qrid_name, value)
        return match_field_cnt