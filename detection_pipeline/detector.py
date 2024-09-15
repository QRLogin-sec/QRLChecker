import datetime
import string
import json
import re

from mitmproxy import ctx
import configparser
from urllib.parse import parse_qsl, urlparse, quote
import urllib
import time
import requests
from utils import *

RED = "\033[31m" 
GREEN = "\033[32m" 
YELLOW = "\033[33m"  
RESET = "\033[0m"

class Detector:
    def __init__(self, components, traffic_recorder, logger):
        self.components = components
        self.logger = logger
        self.traffic_recorder = traffic_recorder
        self.url = self.components.url

        self.polling_manager = self.components.polling_manager
        self.qrcode_manager = self.components.qrcode_manager
        self.app_flow_manager = self.components.app_flow_manager


    def is_ready_for_detection(self):
        self.logger.info("Ready for detection? " + str(self.polling_manager.polling_flow) + str(self.qrcode_manager.qrid) + str(self.qrcode_manager.create_qrcode_flow_info))
        if not is_login_done():
            return False
        self.logger.info("login done")

        self.logger.info(f"is_ready_for_detection detail: \n polling_flow is not None:{self.polling_manager.polling_flow is not None}, qrid != none:{self.qrcode_manager.get_qrid() != {}}, create_qrcode_flow_info is not None:{self.qrcode_manager.get_create_qrcode_flow_info() is not None}")
        res = True
        if self.polling_manager.polling_flow is None:
            print("[ERROR] cannot find polling_flow!!")
            res = False
        if self.qrcode_manager.qrid == {}:
            print("[ERROR] cannot find qrid!!")
            res = False
        if self.qrcode_manager.create_qrcode_flow_info is None:
            print("[ERROR] cannot find create_qrcode_flow!!")
            res = False
        return res



    def detect(self):
        self.logger.info("Start detecting flaw...")

        f1 = self.F1_Unbound_session_id()
        self.print_log(RED + "Detect flaw F1 unbound sessionid: " + str(f1) + RESET)

        f2 = self.F2_Reusable_qrcode()
        self.print_log(RED + "Detect flaw F2 resuable qrcode: " + str(f2) + RESET)

        f3 = self.F3_Predictable_qr_id()
        self.print_log(RED + "Detect flaw F3 predictable qrid: " + str(f3) + RESET)
        
        f4 = self.F4_Controllable_qr_id()
        self.print_log(RED + "Detect flaw F4 controllable qrid: " + str(f4) + RESET)

        f5 = self.F5_Invalid_token_Validation()
        self.print_log(RED + "Detect flaw F5 invalid token validation: " + str(f5) + RESET)
        
        f6_data = self.F6_Sensitive_Data_Leakage()
        self.print_log(RED + "Detect flaw F6 sensitive data leakage: " + str(f6_data) + RESET)
        f6 = False
        if f6_data:
            f6 = True
        
        return [f1, f2, f3, f4, f5, f6]



    def F1_Unbound_session_id(self):
        print("======= Start detecting flaw F1: Unbound session_id =======")
        self.logger.info("Start detecting flaw F1: Unbound session_id")

        if not self.is_ready_for_detection():
            self.print_log("[F1] Not Ready: Unbound sessionid")
            return False

        create_qrcode_flow_info = self.qrcode_manager.create_qrcode_flow_info
        create_qrcode_flow_replay = self.qrcode_manager.create_qrcode_flow_replay
        if create_qrcode_flow_info is not None and create_qrcode_flow_replay is None:    
            flow = create_qrcode_flow_info[0]
            flow_type = create_qrcode_flow_info[1]

            if flow_type == "request":
                oldvalue = self.qrcode_manager.get_qrid_value()
                for i in range(10):
                    if str(i) in oldvalue:
                        newvalue = oldvalue.replace(str(i), str((i+1)%10))
                        qrid_name = self.qrcode_manager.qrid_name_in_creation
                        self.qrcode_manager.set_new_qrid(qrid_name, newvalue)
                        break
                    
                if self.qrcode_manager.newqrid == {}:
                    for c in string.ascii_letters:
                        if c in oldvalue:
                            if c == 'z':
                                newvalue = oldvalue.replace(c, 'a')
                            else:
                                newvalue = oldvalue.replace(c, chr(ord(c)+1))
                            qrid_name = self.qrcode_manager.qrid_name_in_creation
                            self.qrcode_manager.set_new_qrid(qrid_name, newvalue)
                            break
                self.print_log("create newqrid: " + str(self.newqrid))
            

            newflow2 = flow.copy()
            try:
                if self.qrcode_manager.request_cookie_url != "":
                    response =  requests.get(self.qrcode_manager.request_cookie_url, timeout=10)
                else:
                    response = requests.get(self.url, timeout=10)
            except requests.Timeout:
                print("Request timeout!")
                response = None


            if response is None:
                cookie_header = ""
            else:
                resp_cookie = response.cookies
                new_cookie = {c.name: c.value for c in resp_cookie}
                cookie_header = "; ".join([f"{name}={value}" for name, value in new_cookie.items()])
            newflow2.request.headers["Cookie"] = cookie_header


            if self.qrcode_manager.newqrid != {}:
                new_value = self.qrcode_manager.get_newqrid_value()
                old_value = self.qrcode_manager.get_qrid_value()
                qrid_name = self.qrcode_manager.get_qrid_name()
                newflow2 = self.replace_field(newflow2, old_value, new_value, qrid_name)
            self.qrcode_manager.create_qrcode_flow_replay = newflow2
            ctx.master.commands.call("replay.client", [newflow2])

        
        while self.qrcode_manager.newqrid == {} and self.qrcode_manager.create_qrcode_flow_replay.response is None:
            print("Waiting for replayed create qrcode request response...")
            time.sleep(0.5)
        

        if self.qrcode_manager.newqrid == {} and self.qrcode_manager.create_qrcode_flow_replay.response is not None:
            self.logger.info("[REPLAY]Get response of replayed create qrcode request" + str(self.qrcode_manager.create_qrcode_flow_replay.response))
            content_dict = parse_content(self.qrcode_manager.create_qrcode_flow_replay.response)
            self.logger.info("[REPLAY]content_dict: " + str(content_dict))
            self.logger.info("[DETECT]qrid: " + str(self.qrcode_manager.get_qrid()))
            qrid_name = self.qrcode_manager.qrid_name_in_creation      
            old_value = self.qrcode_manager.get_qrid_value()
            content_dict = flatten_nested_dict(content_dict)
            for key, value in content_dict.items():
                if isinstance(value, dict):
                    for k1, v1 in value.items():
                        if k1 == qrid_name and v1 != old_value:
                            self.qrcode_manager.set_new_qrid(k1, v1)
                elif key == qrid_name:
                    self.qrcode_manager.set_new_qrid(key, value)

            if self.qrcode_manager.get_newqrid() == {}:
                cookie_dict = parse_cookie(self.qrcode_manager.create_qrcode_flow_replay, "response")
                for key, value in cookie_dict.items():
                        if key == qrid_name and value != old_value:
                            self.qrcode_manager.set_new_qrid(key, value)

            self.logger.info("[REPLAY] Found new qrid: " + str(self.qrcode_manager.get_newqrid()))

        newqrid = self.qrcode_manager.get_newqrid()
        if newqrid != {} and self.polling_manager.new_polling_flow_replay is None:     
            qrid_name = self.qrcode_manager.get_newqrid_name()
            new_value = self.qrcode_manager.get_newqrid_value()
            old_value = self.qrcode_manager.get_qrid_value()

            newpollingflow = self.polling_manager.get_polling_flow().copy()

            newpollingflow = self.replace_field(newpollingflow, old_value, new_value, qrid_name)

            print("[REPLAY] send replayed polling request")
            ctx.master.commands.call("replay.client", [newpollingflow])

            self.polling_manager.new_polling_flow_replay = newpollingflow


        while self.polling_manager.new_polling_flow_replay is not None and self.polling_manager.new_polling_flow_replay.response is None:
            print("Waiting for replayed polling request response...")
            time.sleep(0.5)


        if self.polling_manager.new_polling_flow_replay is not None and self.polling_manager.new_polling_flow_replay.response is not None:  
            legal_response = None
            flows = self.traffic_recorder.get_flows()
            for flow_info in flows:
                flow = flow_info[0]
                flow_type = flow_info[1]
                if flow_type == "response":
                    if flow.request.url == self.polling_manager.polling_url and flow.request.method == self.polling_manager.polling_flow.request.method:
                        legal_response = flow.response
                        if not flow.response.content:
                            continue
                        self.logger.info("Found legal response: " + str(decode_content(flow.response.content)))
                        break
            replay_response = self.polling_manager.new_polling_flow_replay.response
            self.logger.info("Replayed new polling response: " + str(decode_content(replay_response.content)))

            parsed_legal_response = parse_content(legal_response)
            parsed_replay_response = parse_content(replay_response)
            self.print_log("F1: parsed_legal_response: " + str(parsed_legal_response))
            self.print_log("F1: parsed_replay_response: " + str(parsed_replay_response))
            legal_response_content = self.filter_response_content(parsed_legal_response)
            replay_response_content = self.filter_response_content(parsed_replay_response)
            
            old_qrid_value = self.qrcode_manager.get_qrid_value()
            new_qrid_value = self.qrcode_manager.get_newqrid_value()
            filter_legal_response = json.dumps(legal_response_content).replace(old_qrid_value, "")
            filter_replay_response_content = json.dumps(replay_response_content).replace(new_qrid_value, "")
 
            self.logger.info("F1: filter_legal_response: " + str(filter_legal_response))
            self.logger.info("F1: filter_replay_response_content: " + str(filter_replay_response_content))
            if json.loads(filter_legal_response) == json.loads(filter_replay_response_content):
                self.logger.info("Flaw F1: Unbound session_id exists!")
                return True
        return False



    def F2_Reusable_qrcode(self):
        print("======= Start detecting flaw F2: Reusable qrcode =======")
        self.logger.info("Start detecting flaw F2: Reusable qrcode")
        
        if self.qrcode_manager.get_qrid() == {} or self.polling_manager.get_polling_flow() is None:
            self.print_log("[F2] Not Ready: Reusable qrcode, qrid is None, polling_flow is None")
            return False
        
        polling_flow_replay = self.polling_manager.polling_flow_replay
        if polling_flow_replay is None:
            copy_polling_flow = self.polling_manager.get_polling_flow().copy()
            print("[REPLAY] send replayed copy polling request")
            ctx.master.commands.call("replay.client", [copy_polling_flow])
            polling_flow_replay = copy_polling_flow

        while polling_flow_replay is not None and polling_flow_replay.response is None:
            print("Waiting for replayed copy polling request response...")
            time.sleep(0.5)

        if polling_flow_replay is not None and polling_flow_replay.response is not None:
            success_response = None
            flows = self.traffic_recorder.get_flows()
            for flow_info in flows[::-1]:
                flow = flow_info[0]
                flow_type = flow_info[1]
                if flow_type == "response":
                    if remove_params_from_url(flow.request.url) == remove_params_from_url(self.polling_manager.polling_url):
                        success_response = flow.response
                        self.polling_manager.set_login_success_response(success_response)
                        self.logger.info("F2: Found success response: " + str(decode_content(flow.response.content)))
                        break
            replay_response = polling_flow_replay.response
            self.logger.info("F2: Replayed polling response: " + str(decode_content(replay_response.content)))


            parsed_success_response = parse_content(success_response)
            parsed_replay_response = parse_content(replay_response)
            self.logger.info("F2: parsed_success_response: " + str(parsed_success_response))
            self.logger.info("F2: parsed_replay_response: " + str(parsed_replay_response))
            
            success_response_content = self.filter_response_content(parsed_success_response)
            replay_response_content = self.filter_response_content(parsed_replay_response)
            
            filter_success_response = json.dumps(success_response_content)
            filter_replay_response_content = json.dumps(replay_response_content)

            self.logger.info("F2: filter_success_response: " + str(filter_success_response))
            self.logger.info("F2: filter_replay_response_content: " + str(filter_replay_response_content))

            if json.loads(filter_success_response) == json.loads(filter_replay_response_content): 
                self.logger.info("Flaw F2: Reusable qrcode exists!")
                return True
        return False



    def F3_Predictable_qr_id(self):
        qrid = self.qrcode_manager.get_qrid()
        if qrid != {}:
            for key, value in qrid.items():
                if len(str(value)) <= 6 and str(value).isdigit():
                    self.logger.info("Flaw F3: Predictable qr_id, " + str(value))
                    return True
        else:
            self.print_log("[F3] Not Ready: Predictable qr_id, qrid is None")
        return False
    


    def F4_Controllable_qr_id(self):
        create_qrcode_flow_info = self.qrcode_manager.get_create_qrcode_flow_info()
        if create_qrcode_flow_info is not None:
            if create_qrcode_flow_info[1] == "request":
                self.logger.info("Flaw F4: Controllable qr_id, " + str(create_qrcode_flow_info))
                return True
        else:
            self.print_log("[F4] Not Ready: Controllable qr_id, create_qrcode_flow_info is None")
        return False
    


    def F5_Invalid_token_Validation(self):
        config = configparser.ConfigParser()
        config.read('credential.ini')
        phone_num = config.get('Credentials', 'phone_num')
        id_card = config.get('Credentials', 'id_card')

        login_request = self.app_flow_manager.get_login_request()
        if login_request != []:
            for flow_info in login_request:
                flow = flow_info[0]
                flow_type = flow_info[1]
                if flow_type == "request":
                    content = decode_content(flow.request.content)
                    if phone_num in content:
                        self.logger.info("Flaw F5: Invalid token Validation, phone_num")
                        self.logger.info(f"Flaw F5: Invalid token Validation, {str(flow.request.url)}\n{str(content)}")
                        return True
                    if id_card in content:
                        self.logger.info("Flaw F5: Invalid token Validation, id_card")
                        self.logger.info(f"Flaw F5: Invalid token Validation, {str(flow.request.url)}\n{str(content)}")
                        return True
        else:
            self.print_log("[F5] Not Ready: Invalid token Validation, login_request is None")
        return False
                    


    def F6_Sensitive_Data_Leakage(self):
        config = configparser.ConfigParser()
        config.read('credential.ini')      
        start_search_flag = False
        leaked_info = []
        flows = self.traffic_recorder.get_flows()
        for field, value in config.items('Credentials'):
            for flow_info in flows:
                flow = flow_info[0]
                flow_type = flow_info[1]
                if flow_type == "response":     
                    if flow.request.url == self.polling_manager.get_polling_url(): 
                        start_search_flag = True
                    if not start_search_flag:
                        continue

                    if flow.request.method == "GET" and flow.request.url.endswith(('.jpg', '.png', '.css', '.js')):
                        continue

                    if search(flow, flow_type, value) != "":
                        leaked_info.append(field)
                        self.logger.info(f"Flaw F6: Sensitive Data Leakage, {field}")
                        self.logger.info(f"Flaw F6: Sensitive Data Leakage, {str(flow.request.url)}\n{str(decode_content(flow.response.content))}")
                        break
        return leaked_info
        


    def filter_response_content(self, content_dict):
        filter_list = ['traceid', 'token', 'sign']
        flatten_content_dict = flatten_nested_dict(content_dict)
        for k, v in flatten_content_dict.items():
            for item in filter_list:
                if item == k.replace('-','').lower():
                    flatten_content_dict[k] = ''
                if is_timestamp(v):    
                    flatten_content_dict[k] = '' 

            if isinstance(v, str):
                if v.startswith("http") or "://" in v:
                    url = v
                    parsed_url = urlparse(url)
                    params = dict(parse_qsl(parsed_url.query)) 
                    for key, value in params.items():
                        if len(value) >= 30:
                            flatten_content_dict[k] = flatten_content_dict[k].replace(value, '')
                else:
                    if len(v) >= 30:
                        flatten_content_dict[k] = ''
        return flatten_content_dict


    
        
    
    def replace_field(self, flow, old_value, new_value, qrid_name):
        qrid_name_in_poll = self.qrcode_manager.qrid_name_in_poll

        content = parse_content(flow.request)
        if content and old_value in str(content): 
            for key in content.keys():
                if qrid_name in key or qrid_name_in_poll in key:
                    content[key] = new_value
            
            if 'application/x-www-form-urlencoded' in flow.request.headers.get('Content-Type', ''):
                flow.request.content = urllib.parse.urlencode(content).encode()
            elif 'application/json' in flow.request.headers.get('Content-Type', ''):
                flow.request.content = json.dumps(content).encode()
        
        flow.request.url = flow.request.url.replace(old_value, quote(new_value))

        cookie_dict = parse_cookie(flow, "request")
        for key, value in cookie_dict.items():
            if (key == qrid_name or key == qrid_name_in_poll) and value == old_value:
                cookie_dict[key] = new_value
        new_cookie_header = "; ".join([f"{name}={value}" for name, value in cookie_dict.items()])
        flow.request.headers["Cookie"] = new_cookie_header
        return flow


    def print_log(self, content):
        print(content)
        self.logger.info(content)


    
