from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Optional
from string import Formatter


class TokenType(Enum):
    """Defines the type of token required for API endpoints."""
    USER_TOKEN = auto()
    MACHINE_TOKEN = auto()


@dataclass(frozen=True)
class PathData:
    """Represents the path information and associated token type for an API endpoint.
    
    Attributes:
        path: The URL path template (may include format parameters)
        token_type: The type of authentication token required
        required_params: Set of parameter names required in the path
    """
    path: str
    token_type: TokenType
    
    @property
    def required_params(self) -> set[str]:
        """Extract required parameters from the path template."""
        return {fname for _, fname, _, _ in Formatter().parse(self.path) if fname}


class ApiPath(Enum):
    """Enumeration of API paths with corresponding path data and token types.
    
    Paths are prefixed with their functional group for organization:
    - OTA_*: Over-the-air related endpoints
    - LOCATION_*: Location related endpoints
    - MACHINE_*: Machine related endpoints
    """
    # Machine channels endpoints
    MACHINE_CHANNEL = PathData(path='/machine-channels', token_type=TokenType.USER_TOKEN)
    
    # Location endpoints
    LOCATION_LIST = PathData(path='/locations', token_type=TokenType.USER_TOKEN)
    LOCATION_DETAIL = PathData(path='/locations/{full_code}', token_type=TokenType.USER_TOKEN)
    LOCATION_DRINK_SETTINGS = PathData(path='/locations/{full_code}/drink-settings', token_type=TokenType.USER_TOKEN)
    
    # User endpoints
    USER_LIST = PathData(path='/users', token_type=TokenType.USER_TOKEN)
    USER_UPDATE = PathData(path='/users/{user_name}', token_type=TokenType.USER_TOKEN)
    USER_DETAIL = PathData(path='/user/{user_name}', token_type=TokenType.USER_TOKEN)
    USER_LIST_BY_TYPE = PathData(path='/user/type/{type}', token_type=TokenType.USER_TOKEN)

    # Corporation endpoints
    CORP_LIST = PathData(path='/corporations', token_type=TokenType.USER_TOKEN)
    CORP_DETAIL = PathData(path='/corporations/{user_name}', token_type=TokenType.USER_TOKEN)
    
    # Machine endpoints
    MACHINE_LIST = PathData(path='/machines', token_type=TokenType.USER_TOKEN)
    MACHINE_DETAIL = PathData(path='/machines/{serial_num}', token_type=TokenType.USER_TOKEN)
    MACHINE_IMPORT = PathData(path='/user/machine/import/factory', token_type=TokenType.USER_TOKEN)
    MACHINE_REGISTER = PathData(path='/machine/register', token_type=TokenType.USER_TOKEN)
    MACHINE_EDIT = PathData(path='/user/machine/edit', token_type=TokenType.USER_TOKEN)
    MACHINE_LOGIN = PathData(path='/machine/login', token_type=TokenType.USER_TOKEN)
    MACHINE_TRANSFER = PathData(path='/user/machine/transfer', token_type=TokenType.USER_TOKEN)
    MACHINE_DELETE = PathData(path='/internal/machines/{serial_num}', token_type=TokenType.USER_TOKEN)
    
    # Flavor endpoints
    FLAVOR_CLASS_TYPE = PathData(path='/ref/flavor_class_type', token_type=TokenType.USER_TOKEN)
    FLAVOR_VENDORS = PathData(path='/flavor-vendors', token_type=TokenType.USER_TOKEN)
    FLAVOR_LIST = PathData(path='/flavors', token_type=TokenType.USER_TOKEN)
    FLAVOR_DETAIL = PathData(path='/flavors/{sku}', token_type=TokenType.USER_TOKEN)
    
    # Drink endpoints
    DRINK_CATEGORY = PathData(path='/drink-categories', token_type=TokenType.USER_TOKEN)
    DRINK_LIST = PathData(path='/drinks', token_type=TokenType.USER_TOKEN)
    DRINK_DETAIL = PathData(path='/drinks/{sku}', token_type=TokenType.USER_TOKEN)
    DRINK_DELETE = PathData(path='/internal/drinks/{sku}', token_type=TokenType.USER_TOKEN)
    
    # Menu endpoints
    MENU_LIST = PathData(path='/menus', token_type=TokenType.USER_TOKEN)
    MENU_DETAIL = PathData(path='/menus/{id}', token_type=TokenType.USER_TOKEN)
    MENU_PUMP = PathData(path='/menu/pump', token_type=TokenType.USER_TOKEN)
    MENU_BATCH = PathData(path='/menu/batch', token_type=TokenType.USER_TOKEN)


@dataclass(frozen=True)
class ApiPathInfo:
    """Handles API path information, including any dynamic path parameters.
    
    Args:
        api_path: The API path enum value
        path_parameter: Dictionary of path parameters to substitute
        
    Raises:
        ValueError: If required path parameters are missing
    """
    api_path: ApiPath
    path_parameter: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        path_data = self.api_path.value
        required_params = path_data.required_params
        
        # Validate all required parameters are provided
        missing_params = required_params - set(self.path_parameter.keys())
        if missing_params:
            raise ValueError(f"Missing required path parameters: {missing_params}")
            
        # We use object.__setattr__ to assign attributes within a frozen dataclass
        object.__setattr__(self, 'path', path_data.path)
        object.__setattr__(self, 'token_type', path_data.token_type)
        object.__setattr__(self, 'full_path', self.path.format(**self.path_parameter))
        
        
class ResponseCode(Enum):
    """Enumeration of HTTP response codes."""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500


class Method(Enum):
    """Enumeration of HTTP methods."""
    GET = 'GET'
    PUT = 'PUT'
    POST = 'POST'
    PATCH = 'PATCH'
    DELETE = 'DELETE'
    
    
class Country(Enum):
    US = 'United States'
    AU = 'Australia'
    TW = 'Taiwan'
    JP = 'Japan'
    TH = 'Thailand'
    CA = 'Canada'
    SG = 'Singapore'
    KR = 'South Korea'
    ES = 'Spain'