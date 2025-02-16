import json

import requests
import logging
import urllib3
from api_path import ResponseCode


# urllib3.disable_warnings()


class HttpRequestInit:
    
    def __init__(self, host='', basepath=''):
        self.HOST = host + basepath
        self.TOKEN = None
        self.REFRESH_TOKEN = None
        self.SESSION = requests.Session()
        self.SESSION.headers.update({
            'content-type': 'application/json',
            'accept': 'application/json',
        })
    
    def set_host(self, url):
        self.HOST = url[:]
    
    def get_curl(self, req):
        method = req.method
        uri = req.url
        data = req.body
        headers = ['"{0}: {1}"'.format(k, v) for k, v in req.headers.items()]
        headers = " -H ".join(headers)
        
        if method == "GET":
            command = "curl -X {method} -H {headers} '{uri}'"
        else:
            command = "curl -X {method} -H {headers} -d '{data}' '{uri}'"
        
        return command.format(method=method, headers=headers, data=data, uri=uri)
    
    def request(self, method, path='', **kwargs):
        url = self.HOST + path
        resp = self.SESSION.request(method, url, **kwargs)
        # logging.info(self.get_curl(resp.request))
        print('=' * 60)
        print(f'Request: {self.get_curl(resp.request)}')
        if resp.status_code != ResponseCode.NOT_FOUND.value:
            print(f'Response: {resp.json()}')
        return resp
    
    def add_headers(self, others):
        self.SESSION.headers.update(others)
    
    def machine_auth_header(self):
        pass
    
    def user_auth_header(self, token_type, credential):
        resp = self.request('POST', '/login', data=json.dumps(credential))
        if resp.status_code != 200:
            print(resp.status_code)
            print(resp.json())
            return None
        if token_type == 'refresh':
            token = resp.json()['data']['refreshToken']
        token = resp.json()['data']['accessToken']
        self.SESSION.headers.update({'Authorization': 'Bearer ' + token})