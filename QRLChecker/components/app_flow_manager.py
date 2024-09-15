class AppFlowManager:
    def __init__(self):
        self.authorization_url = ""
        self.app_flows = []
        self.login_request = []  

    def set_authorization_url(self, url):
        self.authorization_url = url

    def add_app_flow(self, flow, type):
        self.app_flows.append([flow, type])

    def add_login_request(self, request):
        self.login_request.append(request)

    def get_app_flows(self):
        return self.app_flows
    
    def get_login_request(self):
        return self.login_request
    
    def get_authorization_url(self):
        return self.authorization_url