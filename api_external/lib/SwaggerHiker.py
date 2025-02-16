#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import os
import constant
from api_path import *
from api_external.lib.HttpRequestInit import HttpRequestInit


class SwaggerHiker(object):
    
    def __init__(self):
        self.backend_host = constant.BACKEND_HOST
        self.swagger_host_list = constant.SWAGGER_HOST_LIST
        self.json_path = constant.SWAGGER_JSON_PATH
        self.schema_file_path = constant.SCHEMA_FILE_PATH
        self.http_session = HttpRequestInit(self.backend_host)
    
    # ---------------------------------------------------------------------------
    def swagger_get_schema(self):
        resp = self.http_session.request(
            'GET',
            f'/{self.json_path}'
        )
        with open(self.schema_file_path, 'w') as schema_file:
            schema_file.write(resp.text)
    
    def swagger_get_auth(self, token_type, token_action='access'):
        if token_type == TokenType.USER_TOKEN:
            credential = {
                'user_name': constant.TEST_USER_NAME_ACCOUNT,
                'password': constant.TEST_USER_ACCOUNT
            }
            self.http_session.user_auth_header(token_type, credential)
        else:
            self.http_session.machine_auth_header()
    
    def swagger_search(self, path, method, header=None, **kwargs):
        if header:
            self.http_session.add_headers(header)
        
        if "data" in kwargs:
            kwargs["data"] = json.dumps(kwargs["data"])
        
        resp = self.http_session.request(
            method, path, **kwargs
        )
        
        # print(resp.status_code)
        # print(resp.json())
        return resp