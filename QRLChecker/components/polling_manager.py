class PollingManager:
    def __init__(self):
        
        self.polling_url = ""
        self.polling_flow = None  
        self.new_polling_flow_replay = None  
        self.polling_flow_replay = None  

        self.polling_resp_indicator = ""
        self.polling_resp_status = {}

    def set_polling_url(self, url):
        self.polling_url = url
    
    def set_polling_flow(self, flow):
        self.polling_flow = flow
        self.polling_url = flow.request.url
    
    def set_polling_flow_replay(self, flow):
        self.polling_flow_replay = flow
    
    def set_new_polling_flow_replay(self, flow):
        self.new_polling_flow_replay = flow
    
    def set_polling_resp_indicator(self, indicator):
        self.polling_resp_indicator = indicator

    def set_polling_resp_status(self, status):
        self.polling_resp_status = status
    
    def clear_polling_flow(self):
        self.polling_flow = None
        self.polling_url = ""


    def get_polling_flow(self):
        return self.polling_flow

    def get_polling_url(self):
        return self.polling_url
    
    def get_polling_flow_replay(self):
        return self.polling_flow_replay
    
    def get_new_polling_flow_replay(self):
        return self.new_polling_flow_replay
    
    def get_polling_resp_indicator(self):
        return self.polling_resp_indicator
    
    def get_polling_resp_status(self):
        return self.polling_resp_status