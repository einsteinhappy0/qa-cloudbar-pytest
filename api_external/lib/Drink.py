import copy
import random
from typing import Dict, Any, List
from api_external.lib.APIEndpointBase import APIEndpointBase
from api_external.lib.CommonUtils import StringUtils, APIUtils
from api_external.lib.Flavor import Flavor
from api_path import *


class BlenderSetting(Enum):
    """Blender settings for different drink types"""
    HIGH_STANDARD = (1, 10)
    LOW_FOAM = (1, 80)
    SMOOTHIE_STANDARD = (3, 30)
    MILKSHAKE_FINEST = (3, 60)
    PULSE = (1, 1)
    MEDIUM = (3, 60)


class Drink(APIEndpointBase):
    """Handles drink-related API operations"""
    
    LIST_API_PATH = ApiPath.DRINK_LIST
    DETAIL_API_PATH = ApiPath.DRINK_DETAIL
    
    def __init__(self):
        super().__init__()
        self._drink_sku: str = ''
    
    def _get_drink_category(self) -> List[str]:
        """Get available drink category IDs"""
        response = APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(ApiPath.DRINK_CATEGORY),
            Method.GET,
            ResponseCode.OK
        )
        return response
    
    def _get_drink_category_ids(self) -> List[str]:
        """Get available drink category IDs"""
        response = self._get_drink_category()
        return [category['_id'] for category in response.json()['data']]
    
    def _gen_drink_formula(self):
        # Get random flavors and calculate volumes
        flavors = random.choices(Flavor.read_list().json()['data']['flavors'], k=3)
        default_volume = 0
        ratios = []
        for flavor in flavors:
            volume = random.randint(1, 500)
            default_volume += volume
            ratios.append({
                "flavor_sku": flavor['full_sku'],
                'volume_ml': volume
            })
        
        # Create formulas for different sugar levels
        formulas = []
        for sugar_level in (100, 50):
            ratios_by_sugar = copy.deepcopy(ratios)
            for idx, ratio in enumerate(ratios_by_sugar):
                # should change to check if it is sugar flavor
                if idx == 0:
                    ratio['volume_ml'] = int(ratio['volume_ml'] * (sugar_level / 100))
            formulas.append({
                "sugar_level": sugar_level,
                "ratios": ratios_by_sugar
            })
        return default_volume, formulas
    
    def _prepare_create_payload(self) -> bool:
        """Prepare payload for creating a new drink"""
        blend_mode = random.choice(list(BlenderSetting))
        item_type = random.choice(['8', '9'])
        name = f'Test_{StringUtils.random_string(10, "LOWER")}'
        version = StringUtils.random_string(2, 'NUMBER')
        country = random.choice(list(Country))
        sku = f'9{item_type}-{name}-{country.name}{version}'
        process_order = ["dispense_ingredient", "blending"]
        random.shuffle(process_order)
        default_volume, formulas = self._gen_drink_formula()
        
        self.create_payload = {
            "allow_sparkling": random.choice([True, False]),
            "sku": sku,
            "blender_setting": {
                "mode": blend_mode.name,
                "duration": random.choice(blend_mode.value)
            },
            "country": country.value,
            "description": StringUtils.random_string(10, 'ALL'),
            "drink_tag": [
                StringUtils.random_string(5, 'ALL'),
                StringUtils.random_string(5, 'ALL')
            ],
            "item_type": item_type,
            "name": name,
            "process_order_steps": process_order,
            "status": "active",
            "version": version,
            "fixed_level": False,
            "drink_category_id": random.choice(self._get_drink_category_ids()),
            # "default_volume": default_volume,
            "formulas": formulas
        }
        return True
    
    def _prepare_update_payload(self) -> bool:
        """Prepare payload for updating a drink"""
        blend_mode = random.choice(list(BlenderSetting))
        drink_category_id = random.choice(self._get_drink_category_ids())
        process_order = ["dispense_ingredient", "blending"]
        random.shuffle(process_order)
        default_volume, formulas = self._gen_drink_formula()
        
        self.update_payload = {
            "blender_setting": {
                "mode": blend_mode.name,
                "duration": random.choice(blend_mode.value)
            },
            "description": StringUtils.random_string(10, 'ALL'),
            "drink_category_id": drink_category_id,
            "drink_tag": [
                StringUtils.random_string(5, 'ALL'),
                StringUtils.random_string(5, 'ALL')
            ],
            "process_order_steps": process_order,
            "formulas": formulas
        }
        self.info_data.update(self.update_payload)
        return True
    
    def _set_resource_id(self, response: Dict[str, Any]) -> None:
        """Store the drink SKU from response"""
        self._drink_sku = response.json()['data']['sku']
    
    def _execute_create_request(self) -> Dict[str, Any]:
        """Execute the create drink API request"""
        return APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(self.__class__.LIST_API_PATH),
            Method.POST,
            ResponseCode.OK,
            data=self.create_payload
        )
    
    def _execute_update_request(self) -> Dict[str, Any]:
        """Execute the update drink API request"""
        return APIUtils.call_api_and_assert_status_code(
            self.generate_detail_path_info(self._drink_sku),
            Method.PUT,
            ResponseCode.OK,
            data=self.update_payload
        )
    
    def delete(self) -> bool:
        """Delete a drink through the API"""
        path_info = ApiPathInfo(ApiPath.DRINK_DELETE, {'sku': self._drink_sku})
        response = APIUtils.call_api_and_assert_status_code(
            path_info,
            Method.DELETE,
            ResponseCode.OK
        )
        return bool(response)
    
    @classmethod
    def _prepare_get_list_parameters(cls) -> List[tuple]:
        """Prepare parameters for listing drinks"""
        total = cls._get_item_amount()
        params = cls._prepare_get_detail_parameters()
        
        params.extend([
            ('amount', total),
            ('status', 'active')
        ])
        return params
    
    @classmethod
    def _get_item_amount(cls) -> int:
        """Get total number of drinks"""
        response = APIUtils.call_api_and_assert_status_code(
            ApiPathInfo(cls.LIST_API_PATH),
            Method.GET,
            ResponseCode.OK,
            None,
            params={'amount': 1}
        )
        return response.json()['data']['total']
    
    @classmethod
    def generate_detail_path_info(cls, sku: str) -> ApiPathInfo:
        """Generate the detail endpoint path with SKU"""
        return ApiPathInfo(cls.DETAIL_API_PATH, {'sku': sku})
    
    @classmethod
    def get_random_resource_id(cls) -> str:
        """Get a random drink SKU from the list"""
        response = cls.read_list()
        drinks = response.json()['data']['drinks']
        if not drinks:
            return None
        random_drink = random.choice(drinks)
        return random_drink['sku']
    
    @property
    def resource_id(self) -> str:
        """Get the drink's unique identifier"""
        return self._drink_sku
    
    def create(self) -> Any:
        resp = super().create()
        if resp:
            self.info_data['drink_category'] = {'_id': self.info_data.pop('drink_category_id')}
        return resp
    
    def update(self) -> Any:
        resp = super().update()
        if resp:
            self.info_data['drink_category'] = {'_id': self.info_data.pop('drink_category_id')}
        return resp