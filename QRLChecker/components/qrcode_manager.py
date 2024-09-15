import os

from qrlogin_process import QRCodeHandler
from utils import *


class QRCodeManager:
    def __init__(self, logger):
        self.logger = logger

        self.qrid_name = ""
        self.qrid_value = ""
        self.qrid_newvalue = ""
        self.qrid_name_in_creation = ""  

        self.request_cookie_url = ""

        self.create_qrcode_url = ""
        self.create_qrcode_flow_info = None  
        self.create_qrcode_flow_replay = None  



    def set_qrid_name(self, key):
        self.qrid_name = key
    
    def set_qrid_value(self, value):
        self.qrid_value = value

    def set_new_qrid(self, value):
        self.qrid_newvalue = value

    def set_qrid_name_in_creation(self, qrid_name):
        self.qrid_name_in_creation = qrid_name
    
    def set_create_qrcode_flow_info(self, flow_info):
        self.create_qrcode_flow_info = flow_info
    
    def set_create_qrcode_url(self, url):
        self.create_qrcode_url = url
    
    def set_create_qrcode_flow_replay(self, flow):
        self.create_qrcode_flow_replay = flow
    
    def set_request_cookie_url(self, url):
        self.request_cookie_url = url

    def get_qrid_name(self):
        return self.qrid_name
    
    def get_qrid_value(self):
        return self.qrid_value
    
    def get_qrid_newvalue(self):
        return self.qrid_newvalue

    def get_create_qrcode_flow_info(self):
        return self.create_qrcode_flow_info
    
    def get_create_qrcode_url(self):
        return self.create_qrcode_url
    
    def get_qrid_name_in_creation(self):
        return self.qrid_name_in_creation
    
    def get_create_qrcode_flow_replay(self):
        return self.create_qrcode_flow_replay
    
    def get_request_cookie_url(self):
        return self.request_cookie_url