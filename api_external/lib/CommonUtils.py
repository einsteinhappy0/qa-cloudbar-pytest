import random
import string
from api_external.lib import *
from api_path import *


class StringUtils:
    def __init__(self):
        pass
    
    @staticmethod
    def random_string(length, str_type='ALL'):
        CHARS_TYPE = {
            'LOWER': string.ascii_lowercase,
            'UPPER': string.ascii_uppercase,
            'LETTER': string.ascii_letters,
            'NUMBER': string.digits,
            'ALL': string.printable
        }
        chars = CHARS_TYPE[str_type.upper()]
        return ''.join(random.choice(chars) for _ in range(length))


class APIUtils:
    def __init__(self):
        pass
    
    @staticmethod
    def call_api_and_assert_status_code(path_info, method, code, header=None, **kwargs):
        connection = SwaggerHiker()
        connection.swagger_get_auth(path_info.token_type, 'access')
        resp = connection.swagger_search(path_info.full_path, method.value, header, **kwargs)
        assert resp.status_code == code.value, \
            f"Expected status code {code.value}, got {resp.status_code} instead.\n" \
            f"Response: {resp.json()}"
        
        return resp


class ValidateUtils:
    def __init__(self):
        pass
    
    @staticmethod
    def validate_list(expect_list, actual_list):
        if type(expect_list) is not type(actual_list) \
                or type(expect_list) is not list \
                or len(expect_list) > len(actual_list):
            print(f"\nExpected list: {expect_list}\n\nActual list: {actual_list}\n")
            return False
        for idx, item in enumerate(expect_list):
            if type(item) is list:
                if not ValidateUtils.validate_list(item, actual_list[idx]):
                    return False
            elif type(item) is dict:
                if not ValidateUtils.validate_dict(item, actual_list[idx]):
                    return False
            else:
                if item != actual_list[idx]:
                    print(f"\nExpected list: {expect_list}\n\nActual list: {actual_list}\n")
                    return False
        return True
    
    @staticmethod
    def validate_dict(expect_dict, actual_dict):
        if type(expect_dict) is not type(actual_dict) \
                or type(expect_dict) is not dict \
                or not set(expect_dict) <= set(actual_dict):
            print(f"\nExpected dict: {expect_dict}\n\nActual dict: {actual_dict}\n")
            if not set(expect_dict) <= set(actual_dict):
                diff = set(expect_dict) - set(actual_dict)
                print(f'Expected keys are not in actual dict: {diff}')
            return False
        for key, expect_value in expect_dict.items():
            actual_value = actual_dict[key]
            if type(expect_value) is dict:
                if not ValidateUtils.validate_dict(expect_value, actual_value):
                    return False
            elif type(expect_value) is list:
                if not ValidateUtils.validate_list(expect_value, actual_value):
                    return False
            else:
                if expect_value != actual_value:
                    print(f'\nValue mismatch for key "{key}":\n'
                          f'  Expected: {expect_value}\n'
                          f'  Actual: {actual_value}')
                    return False
        return True