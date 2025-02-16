# from robot.api import logger
import json
import jsonref
from jsonschema import Draft202012Validator
import os
from importlib import resources
from pathlib import Path
import constant
from api_external.lib import *
from api_path import *


class JSONSchemaLibrary:
    def __init__(self, api_path, method=Method.GET, response=ResponseCode.OK):
        self.schema_filename = constant.SWAGGER_JSON_PATH
        self.path = api_path.value.path
        self.method = method.value.lower()
        self.response = str(response.value)
    
    def get_nested_value(self, dictionary, keys, default=None):
        """
        Safely get nested dictionary value using a list of keys.
        
        Args:
            dictionary: The dictionary to traverse
            keys: List of keys defining the path to the desired value
            default: Value to return if path doesn't exist (default: None)
        
        Returns:
            The value if found, otherwise the default value
        """
        temp = dictionary
        try:
            for key in keys:
                temp = temp[key]
            return temp
        except (KeyError, TypeError):
            return default
    
    def transform_nullable_types(self, schema):
        """
        Recursively transforms schema properties with 'nullable: true' to include 'null' in type array.
        
        Args:
            schema (dict): The JSON schema to transform
        
        Returns:
            dict: The transformed schema
        """
        if not isinstance(schema, dict):
            return schema
        
        # Create a new dict to avoid modifying the input during iteration
        transformed = schema.copy()
        
        # Handle nullable with type
        if 'nullable' in transformed:
            is_nullable = transformed.pop('nullable')
            if is_nullable:
                if 'type' in transformed:
                    # Convert single type to array if needed
                    current_type = transformed['type']
                    if isinstance(current_type, str):
                        transformed['type'] = [current_type, 'null']
                    elif isinstance(current_type, list) and 'null' not in current_type:
                        transformed['type'] = current_type + ['null']
                else:
                    # If no type is specified, assume string
                    transformed['type'] = ['string', 'null']
        
        # Recursively transform nested objects
        for key, value in transformed.items():
            if key == 'properties' and isinstance(value, dict):
                # Transform each property
                transformed[key] = {k: self.transform_nullable_types(v) for k, v in value.items()}
            elif key == 'items' and isinstance(value, dict):
                # Transform array items
                transformed[key] = self.transform_nullable_types(value)
            elif isinstance(value, dict):
                # Transform nested objects
                transformed[key] = self.transform_nullable_types(value)
            elif isinstance(value, list):
                # Transform items in arrays
                transformed[key] = [self.transform_nullable_types(item) if isinstance(item, dict) else item
                                    for item in value]
        
        return transformed
    
    def __load_response_schema(self, full_schema, path, method, response):
        keys = ['paths', path, method, 'responses', response,
                'content', 'application/json', 'schema']
        schema = self.get_nested_value(full_schema, keys)
        if schema:
            # Transform nullable properties before validation
            return self.transform_nullable_types(schema)
        return None
    
    def __load_json_schema(self):
        """ Loads the given schema file """
        schema = None
        if not Path(constant.SCHEMA_FILE_PATH).is_file():
            SwaggerHiker().swagger_get_schema()
        
        with resources.open_text("api_external.res.schema", self.schema_filename) as schema_fid:
            file_uri = Path(os.path.abspath(schema_fid.name)).as_uri()
            schemas_file = schema_fid.read()
            schema = jsonref.loads(schemas_file, base_uri=file_uri, jsonschema=True)
        return schema
    
    def __add_required_fields(self, schema):
        """Recursively adds required fields to all objects in the schema."""
        if not isinstance(schema, dict):
            return
        
        # If this is an object type schema
        if schema.get('type') == 'object' and 'properties' in schema:
            # Make all properties required
            schema['required'] = list(schema['properties'].keys())
            
            # Recursively process all properties
            for prop in schema['properties'].values():
                self.__add_required_fields(prop)
        
        # If this is an array type schema
        elif schema.get('type') == 'array' and 'items' in schema:
            # Process the items schema
            self.__add_required_fields(schema['items'])
    
    def verify_resp_schema(self, sample, require=None):
        """Load json schema and extract response schema"""
        schema = self.__load_json_schema()
        if not schema:
            print(f'Schema file not found: {self.schema_filename}')
            return False
        resp_schema = self.__load_response_schema(schema, self.path, self.method, self.response)
        if not resp_schema:
            print(f"Schema not found for path: {self.path}[{self.method}]({self.response})")
            return False
        # Add required fields recursively
        if require == 'ALL':
            self.__add_required_fields(resp_schema)
        
        """Validates the sample JSON against the given schema."""
        validator = Draft202012Validator(resp_schema)
        if isinstance(sample, str):
            sample = json.loads(sample)
        errors = sorted(validator.iter_errors(sample), key=lambda e: e.path)
        for error in errors:
            print(
                f'Validation error for schema {self.path}[{self.method}]({self.response}) - {error.schema_path}: {error.message}')
            print(f'absolute_path: {error.absolute_path}')
        
        return False if errors else True
    
    def get_request_fields_schema(self):
        """Load json schema and extract response schema"""
        full_schema = self.__load_json_schema()
        if not full_schema:
            print(f'Schema file not found: {self.schema_filename}')
            return []
        
        keys = ['paths', self.path, self.method, 'parameters']
        param_schema = self.get_nested_value(full_schema, keys, [])
        for param in param_schema:
            if param['name'] == 'fields':
                keys = ['schema', 'items', 'enum']
                return self.get_nested_value(param, keys, [])
        return []