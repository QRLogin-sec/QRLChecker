class PollingManager:
    def __init__(self):
        
        self.polling_url = ""
        self.polling_flow = None  
        self.new_polling_flow_replay = None  
        self.polling_flow_replay = None  
        self.login_success_response = None  

    
    def set_polling_flow(self, flow):
        self.polling_flow = flow
        self.polling_url = flow.request.url
    
    def clear_polling_flow(self):
        self.polling_flow = None
        self.polling_url = ""

    def set_login_success_response(self, response):
        self.login_success_response = response

    def get_polling_flow(self):
        return self.polling_flow

    def get_polling_url(self):
        return self.polling_url
    
