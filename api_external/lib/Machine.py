from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
import time
import random
from typing import Dict, Any, List, Optional

from api_path import ApiPath, ApiPathInfo, Method, ResponseCode
from api_external.lib.APIEndpointBase import APIEndpointBase
from api_external.lib.CommonUtils import APIUtils
from api_external.lib.JSONSchemaLibrary import JSONSchemaLibrary
import constant


class Machine(APIEndpointBase):
    """Handles machine-related API operations"""
    
    LIST_API_PATH = ApiPath.MACHINE_LIST
    DETAIL_API_PATH = ApiPath.MACHINE_DETAIL
    
    def __init__(self):
        super().__init__()
        self._serial_num: str = ''
        self._machine_id: str = ''
        self._public_key: str = ''
        self._private_key: bytes = b''
    
    def _sign_ecdsa(self, msg: str = '') -> str:
        """Sign the message with the ECDSA private key"""
        sk = serialization.load_pem_private_key(
            data=self._private_key,
            password=None,
            backend=default_backend()
        )
        signature = sk.sign(
            msg.encode('utf-8'),
            ec.ECDSA(hashes.SHA256())
        ).hex()
        return signature
    
    def _generate_ecc_keypair(self) -> tuple[str, bytes]:
        """Generate the ECC private key / public key pair"""
        pk = ec.generate_private_key(
            curve=ec.SECP256K1(),
            backend=default_backend()
        )
        private_key = pk.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_key = pk.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_key.decode("utf-8"), private_key
    
    def _prepare_import_payload(self) -> bool:
        """Prepare payload for creating a new machine"""
        self._machine_id = str(int(time.time()))
        self._serial_num = f'db0xqatesting{self._machine_id}'
        
        machine_import_data = {
            'csv': [{
                'serial_num': self._serial_num,
                'machine_id': self._machine_id,
                'hardware_version': '4.5A'
            }]
        }
        # self.info_data.update(self.create_payload['csv'][0])
        return machine_import_data
    
    def _prepare_register_payload(self):
        # register key to machine
        self.public_key, self.private_key = self._generate_ecc_keypair()
        machine_register_data = {
            'serial_num': self._serial_num,
            'public_key': self._public_key
        }
        return machine_register_data
    
    def _prepare_create_payload(self):
        self.create_payload = {
            'machine_import_data': self._prepare_import_payload(),
            'machine_register_data': self._prepare_register_payload()
        }
        return True
    
    def _execute_create_request(self) -> Dict[str, Any]:
        """Execute the create machine API request"""
        # Import machine
        machine_import_data = self.create_payload['machine_import_data']
        resp = APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(ApiPath.MACHINE_IMPORT),
            Method.POST,
            ResponseCode.OK,
            None,
            data=machine_import_data
        )
        
        machine_register_data = self.create_payload['machine_register_data']
        resp = APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(ApiPath.MACHINE_REGISTER),
            Method.POST,
            ResponseCode.OK,
            None,
            data=machine_register_data
        )
        
        # Set machine name
        self.create_payload = {
            'name': f'qatesting-{self._machine_id}',
            'serial_num': self._serial_num,
            'machine_id': self._machine_id,
            "drinkable_hot_water": True,
            "sparkling_water": True,
            "alert_mute": True,
            "auto_ratio": True,
            "is_reverse_pump_enabled": True,
            "is_adaptive_dispense_enabled": True
        }
        resp = APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(ApiPath.MACHINE_EDIT),
            Method.PATCH,
            ResponseCode.OK,
            None,
            data=self.create_payload
        )
        return resp
    
    # needs to add fields
    def _prepare_update_payload(self) -> bool:
        """Prepare payload for updating a machine"""
        self.update_payload = {
            'name': f'qatesting-{self._machine_id}',
            'serial_num': self._serial_num,
            'machine_id': self._machine_id
        }
        return True
    
    def _execute_update_request(self) -> Dict[str, Any]:
        """Execute the update machine API request"""
        return APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(ApiPath.MACHINE_EDIT),
            Method.PATCH,
            ResponseCode.OK,
            None,
            data=self.update_payload
        )
    
    def _set_resource_id(self, response: Dict[str, Any]) -> None:
        """Store the machine serial number from response"""
        # self._serial_num = self.create_payload['csv'][0]['serial_num']
        pass
    
    def delete(self) -> bool:
        """Delete a machine through the API"""
        # Check current owner
        response = APIUtils.call_api_and_assert_status_code(
            self.generate_detail_path_info(self._serial_num),
            Method.GET,
            ResponseCode.OK
        )
        user_name = response.json()['data']['user_name']
        
        # Return machine if needed
        if user_name != constant.BOTRISTA_USERNAME:
            APIUtils.call_api_and_assert_status_code(
                ApiPathInfo(ApiPath.MACHINE_TRANSFER),
                Method.POST,
                ResponseCode.OK,
                None,
                data={
                    'action': 'Return',
                    'serial_num': self._serial_num
                }
            )
        
        # Delete machine
        response = APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(ApiPath.MACHINE_DELETE, {'serial_num': self._serial_num}),
            Method.DELETE,
            ResponseCode.OK
        )
        return bool(response)
    
    @classmethod
    def _prepare_get_list_parameters(cls) -> List[tuple]:
        """Prepare parameters for listing machines"""
        field_list = JSONSchemaLibrary(cls.LIST_API_PATH).get_request_fields_schema()
        return [
            ('fields[]', f) for f in field_list
        ] + [('status', 'active')]
    
    @classmethod
    def generate_detail_path_info(cls, serial_num: str) -> ApiPathInfo:
        """Generate the detail endpoint path with serial number"""
        return ApiPathInfo(cls.DETAIL_API_PATH, {'serial_num': serial_num})
    
    @classmethod
    def get_random_resource_id(cls) -> str:
        """Get a random machine serial number from the list"""
        response = cls.read_list()
        machines = response.json()['data']
        if not machines:
            return ""
        random_machine = random.choice(machines)
        return random_machine['serial_num']
    
    @property
    def resource_id(self) -> str:
        """Get the machine's unique identifier"""
        return self._serial_num
    
    def get_machine_token(self):
        timestamp = int(time.time() * 1000)
        msg = f'{self._serial_num}-{timestamp}'
        signature = self._sign_ecdsa(self._private_key, msg=msg)
        payload = {
            "serial_num": self._serial_num,
            "verify": f"{self._serial_num}-{timestamp}",
            "signature": signature
        }
        resp = APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(ApiPath.MACHINE_LOGIN),
            Method.POST,
            ResponseCode.OK,
            None,
            data=payload
        ).json()
        return {'access_token': resp['data']['accessToken'], 'refresh_token': resp['data']['refreshToken']}
    
    def install_to_location(self, location):
        resp = APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(ApiPath.MACHINE_TRANSFER),
            Method.POST,
            ResponseCode.OK,
            None,
            data={
                'action': 'Install',
                'location_code': location,
                'serial_num': self._serial_num
            }
        )
        return resp