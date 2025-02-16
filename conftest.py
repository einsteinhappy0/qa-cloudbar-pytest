import pytest
from api_external.lib import *
# import constant


def fixture_factory(test_obj):
    test_obj.create()
    yield test_obj
    test_obj.delete()
    
    
@pytest.fixture(scope="function")
def location():
    yield from fixture_factory(Location())
    
    
@pytest.fixture(scope="function")
def machine():
    yield from fixture_factory(Machine())


@pytest.fixture(scope="function")
def user():
    yield from fixture_factory(User())
    
    
@pytest.fixture(scope="function")
def corporation():
    yield from fixture_factory(Corporation())
    
    
@pytest.fixture(scope="function")
def flavor():
    yield from fixture_factory(Flavor())
    
    
@pytest.fixture(scope="function")
def menu():
    yield from fixture_factory(Menu())


def pytest_collection_modifyitems(config, items):
    selected_case_id = config.getoption("--case_id")
    if selected_case_id:
        selected_items = []
        for item in items:
            for mark in item.iter_markers(name="case_id"):
                if mark.args and mark.args[0] == selected_case_id:
                    selected_items.append(item)
        items[:] = selected_items


def pytest_addoption(parser):
    parser.addoption("--case_id", action="store", help="Run specific test case by case_id")


@pytest.fixture(autouse=True)
def my_record_property(request, record_property):
    for mark in request.node.own_markers:
        if mark.name == 'case_id':
            record_property('test_id', mark.args[0])
            break