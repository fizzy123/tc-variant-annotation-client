# This method will be used by the mock to replace requests.get
def mocked_requests_get_wrapper(response_dict):
    def mocked_requests_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code, text):
                self.json_data = json_data
                self.status_code = status_code
                self.text = text
                self.ok = self.status_code < 400
    
            def json(self):
                return self.json_data
            
            def text(self):
                return self.text

        for key, value in response_dict.items():
            if args[0] == key:
                return MockResponse(value.get("json"), value.get("status_code"), value.get("text"))
    return mocked_requests_get
