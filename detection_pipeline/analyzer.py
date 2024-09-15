import sys
import time
from config.logger_config import LoggerConfig
from traffic_recorder import TrafficRecorder
from components.components import Components
from detector import Detector
import threading
import urllib
import os
from urllib.parse import unquote, urlparse
from utils import *

class Analyzer:
    def __init__(self, url, debuggable=False):
        self.debuggable = debuggable

        self.url = url
        self.domain = ".".join(urlparse(url).netloc.split(":")[0].split(".")[-2:])    

        self.logger = LoggerConfig(url).get_logger()

        self.components = Components(url, self.logger) 
        
        
        self.traffic_recorder = TrafficRecorder(url, self.logger, self.debuggable)

        self.polling_manager = self.components.polling_manager
        self.qrcode_manager = self.components.qrcode_manager
        self.app_flow_manager = self.components.app_flow_manager
        

        self.detector = Detector(self.components, self.traffic_recorder, self.logger)

        os.makedirs("res", exist_ok=True)
        self.res_file = f"./res/res_{urllib.parse.quote(url, safe='')}.txt"

        self.num = 0
        self.check()
        
        self.lock = threading.Lock()
        threading.Thread(target=self.run_check_done).start()


    def check(self):
        os.makedirs("intermediate_files", exist_ok=True)
        screenshot_path = "./intermediate_files/screenshot.png"
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
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
                self.logger.info("is_login_done: True")
                self.prepare()
                if not write_head:
                    wf.write("qrid: \n" + str(self.qrcode_manager.get_qrid()) + "\n\n")
                    wf.write("F1\t\tF2\t\tF3\t\tF4\t\tF5\t\tF6\n")
                    write_head = True
                res = self.detector.detect()
                for i in res:
                    wf.write(str(i) + "\t")
                wf.write("\n")
                self.print_log("Detection result: " + str(res))
                break
            time.sleep(3)


    def load(self, loader):
        loader.add_option(name = "url", typespec = str, default = "", help = "The URL to analyze")


    
    

    def prepare(self):
        """
        Preparation for flaw detection:
        1. Decodes QR code.
        2. Identifies polling request and associated qrid.
        3. Finds the request to create a QR code.
        4. Analyzes app flows to find the login request.
        """
        self.logger.info("Starting preparation...")

        self.qrcode_manager.decode_qrcode()

        self.identify_polling_request_and_qrid()

        self.find_create_qrcode_request()

        self.extract_cookie()

        self.analyze_app_flows_for_login_request()



    def identify_polling_request_and_qrid(self):
        """
        Identify the polling request and qrid
        """
        if not self.qrcode_manager.get_qrid() or not self.polling_manager.get_polling_flow():
            self.qrcode_manager.filter_qrcode_params()

            sorted_url_counts = self.traffic_recorder.sort_url_counts_by_frequency()
            self.logger.info(f"Sorted filtered_url_counts: {sorted_url_counts}")

            self.determine_polling_flow_and_qrid(sorted_url_counts)


   
    

    def determine_polling_flow_and_qrid(self, sorted_url_counts):
        """
        Determine the polling flow and qrid by matching params with flows.
        """
        url_flow_map = self.traffic_recorder.build_url_flow_map()

        for url, count in sorted_url_counts:
            if self.polling_manager.get_polling_flow():
                break

            url_flows = url_flow_map.get(url, [])

            for flow in url_flows:
                if flow.request.method == "OPTIONS":
                    continue

                match_field_cnt = self.qrcode_manager.match_qrcode_params_with_flow(flow)
                if match_field_cnt > 0:
                    self.process_matched_qrid(flow, match_field_cnt, url_flows)
                    if self.polling_manager.get_polling_flow():
                        self.logger.info(f"Determine polling flow: {str(self.polling_manager.get_polling_flow())}")
                        break
            if self.polling_manager.get_polling_flow():
                break
        if self.polling_manager.get_polling_flow() is None:
            print("[ERROR] cannot match qrcode_params with polling request")





    def process_matched_qrid(self, flow, match_field_cnt, url_flows):
        """
        Process the matched qrid from the flow
        """
        if match_field_cnt > 1:
            self.handle_multiple_matched_qrid()
        if match_field_cnt > 0:
            self.check_polling_flow(flow, url_flows)


    def handle_multiple_matched_qrid(self):
        """
        Handle cases where multiple qrids are matched
        """
        max_len = 0
        max_len_key = ""
        for key, value in self.qrcode_manager.get_qrid().items():
            key_lower = key.lower()
            if any(keyword in key_lower for keyword in ["id", "qr", "token", "code", "login", "no"]):
                max_len_key = key
                break
            elif len(value) > max_len:
                max_len = len(value)
                max_len_key = key
                max_len_value = value
        self.qrcode_manager.clear_qrid()
        self.qrcode_manager.set_qrid(max_len_key, max_len_value)
        self.qrcode_manager.set_qrid_name_in_poll(max_len_key)
        self.logger.info(f"Multiple qrid matched: {self.qrcode_manager.get_qrid()}")


    def check_polling_flow(self, flow, url_flows):
        """
        Determine the polling flow and qrid
        """
        if flow.request.method == "POST":
            for tmpflow in url_flows:
                if tmpflow.request.method == "GET":
                    flow = tmpflow
                    break
        
        self.polling_manager.set_polling_flow(flow)

        self.qrcode_manager.set_qrid_name_in_poll(str(list(self.qrcode_manager.get_qrid().keys())[0]))
        self.logger.info(f"Determine qrid: {self.qrcode_manager.get_qrid()}")

        threshold = 0       
        for flow in url_flows:
            if flow.request.method == "OPTIONS":       
                continue
            if search(flow, "request", self.qrcode_manager.get_qrid_value()) == "":
                threshold += 1
                if threshold > 2:
                    self.logger.info(f"Clear polling: {self.polling_manager.get_polling_url()}")
                    self.polling_manager.clear_polling_flow()
                    self.qrcode_manager.clear_qrid()
                    break


    def find_create_qrcode_request(self):
        """
        Find the request to create a QR code based on qrid
        """
        if self.qrcode_manager.get_qrid() and not self.qrcode_manager.get_create_qrcode_flow_info():
            self.logger.info("Searching create qrcode flow...")

            for flow_info in self.traffic_recorder.get_flows():
                flow = flow_info[0]
                flow_type = flow_info[1]
                if flow.request.method == "OPTIONS":
                    continue
                if (flow_type == "request" and
                    remove_params_from_url(flow.request.url) == remove_params_from_url(self.polling_manager.get_polling_url()) and
                    flow.request.method == self.polling_manager.get_polling_flow().request.method):
                    continue
                field = search(flow, flow_type, list(self.qrcode_manager.get_qrid().values())[0])
                if field:
                    self.qrcode_manager.set_qrid_name_in_creation(field)
                    self.logger.info(f"Found qrid_name_in_creation: {field}")
                    self.qrcode_manager.set_create_qrcode_flow_info(flow_info)
                    self.logger.info(f"Found create qrcode flow: {str(flow_info)}")
                    break

    
    def extract_cookie(self):
        """
        Extract cookie from the request to create a QR code or else requests
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
                        self.request_cookie_url = flow.request.url
                        has_found = True
                        break
                    if has_found == True:
                        break


    def analyze_app_flows_for_login_request(self):
        """
        Analyze app flows to find the login request based on qrid
        """
        if not self.app_flow_manager.get_login_request() and self.qrcode_manager.get_qrid():
            qrid_value = self.qrcode_manager.get_qrid_value()
            for flow_info in self.app_flow_manager.get_app_flows():
                flow = flow_info[0]
                flow_type = flow_info[1]
                if flow_type == "request" and search(flow, flow_type, qrid_value):
                    self.app_flow_manager.add_login_request(flow_info)
                    self.logger.info(f"[app] Found login request: {str(flow_info)}")
                    break




    


    def print_log(self, content):
        print(content)
        self.logger.info(content)



    

    def request(self, flow):
        # if self.domain not in flow.request.url:
        #     return
        if is_login_done():
            self.traffic_recorder.write_log_request(flow)
            return
        
        if "Android" in flow.request.headers.get('User-Agent', ''):
            self.app_flow_manager.add_app_flow(flow, "request")
            self.traffic_recorder.write_log_request(flow)
            self.logger.info("[APP]Get request of app flow")
            self.logger.info("[APP]Request: " + str(flow.request))  
            return
        self.num = self.num + 1


        self.traffic_recorder.write_log_request(flow)

        self.traffic_recorder.record_flow(flow, "request")
        url = flow.request.url
        self.traffic_recorder.update_url_counts(url)


    def response(self, flow):
        # if self.domain not in flow.request.url:
        #     return
        if is_login_done():
            self.traffic_recorder.write_log_request(flow)
            return
        
        if "Android" in flow.request.headers.get('User-Agent', ''):
            self.app_flow_manager.add_app_flow(flow, "response")
            self.traffic_recorder.write_log_response(flow)
            return

        self.traffic_recorder.write_log_response(flow)
        self.traffic_recorder.record_flow(flow, "response")

        if flow.request == self.qrcode_manager.create_qrcode_flow_replay:
            self.logger.info("[REPLAY]Get response of replayed create qrcode request" + str(flow.response))

        if flow.request == self.polling_manager.new_polling_flow_replay:
            self.logger.info("[REPLAY]Get response of replayed polling request" + str(flow.response))
        


if len(sys.argv) > 1:
    url = sys.argv[4][4:]
    print("url:", url)
    debuggable = False
    addons = [
        Analyzer(url, debuggable)]
else:
    print("[!] No url argument provided.")