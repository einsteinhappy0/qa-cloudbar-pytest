import pytest
from api_path import *
from api_external.lib import *
import constant


@pytest.mark.case_id('C200')
def test_get_current_drink_setting(corporation, location, menu, machine):
    location.set_user_name(corporation.resource_id)
    machine.install_to_location(location.resource_id)
    menu.assign_to_machines([machine.resource_id])
    resp = location.get_drink_settings(menu.resource_id)
    json_schema_lib = JSONSchemaLibrary(
        ApiPath.LOCATION_DRINK_SETTINGS,
        Method.GET,
        ResponseCode.OK
    )
    assert json_schema_lib.verify_resp_schema(resp.json(), 'ALL')