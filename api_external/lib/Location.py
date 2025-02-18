#!/usr/bin/env python
# -*- coding: utf-8 -*-
from importlib import resources
import json
from api_external.lib.APIEndpointBase import APIEndpointBase
from api_external.lib.CommonUtils import StringUtils
from api_external.lib.CommonUtils import APIUtils
from api_path import *
import time
import constant
import random
from datetime import datetime, timezone


class Location(APIEndpointBase):
    LIST_API_PATH = ApiPath.LOCATION_LIST
    DETAIL_API_PATH = ApiPath.LOCATION_DETAIL
    
    def __init__(self):
        super().__init__()
        self._location_id = ''
        self._user_name = constant.TEST_HQ_USER_NAME
    
    def _prepare_create_payload(self):
        # lack field: incoming_call_contacts
        if not self.create_payload:
            with resources.open_text("api_external.res.create_data", 'create_location.json') as res:
                self.create_payload = json.load(fp=res)
        if not self.create_payload:
            return False
        self.create_payload = dict(self.create_payload)
        
        province = StringUtils.random_string(2, 'UPPER')
        name = StringUtils.random_string(5, 'LOWER')
        secs = int(time.time())
        phone = StringUtils.random_string(9, 'NUMBER')
        address = StringUtils.random_string(20, 'LETTER')
        store_code = StringUtils.random_string(6, 'NUMBER')
        zip_code = StringUtils.random_string(3, 'NUMBER')
        email = f'{name}@gmail.com'
        location_name = f'{name}{secs}'
        self.create_payload.update({
            'city': location_name,
            'contact_email': email,
            'contact_name': location_name,
            'contact_phone': phone,
            'name': location_name,
            # 'province': province,
            'province': 'NY',
            'store_code': store_code,
            'user_name': self._user_name,
            'zip_code': zip_code,
            'address': address,
        })
        return True
    
    def __edit_launch_decommission_time(self):
        # Get the current time in UTC
        now_utc = datetime.now(timezone.utc)
        # Format the datetime in ISO 8601 with milliseconds and 'Z'
        formatted_time = now_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        self.update_payload.update({
            'launch_time': formatted_time,
            'decommission_time': formatted_time
        })
    
    def _set_resource_id(self, resp):
        resp_dict = resp.json()
        self._location_id = resp_dict['data']['full_code']
    
    def _prepare_update_payload(self):
        name = StringUtils.random_string(5, 'LOWER')
        secs = int(time.time())
        phone = StringUtils.random_string(9, 'NUMBER')
        zip_code = StringUtils.random_string(3, 'NUMBER')
        email = f'{name}@gmail.com'
        
        multi_email = [
            f"{StringUtils.random_string(5, 'LOWER')}@gmail.com",
            f"{StringUtils.random_string(5, 'LOWER')}@gmail.com"
        ]
        location_name = f'{name}{secs}'
        address = StringUtils.random_string(20, 'LETTER')
        
        # Get the current time in UTC
        now_utc = datetime.now(timezone.utc)
        # Format the datetime in ISO 8601 with milliseconds and 'Z'
        formatted_time = now_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        
        self.update_payload.update({
            'name': name,
            'address': address,
            'city': location_name,
            'contact_email': email,
            'contact_name': location_name,
            'contact_phone': phone,
            'filter_program': random.choice([True, False]),
            'free_shipping': random.choice([True, False]),
            'no_sale_mute': random.choice([True, False]),
            'order_bib_system': random.choice([True, False]),
            'sell_acce': random.choice([True, False]),
            'sell_topping': random.choice([True, False]),
            # 'selling_item':,
            'zip_code': zip_code,
            'subscribe_order': random.choice([True, False]),
            'subscribe_sales': random.choice([True, False]),
            'multi_email': multi_email,
            'vip': random.choice([True, False]),
            'launch_time': formatted_time,
            'decommission_time': formatted_time,
        })
        
        return True
    
    def _execute_update_request(self):
        path_info = self.__class__.generate_detail_path_info(self._location_id)
        resp = APIUtils.call_api_and_assert_status_code(
            path_info,
            Method.PATCH,
            ResponseCode.OK,
            None,
            data=self.update_payload
        )
        return resp
    
    def delete(self):
        path_info = self.__class__.generate_detail_path_info(self._location_id)
        resp = APIUtils.call_api_and_assert_status_code(
            path_info,
            Method.DELETE,
            ResponseCode.OK,
        )
        return resp
    
    @classmethod
    def _prepare_get_list_parameters(cls):
        total = cls._get_item_amount()
        params = cls._prepare_get_detail_parameters()
        params += [('amount', total), ('status', 'active')]
        return params
    
    @classmethod
    def generate_detail_path_info(cls, full_code):
        return ApiPathInfo(cls.DETAIL_API_PATH, {'full_code': full_code})
    
    @classmethod
    def get_random_resource_id(cls):
        location_list_resp = cls.read_list().json()
        location_list = location_list_resp['data']['locations']
        if len(location_list) == 0:
            return None
        random_location = random.choice(location_list)
        return random_location['full_code']
    
    @property
    def resource_id(self):
        return self._location_id
        
    def set_user_name(self, user_name):
        self._user_name = user_name
        
    def get_drink_settings(self, menu_id):
        path_info = ApiPathInfo(ApiPath.LOCATION_DRINK_SETTINGS, {'full_code': self._location_id})
        resp = APIUtils.call_api_and_assert_status_code(
            path_info,
            Method.GET,
            ResponseCode.OK,
            None,
            params={'menu_id': menu_id}
        )
        return resp