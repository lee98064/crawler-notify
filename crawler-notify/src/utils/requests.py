import requests

class BaseUrlSession(requests.Session):
    def __init__(self, base_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = base_url

    def request(self, method, url, *args, **kwargs):
        full_url = self.base_url + url
        return super().request(method, full_url, *args, **kwargs)