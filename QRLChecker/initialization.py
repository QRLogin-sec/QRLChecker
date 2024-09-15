import sys
import time
from config.logger_config import LoggerConfig
from traffic_recorder import TrafficRecorder
from components.components import Components
from detection import Detector
import threading
import urllib
import os
from urllib.parse import unquote, urlparse
from utils import *

class Analyzer:
    def __init__(self, url, debuggable=False):
        self.debuggable = debuggable

        self.url = url

        self.logger = LoggerConfig(url).get_logger()

        self.components = Components(url, self.logger) 
        
        self.traffic_recorder = TrafficRecorder(url, self.logger, self.debuggable)

        self.polling_manager = self.components.polling_manager
        self.qrcode_manager = self.components.qrcode_manager
        self.app_flow_manager = self.components.app_flow_manager
        

        os.makedirs("res", exist_ok=True)
        self.res_file = f"./res/res_{urllib.parse.quote(url, safe='')}.txt"

        self.check()
        self.read_config()
        self.detector = Detector(self.components, self.traffic_recorder, self.logger)
        
        self.lock = threading.Lock()
        threading.Thread(target=self.run_check_done).start()
    

    def read_config(self):
        config = json.load(open("./config/configuration.json", "r"))
        base_info = config["base"]
        polling_resp_info = config["polling_response_format"]

        self.qrcode_manager.set_qrid_name(base_info["qrid_name"])
        self.qrcode_manager.set_create_qrcode_url(base_info["generation_url"])

        self.polling_manager.set_polling_url(base_info["polling_url"])
        
        self.app_flow_manager.set_authorization_url(base_info["authorization_url"])
        
        self.polling_manager.set_polling_resp_indicator(polling_resp_info["indicator"])
        self.polling_manager.set_polling_resp_status(polling_resp_info["value"])


    def check(self):
        os.makedirs("intermediate_files", exist_ok=True)

        if os.path.exists("./intermediate_files/done_flag.txt"):
            os.remove("./intermediate_files/done_flag.txt")


    def run_check_done(self):
        '''
        Check if QRLogin is done and start flaw detection
        '''        
        wf = open(self.res_file, 'w')
        write_head = False
        while True:
            if is_login_done():
                self.logger.info("************* is_login_done: True")
                self.prepare()

                if not write_head:
                    wf.write(f"qrid: \n{str(self.qrcode_manager.get_qrid_name())}: {str(self.qrcode_manager.get_qrid_value())}\n\n")
                    wf.write("F1\t\tF2\t\tF3\t\tF4\t\tF5\t\tF6\n")
                    write_head = True

                res = self.detector.detect()
                for i in res:
                    wf.write(str(i) + "\t")
                wf.write("\n")
                break
            time.sleep(3)


    def load(self, loader):
        loader.add_option(name = "url", typespec = str, default = "", help = "The URL to analyze")


    def prepare(self):
        """
        Preparation for flaw detection:
        1. Identifies polling request and associated qrid.
        2. Finds the request to create a QR code.
        3. Analyzes app flows to find the login request.
        4. Identifies the request to extract cookie.
        """
        self.logger.info("Starting preparation...")

        self.locate_polling_request_and_qrid()

        self.locate_create_qrcode_request()

        self.locate_app_authorization_request()

        self.identify_cookie_request()


    
    def locate_polling_request_and_qrid(self):
        """
        Identify the polling request and qrid
        """
        for flow_info in self.traffic_recorder.get_flows():
            flow = flow_info[0]
            flow_type = flow_info[1]
            if flow_type == "response":
                continue
            if flow.request.method == "OPTIONS":       
                continue
            
            if self.polling_manager.get_polling_flow() is not None:
                break

            # polling
            if flow.request.url == self.polling_manager.get_polling_url():
                self.polling_manager.set_polling_flow(flow)
                self.print_log(f"************* Found polling flow: {str(flow)}")
                
                # qrid
                qrid_value = self.locate_field_value(flow, "request", self.qrcode_manager.get_qrid_name())
                if qrid_value != "":
                    self.qrcode_manager.set_qrid_value(qrid_value)
                    self.print_log(f"************* Found qrid: {qrid_value}")
                else:
                    self.print_log(f"************* Not found qrid in polling flow: {self.qrcode_manager.get_qrid_name()}")



    def locate_create_qrcode_request(self):
        """
        Find the request to create a QR code based on qrid
        """
        for flow_info in self.traffic_recorder.get_flows():
            flow = flow_info[0]
            flow_type = flow_info[1]
            if flow.request.method == "OPTIONS": 
                continue

            if flow_type == "request" and flow.request.url == self.polling_manager.get_polling_url() and flow.request.method == self.polling_manager.get_polling_flow().request.method:
                continue
            
            
            if self.qrcode_manager.get_create_qrcode_flow_info() is None and flow.request.url == self.qrcode_manager.get_create_qrcode_url():
                print(f"$$$$$$$$$$$ flow.request.url: {flow.request.url}, {flow_type}")
                field = search(flow, flow_type, self.qrcode_manager.get_qrid_value())
                if field != "":
                    self.qrcode_manager.set_qrid_name_in_creation(field)
                    self.logger.info(f"************* Found qrid_name_in_creation: {field}")
                    self.qrcode_manager.set_create_qrcode_flow_info(flow_info)
                    self.logger.info(f"$$$$$$$$$$$ Found create qrcode flow: {str(flow_info)}")
                    print(f"$$$$$$$$$$$ Found create qrcode flow: {str(flow_info)}")
                    break
    
    
    def locate_app_authorization_request(self):
        """
        Find the request to authorize the app
        """
        if self.app_flow_manager.get_login_request() == []:
            for flow_info in self.app_flow_manager.get_app_flows():
                flow = flow_info[0]
                flow_type = flow_info[1]
                if flow_type == "request":
                    if flow.request.url == self.app_flow_manager.get_authorization_url():
                        self.app_flow_manager.add_login_request(flow_info)
                        self.logger.info(f"$$$$$$$$$$$[app] Found login request: {str(flow_info)}")


    def identify_cookie_request(self):
        """
        Identify the request to extract cookie
        """
        cookie_dict = {}
        create_qrcode_flow_info = self.qrcode_manager.get_create_qrcode_flow_info()
        if create_qrcode_flow_info is not None:
            flow = create_qrcode_flow_info[0]
            flow_type = create_qrcode_flow_info[1]
            cookie_dict = parse_cookie(flow, "request")

            if cookie_dict != {}:
                for flow_info in self.traffic_recorder.get_flows():
                    flow = flow_info[0]
                    flow_type = flow_info[1]
                    if flow_type == "request":
                        continue
                    has_found = False
                    for k, v in cookie_dict.items():
                        if k not in str(flow.response.headers) or v not in str(flow.response.headers):
                            break
                        self.qrcode_manager.set_request_cookie_url(flow.request.url)
                        has_found = True
                        break
                    if has_found == True:
                        break
    


    def locate_field_value(self, flow, flow_type, field):
        """
        Find the value of a field in the request/response
        """
        if flow_type == "request":
            for k, v in flow.request.query.items():
                if field == str(k):
                    return v
            if field in str(flow.request.url):
                return "noValue"
            
            if flow.request.content:
                content_dict = parse_content(flow.request)
                if isinstance(content_dict, dict):
                    flatten_dict = flatten_nested_dict(content_dict)
                    for k, v in flatten_dict.items():
                        if field == str(k):
                            return v

            for k, v in flow.request.headers.items():
                if k.lower() in ['cookie', 'set-cookie']:
                    continue
                if field == str(k):
                    return v
            cookie_dict = parse_cookie(flow, flow_type)
            for key, value in cookie_dict.items():
                if str(key) == str(field):
                    return value
    
        if flow_type == "response":
            if flow.response.content:
                content_dict = parse_content(flow.response)
                if isinstance(content_dict, dict):
                    flatten_dict = flatten_nested_dict(content_dict)
                    for k, v in flatten_dict.items():
                        if field == str(k):
                            return v
                        elif field == str(unquote(str(k))):
                            return v

            for k, v in flow.response.headers.items():
                if field == str(k):
                    print("##############search result in headers(actually):", k)
                    return v
            for k, v in flow.response.headers.items():
                if field in str(v):
                    cookie_dict = parse_cookie(flow, "response")
                    for key, value in cookie_dict.items():
                        if field == str(key):
                            print("##############search result in headers(in set-cookie):", key)
                            return value
                    return v
        return ""


    def print_log(self, content):
        print(content)
        self.logger.info(content)
    

    def request(self, flow):
        if is_login_done():
            self.traffic_recorder.write_log_request(flow)
            return
        
        if "Android" in flow.request.headers.get('User-Agent', ''):
            self.app_flow_manager.add_app_flow(flow, "request")
            self.traffic_recorder.write_log_request(flow)
            self.logger.info("[APP]Get request of app flow")
            self.logger.info("[APP]Request: " + str(flow.request))  
            return

        self.traffic_recorder.write_log_request(flow)
        self.traffic_recorder.record_flow(flow, "request")
        url = flow.request.url
        self.traffic_recorder.update_url_counts(url)


    def response(self, flow):
        if is_login_done():
            self.traffic_recorder.write_log_request(flow)
            return
        
        if "Android" in flow.request.headers.get('User-Agent', ''):
            self.app_flow_manager.add_app_flow(flow, "response")
            self.traffic_recorder.write_log_response(flow)
            return

        self.traffic_recorder.write_log_response(flow)
        self.traffic_recorder.record_flow(flow, "response")

        if flow.request == self.qrcode_manager.get_create_qrcode_flow_replay():
            self.logger.info("[REPLAY]Get response of replayed create qrcode request" + str(flow.response))

        if flow.request == self.polling_manager.get_new_polling_flow_replay():
            self.logger.info("[REPLAY]Get response of replayed polling request" + str(flow.response))
        


if len(sys.argv) > 1:
    url = sys.argv[4][4:]
    print("url:", url)
    debuggable = False
    addons = [
        Analyzer(url, debuggable)]
else:
    print("[!] No url argument provided.")