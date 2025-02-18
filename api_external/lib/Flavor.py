from importlib import resources
import json
import random
from typing import Dict, Any, List, Tuple, Optional

from api_path import ApiPath, ApiPathInfo, Method, ResponseCode
from api_external.lib.APIEndpointBase import APIEndpointBase
from api_external.lib.CommonUtils import StringUtils, APIUtils


class Flavor(APIEndpointBase):
    """Handles flavor-related API operations"""
    
    LIST_API_PATH = ApiPath.FLAVOR_LIST
    DETAIL_API_PATH = ApiPath.FLAVOR_DETAIL
    
    def __init__(self):
        super().__init__()
        self._flavor_sku: str = ''
    
    def _get_flavor_types(self) -> List[Tuple[str, str]]:
        """Get available flavor types excluding 'FIL'"""
        resp = APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(ApiPath.FLAVOR_CLASS_TYPE),
            Method.GET,
            ResponseCode.OK
        )
        flavor_types = [
            (item['key'], item['value'])
            for item in resp.json()['data']
            if item['key'] != 'FIL'
        ]
        return flavor_types
    
    def _get_flavor_vendors(self) -> List[Dict[str, str]]:
        """Get available flavor vendors"""
        response = APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(ApiPath.FLAVOR_VENDORS),
            Method.GET,
            ResponseCode.OK
        )
        return response.json()['data']
    
    def _prepare_create_payload(self) -> bool:
        """Prepare payload for creating a new flavor"""
        if not self.create_payload:
            with resources.open_text("api_external.res.create_data", 'create_flavor.json') as res:
                self.create_payload = json.load(fp=res)
        if not self.create_payload:
            return False
        self.create_payload = dict(self.create_payload)
        
        self._update_create_payload_with_random_data()
        return True
    
    def _update_create_payload_with_random_data(self) -> None:
        """Update create payload with randomized data"""
        sku = StringUtils.random_string(4, 'UPPER')
        name = f'Testing-{sku}'
        
        type_item = random.choice(self._get_flavor_types())
        vendor_item = random.choice(self._get_flavor_vendors())
        
        self.create_payload.update({
            "sku": sku,
            "name": name,
            "class": type_item[0],
            "type": type_item[1],
            "vendor_code": vendor_item['code'],
            "vendor": vendor_item['name'],
            "vendor_abbr": vendor_item['abbr'],
            "country": vendor_item['country']
        })
    
    def _prepare_update_payload(self) -> bool:
        """Prepare payload for updating a flavor"""
        with resources.open_text("api_external.res.create_data", 'update_flavor.json') as res:
            self.update_payload = json.load(fp=res)
        if not self.update_payload:
            return False
        
        self.update_payload['name'] = f"TestEdit_{self.info_data['name']}"
        return True
    
    def _set_resource_id(self, response: Dict[str, Any]) -> None:
        """Store the flavor SKU from response"""
        self._flavor_sku = response.json()['data']['sku']
    
    def _execute_create_request(self) -> Dict[str, Any]:
        """Execute the create flavor API request"""
        resp = APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(self.LIST_API_PATH),
            Method.POST,
            ResponseCode.OK,
            data=self.create_payload
        )
        return resp
    
    def create(self) -> Any:
        resp = super().create()
        if resp:
            self.info_data.pop('sku')
        return resp
    
    def _execute_update_request(self) -> Dict[str, Any]:
        """Execute the update flavor API request"""
        path_info = self.__class__.generate_detail_path_info(self._flavor_sku)
        resp = APIUtils.call_api_and_assert_status_code(
            path_info,
            Method.PUT,
            ResponseCode.OK,
            data=self.update_payload
        )
        return resp
    
    def delete(self) -> bool:
        """Delete a flavor through the API"""
        response = APIUtils.call_api_and_assert_status_code(
            self.generate_detail_path_info(self._flavor_sku),
            Method.DELETE,
            ResponseCode.OK
        )
        return bool(response)
    
    @classmethod
    def _prepare_get_list_parameters(cls) -> List[tuple]:
        """Prepare parameters for listing flavors"""
        total = cls._get_item_amount()
        return [
            ('amount', total),
            ('status', 'active')
        ]
    
    @classmethod
    def generate_detail_path_info(cls, sku: str) -> ApiPathInfo:
        """Generate the detail endpoint path with SKU"""
        return ApiPathInfo(cls.DETAIL_API_PATH, {'sku': sku})
    
    @classmethod
    def get_random_resource_id(cls) -> str:
        """Get a random flavor SKU from the list"""
        response = cls.read_list()
        flavors = response.json()['data']['flavors']
        if not flavors:
            return None
        random_flavor = random.choice(flavors)
        return random_flavor['full_sku']
    
    @property
    def resource_id(self) -> str:
        """Get the flavor's unique identifier"""
        return self._flavor_sku
    
    @classmethod
    def _prepare_get_detail_parameters(cls) -> dict | list:
        return []