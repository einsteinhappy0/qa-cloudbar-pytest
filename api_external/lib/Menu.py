#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from typing import Dict, Any, List, Optional

from api_external.lib.APIEndpointBase import APIEndpointBase
from api_external.lib.CommonUtils import StringUtils, APIUtils
from api_external.lib.JSONSchemaLibrary import JSONSchemaLibrary
from api_path import *


ModelPump = {
    'DrinkBot_Pro-4.1': {'fridge_capacity': 8, 'room_capacity': 2},
    'DrinkBot_Pro-4.6': {'fridge_capacity': 6, 'room_capacity': 6},
    'DrinkBot_Pro-4.x': {'fridge_capacity': 8, 'room_capacity': 4},
    'DrinkBot_Mini-8-0': {'fridge_capacity': 0, 'room_capacity': 8}
}


class Menu(APIEndpointBase):
    """Handles menu-related API operations"""
    
    LIST_API_PATH = ApiPath.MENU_LIST
    DETAIL_API_PATH = ApiPath.MENU_DETAIL
    
    def __init__(self):
        super().__init__()
        self._menu_id: str = ''
        self._model = None
        self._country = None
        self._drink_create_payload = []
        self._drink_update_payload = []

    def _menu_pump(self, country, model, drink_skus):
        pump_data = {
            "sku": drink_skus,
            "filter": {"sku": "", "name": "", "drink_category_id": [], "flavor": []},
            "country": country,
            "version": model,
            "drink_mode": True,
            "add_on": [],
            "pump": ModelPump[model]
        }
        resp = APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(ApiPath.MENU_PUMP),
            Method.POST,
            ResponseCode.OK,
            None,
            data=pump_data
        )
        return resp
    
    
    def _prepare_create_payload(self) -> bool:
        """Update create payload with randomized data"""
        menu_name = f"QATest_Menu_{StringUtils.random_string(5, 'UPPER')}"
        self._model = random.choice(list(ModelPump))
        self._country = random.choice(list(Country)).value
        added_sku_list = []
        for _ in range(2):
            menu_pump_resp = self._menu_pump(self._country, self._model, added_sku_list)
            new_drink = random.choice(menu_pump_resp.json()['data']['available'])
            for key in ['country', 'date_modified', 'description', 'ingredient', 'flavor', 'status', 'photo']:
                new_drink.pop(key)
            self._drink_create_payload.append(new_drink)
            added_sku_list.append(new_drink['sku'])
        
        self.create_payload.update({
            'name': menu_name,
            'add_on': [],
            'country': self._country,
            'drinks': added_sku_list,
            'target_model': self._model,
        })
        return True
    
    def _prepare_update_payload(self) -> bool:
        """Prepare payload for updating a menu"""
        added_sku_list = []
        for _ in range(2):
            menu_pump_resp = self._menu_pump(self._country, self._model, added_sku_list)
            new_drink = random.choice(menu_pump_resp.json()['data']['available'])
            for key in ['country', 'date_modified', 'description', 'ingredient', 'flavor', 'status', 'photo']:
                new_drink.pop(key)
            self._drink_update_payload.append(new_drink)
            added_sku_list.append(new_drink['sku'])
            
        self.update_payload = {
            'drinks': added_sku_list,
            # Add other updateable fields here
        }
        self.info_data.update(self.update_payload)
        return True
    
    def _set_resource_id(self, response: Dict[str, Any]) -> None:
        """Store the menu ID from response"""
        self._menu_id = response.json()['data']['id']  # Adjust based on actual response structure
    
    def _execute_create_request(self) -> Dict[str, Any]:
        """Execute the create menu API request"""
        return APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(self.LIST_API_PATH),
            Method.POST,
            ResponseCode.OK,
            None,
            data=self.create_payload
        )
    
    def _execute_update_request(self) -> Dict[str, Any]:
        """Execute the update menu API request"""
        return APIUtils.call_api_and_assert_status_code(
            self.generate_detail_path_info(self._menu_id),
            Method.PUT,  # or PATCH depending on your API
            ResponseCode.OK,
            None,
            data=self.update_payload
        )
    
    def delete(self) -> Any:
        """Delete a menu through the API"""
        response = APIUtils.call_api_and_assert_status_code(
            self.generate_detail_path_info(self._menu_id),
            Method.DELETE,
            ResponseCode.OK
        )
        return response
    
    @classmethod
    def _prepare_get_list_parameters(cls) -> List[tuple]:
        """Prepare parameters for listing menus"""
        total = cls._get_total_items()
        field_list = JSONSchemaLibrary(cls.LIST_API_PATH).get_request_fields_schema()
        
        params = [('fields[]', f) for f in field_list]
        params.extend([
            ('amount', total),
            ('status', 'active')
        ])
        return params
    
    @classmethod
    def _get_total_items(cls) -> int:
        """Get total number of menus"""
        response = APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(cls.LIST_API_PATH),
            Method.GET,
            ResponseCode.OK,
            params={'amount': 1}
        )
        return response.json()['data']['total']  # Adjust based on actual response structure
    
    @classmethod
    def generate_detail_path_info(cls, menu_id: str) -> ApiPathInfo:
        """Generate the detail endpoint path with menu ID"""
        return ApiPathInfo(cls.DETAIL_API_PATH, {'id': menu_id})  # Adjust parameter name if needed
    
    @classmethod
    def get_random_resource_id(cls) -> str:
        """Get a random menu ID from the list"""
        response = cls.read_list()
        menus = response.json()['data']['menus']  # Adjust based on actual response structure
        if not menus:
            return ""
        random_menu = random.choice(menus)
        return random_menu['_id']  # Adjust field name if needed
    
    @property
    def resource_id(self) -> str:
        """Get the menu's unique identifier"""
        return self._menu_id
    
    def create(self) -> Any:
        resp = super().create()
        if resp:
            self.info_data['drinks'] = self._drink_create_payload
        return resp
    
    def update(self) -> Any:
        resp = super().update()
        if resp:
            self.info_data['drinks'] = self._drink_update_payload
        return resp
        
    def assign_to_machines(self, machines: List[Any]) -> Any:
        batch_payload = {
            'menu_id': self._menu_id,
            'serial_num': machines
        }
        resp = APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(ApiPath.MENU_BATCH),
            Method.POST,
            ResponseCode.OK,
            None,
            data=batch_payload
        )
        return resp