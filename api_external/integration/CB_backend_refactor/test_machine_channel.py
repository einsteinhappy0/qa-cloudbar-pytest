import pytest
# import json
from api_external.lib import *
from api_path import *


@pytest.mark.smoke
@pytest.mark.case_id('C6858')
def test_get_machine_channel_list():
    api_path = ApiPath.MACHINE_CHANNEL
    method = Method.GET
    response_code = ResponseCode.OK
    
    resp = APIUtils.call_api_and_assert_status_code(
        ApiPathInfo(api_path),
        method,
        response_code
    )
    
    # verify response schema
    json_schema_lib = LIB.JSONSchemaLibrary(api_path, method, response_code)
    assert json_schema_lib.verify_resp_schema(resp.json())