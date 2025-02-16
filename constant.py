import os
from dotenv import load_dotenv


load_dotenv()

# test timeout
TIMEOUT = os.getenv("TIMEOUT", 300)

# host settings
BACKEND_HOST = os.getenv("BACKEND_HOST", "https://api.qa.botrista.io")
BASE_HOST = os.getenv("BASE_HOST", "https://us-stage-orderbws.botrista.io")
CLOUD_BAR_DOMAIN = os.getenv("CLOUD_BAR_DOMAIN", "https://cloudbar.qa.botrista.io")
OTA_DOMAIN = os.getenv("OTA_DOMAIN", "https://us-orderbws.botrista.io")

# Please put legacy host in the end potision. If legancy migrate to backend, it doesn't matter to end potision
SWAGGER_ENV = os.getenv("SWAGGER_ENV", "qa")
SWAGGER_HOST_LIST = os.getenv("SWAGGER_HOST_LIST",
                              [f"https://api-sales-dashboard.{SWAGGER_ENV}.botrista.io",  f"https://api.{SWAGGER_ENV}.botrista.io"])

# testing user
TEST_HQ_USER_LOCATION_PREFIX = os.getenv("TEST_HQ_USER_LOCATION_PREFIX", "QLY")
TEST_HQ_USER_NAME = os.getenv("TEST_HQ_USER_NAME", "avrch1688539889")
TEST_USER_ACCOUNT = os.getenv("TEST_USER_ACCOUNT", "Botrista_QA")
TEST_USER_NAME = os.getenv("TEST_USER_NAME", "qa_testing")
TEST_USER_NAME_ACCOUNT = os.getenv("TEST_USER_NAME", "QA_Testing")
TEST_USER_NAME_BOTRISTA = os.getenv("TEST_USER_NAME", "botrista")
TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL", "qatesting_cb@mailsac.com")

# test serial_num
DRINKBOT_PRO_4_3_SERIAL_NUM = os.getenv(
    "DRINKBOT_PRO_4_3_SERIAL_NUM", "db0x9947598qatesting")
DRINKBOT_PRO_4_3_MACHINE_ID = os.getenv(
    "DRINKBOT_PRO_4_3_MACHINE_ID", "db0x9947598qatesting")

# Flavor_category_id
FLAVOR_CATEGORY_ID = os.getenv(
    "FLAVOR_CATEGORY_ID", "60657942b9183ced77d7e7d2")
FLAVOR_MIGRATION_ID = os.getenv(
    "FLAVOR_MIGRATION_ID", "5fa242193fb7cd8a5017d637")
AWS_S3_URL = os.getenv(
    "AWS_S3_URL", "http://s3.us-west-2.amazonaws.com/botrista-dev-drone-ci")

# mailsac email service
MAILSAC_AUTH_KEY = os.getenv("MAILSAC_AUTH_KEY", "k_s8jdMYFYWp1Gi0QcLGWMAZLJkvHKa35hQOjk")
MAILSAC_WEBSOCKET_ENDPOINT = os.getenv("MAILSAC_WEBSOCKET_ENDPOINT", "wss://sock.mailsac.com/incoming-messages")

# rold id of admin
ADMIN_ROLE_ID = os.getenv("ADMIN_ROLE_ID", "6644876c429191f785b5eeb9")

BOTRISTA_USERNAME = "botrista_machines"

SWAGGER_JSON_PATH = 'swagger.json'
CWD = os.path.dirname(os.path.abspath(__file__))
SCHEMA_FILE_PATH = f'{CWD}/api_external/res/schema/{SWAGGER_JSON_PATH}'