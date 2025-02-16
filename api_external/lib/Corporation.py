from importlib import resources
import json
import random
from typing import Dict, Any, List, Optional
import api_external.lib.User as User

from api_path import ApiPath, ApiPathInfo, Method, ResponseCode, Country
from api_external.lib.APIEndpointBase import APIEndpointBase
from api_external.lib.CommonUtils import StringUtils, APIUtils


class Corporation(APIEndpointBase):
    """Handles corporation-related API operations"""
    
    LIST_API_PATH = ApiPath.CORP_LIST
    DETAIL_API_PATH = ApiPath.CORP_DETAIL
    OLD_LIST_API_PATH = ApiPath.USER_LIST_BY_TYPE
    
    def __init__(self):
        super().__init__()
        self._corp_name: str = ''
    
    def _prepare_create_payload(self) -> bool:
        """Prepare payload for creating a new corporation"""
        if not self.create_payload:
            """Load default creation data from JSON file"""
            with resources.open_text("api_external.res.create_data", 'create_corporation.json') as res:
                self.create_payload = json.load(fp=res)
        if not self.create_payload:
            return False
        
        self.create_payload = dict(self.create_payload)
        self._update_create_payload_with_random_data()
        return True
    
    def _update_create_payload_with_random_data(self) -> None:
        """Update create payload with randomized data"""
        user_name = StringUtils.random_string(10, 'LOWER')
        email = f'{user_name}@botrista.com'
        location_prefix = StringUtils.random_string(5, 'UPPER')
        corp_type = "Headquarter"
        
        self.create_payload.update({
            'name': f'test_{user_name}',
            'user_name': f'test_{user_name}',
            'type': corp_type,
            'country': random.choice(list(Country)).value,
            'email': email,
            'phone_number': StringUtils.random_string(10, 'NUMBER'),
            'owner_name': StringUtils.random_string(10, 'LOWER'),
            'location_prefix': location_prefix
        })
    
    def _prepare_update_payload(self) -> bool:
        """Prepare payload for updating a corporation"""
        name = StringUtils.random_string(10, 'LOWER')
        email = f'{name}@botrista.com'
        multi_email = self.info_data.get('multi_email', []) + ['example3@mail.com']
        
        self.update_payload = {
            "name": name,
            "email": email,
            "phone_number": StringUtils.random_string(10, 'NUMBER'),
            "owner_name": StringUtils.random_string(10, 'LOWER'),
            "adjust_to_cup_size": random.choice([True, False]),
            "subscribe": random.choice([True, False]),
            "subscribe_daily": random.choice([True, False]),
            "account_manager": "qatestingfae",
            "order_term": "Net 15",
            "multi_email": multi_email,
            "subscribe_sales": random.choice([True, False]),
            "subscribe_weekly": random.choice([True, False]),
            "alert_mute": random.choice([True, False]),
            "contract_status": "Demo",
            "company_logo": "https://www.example.com/logo2.png",
            "screen_saver": "https://www.example.com/screen_saver2.png"
        }
        return True
    
    def _set_resource_id(self, response: Dict[str, Any]) -> None:
        """Store the corporation username from response"""
        self._corp_name = response.json()['data']['user_name']
    
    def _execute_create_request(self) -> Dict[str, Any]:
        """Execute the create corporation API request"""
        return APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(self.__class__.LIST_API_PATH),
            Method.POST,
            ResponseCode.OK,
            None,
            data=self.create_payload
        )
    
    def _execute_update_request(self) -> Dict[str, Any]:
        """Execute the update corporation API request"""
        return APIUtils.call_api_and_assert_status_code(
            self.generate_detail_path_info(self._corp_name),
            Method.PUT,
            ResponseCode.OK,
            None,
            data=self.update_payload
        )
    
    def delete(self) -> bool:
        """Delete (deactivate) a corporation through the API"""
        response = APIUtils.call_api_and_assert_status_code(
            self.generate_detail_path_info(self._corp_name),
            Method.PUT,
            ResponseCode.OK,
            None,
            data={'status': 'inactive'}
        )
        return bool(response)
    
    @classmethod
    def read_list(cls) -> Dict[str, Any]:
        """Read/retrieve list of corporations from the API"""
        return APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(cls.OLD_LIST_API_PATH, {'type': 'Headquarter'}),
            Method.GET,
            ResponseCode.OK,
        )
    
    @classmethod
    def generate_detail_path_info(cls, user_name: str) -> ApiPathInfo:
        """Generate the detail endpoint path with username"""
        return ApiPathInfo(cls.DETAIL_API_PATH, {'user_name': user_name})
    
    @classmethod
    def get_random_resource_id(cls) -> str:
        """Get a random corporation username from the list"""
        response = cls.read_list()
        corporations = response.json()['data']
        if not corporations:
            return ""
        random_corp = random.choice(corporations)
        return random_corp['user_name']
    
    @property
    def resource_id(self) -> str:
        """Get the corporation's unique identifier"""
        return self._corp_name
    
    def _prepare_get_list_parameters(cls) -> dict | list:
        return []
    
    @classmethod
    def _prepare_get_detail_parameters(cls) -> dict | list:
        return []
    
    @classmethod
    def read_detail(cls, resource_id) -> Any:
        return User.read_detail(resource_id)
    
    def delete(self) -> bool:
        """Deactivate (soft delete) a user"""
        response = APIUtils.call_api_and_assert_status_code(
            self.__class__.generate_detail_path_info(self._corp_name),
            Method.PUT,
            ResponseCode.OK,
            None,
            data={'status': 'inactive'}
        )
        return bool(response)