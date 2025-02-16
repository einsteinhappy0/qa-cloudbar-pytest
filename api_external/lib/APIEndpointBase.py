from api_path import *
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
from api_external.lib.CommonUtils import APIUtils
from api_external.lib.JSONSchemaLibrary import JSONSchemaLibrary


class APIEndpointBase(ABC):
    """
    Abstract base class for API endpoints that implements CRUD operations.
    Provides a template for API interactions with standardized methods.
    """
    # Class-level endpoint configurations
    LIST_API_PATH: Optional[ApiPath] = None
    DETAIL_API_PATH: Optional[ApiPath] = None
    
    def __init__(self):
        """Initialize API endpoint with empty data containers"""
        self.create_payload: Dict[str, Any] = {}
        self.update_payload: Dict[str, Any] = {}
        self.info_data: Dict[str, Any] = {}
    
    @abstractmethod
    def _prepare_create_payload(self) -> bool:
        """
        Prepare payload for creating a new resource.
        Returns: bool indicating success/failure
        """
        pass
    
    @abstractmethod
    def _set_resource_id(self):
        pass
    
    def create(self) -> Any:
        """
        Create a new resource through the API.
        Returns: bool indicating success/failure
        """
        if not self._prepare_create_payload():
            return None
        resp = self._execute_create_request()
        if not resp:
            return None
        self._set_resource_id(resp)
        self.info_data.update(self.create_payload)
        return resp
    
    def _execute_create_request(self) -> Any:
        """
        Execute the actual create API request.
        Returns: API response data
        """
        resp = APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(self.__class__.LIST_API_PATH),
            Method.POST,
            ResponseCode.OK,
            None,
            data=self.create_payload
        )
        return resp
    
    @abstractmethod
    def _prepare_update_payload(self) -> bool:
        """
        Prepare payload for updating a resource.
        Returns: bool indicating success/failure
        """
        pass
    
    @abstractmethod
    def _execute_update_request(self) -> Any:
        """
        Execute the actual update API request.
        Returns: API response data
        """
        pass
    
    def update(self) -> Any:
        """
        Update an existing resource through the API.
        Returns: bool indicating success/failure
        """
        if not self._prepare_update_payload():
            return None
        resp = self._execute_update_request()
        if not resp:
            return None
        self.info_data.update(self.update_payload)
        return resp
    
    @abstractmethod
    def delete(self) -> Any:
        """Delete a resource through the API"""
        pass
    
    @classmethod
    def _prepare_get_detail_parameters(cls) -> dict | list:
        field_list = JSONSchemaLibrary(cls.DETAIL_API_PATH).get_request_fields_schema()
        params = [('fields[]', f) for f in field_list]
        return params
    
    @classmethod
    @abstractmethod
    def generate_detail_path_info(cls, resource_id):
        pass
    
    @classmethod
    def read_detail(cls, resource_id) -> Any:
        """
        Read/retrieve a resource from the API.
        Returns: API response data
        """
        params = cls._prepare_get_detail_parameters()
        api_path_info = cls.generate_detail_path_info(resource_id)
        resp = APIUtils.call_api_and_assert_status_code(
            api_path_info,
            Method.GET,
            ResponseCode.OK,
            None,
            params=params
        )
        return resp
    
    @classmethod
    def _get_item_amount(cls):
        resp = APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(cls.LIST_API_PATH),
            Method.GET,
            ResponseCode.OK,
            None,
            params={
                'amount': 1,
            }
        )
        return resp.json()['data']['total']
    
    @classmethod
    @abstractmethod
    def _prepare_get_list_parameters(cls) -> dict | list:
        pass
    
    @classmethod
    def read_list(cls) -> Any:
        """
        Read/retrieve a resource from the API.
        Returns: API response data
        """
        params = cls._prepare_get_list_parameters()
        resp = APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(cls.LIST_API_PATH),
            Method.GET,
            ResponseCode.OK,
            None,
            params=params
        )
        return resp
    
    @property
    @abstractmethod
    def resource_id(self):
        pass
    
    @classmethod
    @abstractmethod
    def get_random_resource_id(cls) -> str:
        pass