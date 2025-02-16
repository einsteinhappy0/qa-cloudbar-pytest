import pytest
from api_path import *
from api_external.lib import *


@pytest.mark.case_id('C100')
@pytest.mark.parametrize("test_cls", [Location, Flavor, Drink,
                                      User, Machine, Corporation, Menu])
def test_get_list(test_cls):
    all_details_resp = test_cls.read_list()
    list_path = test_cls.LIST_API_PATH
    if test_cls is Corporation:
        list_path = test_cls.OLD_LIST_API_PATH
    json_schema_lib = JSONSchemaLibrary(
        list_path,
        Method.GET,
        ResponseCode.OK
    )
    assert json_schema_lib.verify_resp_schema(all_details_resp.json())


@pytest.mark.case_id('C101')
@pytest.mark.parametrize("test_cls", [Location, Flavor, Drink,
                                      User, Machine, Corporation, Menu])
def test_get_info(test_cls):
    random_id = test_cls.get_random_resource_id()
    detail_resp = test_cls.read_detail(random_id)
    detail_path = test_cls.DETAIL_API_PATH
    if test_cls is Corporation:
        detail_path = User.DETAIL_API_PATH
    json_schema_lib = JSONSchemaLibrary(
        detail_path,
        Method.GET,
        ResponseCode.OK
    )
    assert json_schema_lib.verify_resp_schema(detail_resp.json())


@pytest.mark.case_id('C102')
@pytest.mark.parametrize("test_cls", [Location, Flavor, Drink,
                                      User, Machine, Corporation, Menu])
def test_create(test_cls):
    test_obj = test_cls()
    
    create_resp = test_obj.create()
    # verify response schema
    if test_cls is Machine:
        json_schema_lib = JSONSchemaLibrary(
            ApiPath.MACHINE_EDIT,
            Method.PATCH,
            ResponseCode.OK
        )
    else:
        json_schema_lib = JSONSchemaLibrary(
            test_cls.LIST_API_PATH,
            Method.POST,
            ResponseCode.OK
        )
    assert json_schema_lib.verify_resp_schema(create_resp.json())
    
    detail_path = test_cls.DETAIL_API_PATH
    if test_cls is Corporation:
        detail_path = User.DETAIL_API_PATH
    detail_resp = test_cls.read_detail(test_obj.resource_id)
    json_schema_lib = JSONSchemaLibrary(
        detail_path,
        Method.GET,
        ResponseCode.OK
    )
    assert json_schema_lib.verify_resp_schema(detail_resp.json())
    assert ValidateUtils.validate_dict(test_obj.info_data, detail_resp.json()["data"]), 'Verify create info data failed.'
    
    test_obj.delete()


@pytest.mark.case_id('C103')
@pytest.mark.parametrize("test_cls", [Location, Flavor, Drink,
                                      User, Machine, Corporation, Menu])
def test_update(test_cls):
    test_obj = test_cls()
    test_obj.create()
    test_obj.update()
    
    detail_path = test_cls.DETAIL_API_PATH
    if test_cls is Corporation:
        detail_path = User.DETAIL_API_PATH
    detail_resp = test_cls.read_detail(test_obj.resource_id)
    json_schema_lib = JSONSchemaLibrary(
        detail_path,
        Method.GET,
        ResponseCode.OK
    )
    assert json_schema_lib.verify_resp_schema(detail_resp.json())
    assert ValidateUtils.validate_dict(test_obj.info_data, detail_resp.json()["data"]), 'Verify update info data failed.'
    
    test_obj.delete()


@pytest.mark.case_id('C104')
@pytest.mark.parametrize("test_cls", [Location, Flavor, Drink,
                                      User, Machine, Corporation, Menu])
def test_delete(test_cls):
    test_obj = test_cls()
    test_obj.create()
    test_obj.delete()
    
    if test_cls is Corporation or test_cls is User:
        resp = test_cls.read_detail(test_obj.resource_id)
        assert 'inactive' == resp.json()['data']['status']
    else:
        path_info_detail = test_cls.generate_detail_path_info(test_obj.resource_id)
        # verify the item has been delete
        APIUtils.call_api_and_assert_status_code(
            path_info_detail,
            Method.DELETE,
            ResponseCode.NOT_FOUND
        )