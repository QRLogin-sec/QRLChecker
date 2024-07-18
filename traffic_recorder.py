import os
import urllib.parse
from utils import *

class TrafficRecorder:
    def __init__(self, url, logger, debuggable=True):
        self.url = url
        self.debuggable = debuggable
        self.logger = logger
        
        os.makedirs("./logs", exist_ok=True)
        self.traffic_recording = f"./logs/traffic_{urllib.parse.quote(url, safe='')}.txt"
        if os.path.exists(self.traffic_recording):
            os.remove(self.traffic_recording)
        
        self.flows = []  

        self.url_counts = {}  

    def record_flow(self, flow, flow_type):
        self.flows.append([flow, flow_type])

    def get_traffic_recording(self):
        return self.traffic_recording

    def get_flows(self):
        return self.flows
    
    
    def update_url_counts(self, url):
        if url in self.url_counts:
            self.url_counts[url] += 1
        else:
            self.url_counts[url] = 1


    def sort_url_counts_by_frequency(self):
        """
        Sort URL counts based on frequency of appearance
        """
        filtered_url_counts = {}
        for url, cnt in self.url_counts.items():
            filtered_url = remove_params_from_url(url)
            filtered_url_counts[filtered_url] = filtered_url_counts.get(filtered_url, 0) + self.url_counts[url]
        sorted_url_counts = sorted(filtered_url_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_url_counts



    def build_url_flow_map(self):
        url_flow_map = {}
        for flow_info in self.flows:
            flow = flow_info[0]
            flow_type = flow_info[1]
            if flow_type == "request":
                url = remove_params_from_url(flow.request.url)
                url_flow_map[url] = url_flow_map.get(url, []) + [flow]
        return url_flow_map
    

    def write_log_request(self, flow):
        if not self.debuggable:
            return
        with open(self.traffic_recording, "a") as f:
            f.write(f"\n[Request{self.num}]{flow.request.url}\n")
            f.write(f"Method: {flow.request.method}\n")
            self.logger.debug(f"\n[Request{self.num}]\n{flow.request.url}")
            self.logger.debug(f"Method: {flow.request.method}")

            headers = dict(flow.request.headers)
            for key in headers:
                f.write(f"{key}: {headers[key]}\n")
                self.logger.debug(f"{key}: {headers[key]}")
                
            if flow.request.content:
                decoded_content = decode_content(flow.request.content)
                f.write(f"Body:$$${decoded_content}$$$")
                self.logger.debug(f"Body:$$${decoded_content}$$$\n")
            else:
                pass
            f.write("\n\n\n\n")
    
    
    def write_log_response(self, flow):
        if not self.debuggable:
            return
        with open(self.traffic_recording, "a", encoding="utf-8") as f:
            f.write(f"\n[Response]\n{flow.request.url}\n")
            self.logger.debug(f"\n[Response]{flow.request.url}")

            headers = dict(flow.response.headers)
            for key in headers:
                f.write(f"{key}: {headers[key]}\n")
                self.logger.debug(f"{key}: {headers[key]}")

            if flow.response.content:
                decoded_content = decode_content(flow.response.content)
                f.write(f"Body:$$${decoded_content}$$$")
                self.logger.debug(f"Body:$$${decoded_content}$$$\n")
            else:
                pass
            f.write("\n\n\n\n")