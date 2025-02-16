# How to run test case
Using wrapped bash file to trigger testing type
```
bash qa-cloudbar/wrap.sh [test env] [testing type] [testing file name]
```
 - Test environment: Select the environment in which you want to run the tests.
 - Testing type options:
    - Regression: Includes web and API testing.
    - Smoke Test: Covers important services and pages.
    - File: Allows you to choose the specific test file for execution.
    - Testing file name: This variable is optional when you select the testing type as 'File.' You can choose the test file you wish to execute.
```
<!-- Testing type: file -->
bash qa-cloudbar/wrap.sh qa file User_Login_Cloud

<!-- Testing type: regression -->
bash qa-cloudbar/wrap.sh qa regression

<!-- Testing type: smoke testing -->
bash qa-cloudbar/wrap.sh qa smoke_test
```