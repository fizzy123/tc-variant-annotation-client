# This method will be used by the mock to replace requests.get
def mocked_requests_get_wrapper(response_dict):
    def mocked_requests_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code
    
            def json(self):
                return self.json_data
    
        print(response_dict)
        for key, value in response_dict.items():
            if args[0] == key:
                return MockResponse(value["json"], value["status_code"])
    return mocked_requests_get
