from enum import Enum
import random
from typing import Dict, Any, List
from api_path import *
from api_path import ApiPath, ApiPathInfo, Method, ResponseCode
from api_external.lib.APIEndpointBase import APIEndpointBase
from api_external.lib.CommonUtils import StringUtils, APIUtils
from api_external.lib.JSONSchemaLibrary import JSONSchemaLibrary


class UserType(Enum):
    BOT = 'Botrista'
    FAE = 'FAE'
    OP = 'Operation'
    DIST = 'Distributor'


class UserUnit(Enum):
    IMP = 'imperial'
    MET = 'metric'


class User(APIEndpointBase):
    """Handles user-related API operations"""
    
    LIST_API_PATH = ApiPath.USER_LIST
    DETAIL_API_PATH = ApiPath.USER_DETAIL
    UPDATE_API_PATH = ApiPath.USER_UPDATE
    
    def __init__(self):
        super().__init__()
        self._username: str = ''
    
    def _prepare_create_payload(self) -> bool:
        """Prepare payload for creating a new user"""
        name = StringUtils.random_string(10, 'LOWER')
        password = StringUtils.random_string(10, 'ALL')
        country = random.choice(list(Country)).value
        
        self.create_payload.update({
            'name': f'test_{name}',
            'user_name': f'test_{name}',
            'password': password,
            'password_confirmation': password,
            'type': random.choice(list(UserType)).value,
            'country': country,
            'email': f'{name}@botrista.com',
            'status': 'active',
            'prefer_unit': random.choice(list(UserUnit)).value,
            'adjust_to_cup_size': True,
            'subscribe': True,
            'alert_mute': True
        })
        
        return True
        
    def create(self) -> Any:
        resp = super().create()
        if resp:
            self.info_data.pop('password', None)
            self.info_data.pop('password_confirmation', None)
        return resp
    
    def _prepare_update_payload(self) -> bool:
        """Prepare payload for updating a user"""
        name = StringUtils.random_string(10, 'LOWER')
        country = random.choice(list(Country)).value
        self.update_payload.update({
            'name': name,
            'type': random.choice(list(UserType)).value,
            'country': country,
            'prefer_unit': random.choice(list(UserUnit)).value,
            'adjust_to_cup_size': random.choice([True, False]),
            'subscribe': random.choice([True, False]),
            'alert_mute': random.choice([True, False])
        })
        
        return True
    
    def _set_resource_id(self, response: Dict[str, Any]) -> None:
        """Store the username from response"""
        self._username = response.json()['data']['user_name']
    
    def _execute_update_request(self) -> Dict[str, Any]:
        """Execute the update user API request"""
        return APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(self.UPDATE_API_PATH, {'user_name': self._username}),
            Method.PUT,
            ResponseCode.OK,
            None,
            data=self.update_payload
        )
    
    def delete(self) -> bool:
        """Deactivate (soft delete) a user"""
        response = APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(self.UPDATE_API_PATH, {'user_name': self._username}),
            Method.PUT,
            ResponseCode.OK,
            None,
            data={'status': 'inactive'}
        )
        return bool(response)
    
    @classmethod
    def _prepare_get_list_parameters(cls) -> List[tuple]:
        """Prepare parameters for listing users"""
        field_list = JSONSchemaLibrary(cls.LIST_API_PATH).get_request_fields_schema()
        params = [('fields[]', f) for f in field_list]
        params.append(('status', 'active'))
        return params
    
    @classmethod
    def generate_detail_path_info(cls, username: str) -> ApiPathInfo:
        """Generate the detail endpoint path with username"""
        return ApiPathInfo(cls.DETAIL_API_PATH, {'user_name': username})
    
    @classmethod
    def get_random_resource_id(cls) -> str:
        """Get a random username from the list"""
        response = cls.read_list()
        users = response.json()['data']
        if not users:
            return ""
        random_user = random.choice(users)
        return random_user['user_name']
    
    @property
    def resource_id(self) -> str:
        """Get the user's unique identifier"""
        return self._username
        
    @classmethod
    def _prepare_get_detail_parameters(cls) -> dict | list:
        return []