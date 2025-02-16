# e.g bash qa-cloudbar/wrap.sh prod smoke_test --docker_skip
echo "Start The Test"

rm ./qa-cloudbar/.env

if [ "$1" = "beta" ]
then
    echo "Run in Beta Environment"
    echo "BACKEND_HOST=https://api.beta.botrista.io" >> ./qa-cloudbar/.env
    echo "SALES_DASHBOARD_HOST=https://api-sales-dashboard.beta.botrista.io" >> ./qa-cloudbar/.env
    echo "CLOUD_BAR_DOMAIN=https://cloudbar.beta.botrista.io" >> ./qa-cloudbar/.env
    echo "SWAGGER_ENV=qa" >> ./qa-cloudbar/.env
elif [ "$1" = "prod" ]
then
    echo "Run in Production Environment"
    echo "BACKEND_HOST=https://us-orderbws.botrista.io" >> ./qa-cloudbar/.env
    echo "SALES_DASHBOARD_HOST=https://us-sales-dashboard.botrista.io" >> ./qa-cloudbar/.env
    echo "CLOUD_BAR_DOMAIN=https://internal.botrista.io" >> ./qa-cloudbar/.env
    echo "SWAGGER_ENV=qa" >> ./qa-cloudbar/.env
elif [ "$1" = "dev" ]
then
    echo "Run in Developmemt Environment"
    echo "BACKEND_HOST=https://api.dev.botrista.io" >> ./qa-cloudbar/.env
    echo "SALES_DASHBOARD_HOST=https://api-sales-dashboard.dev.botrista.io" >> ./qa-cloudbar/.env
    echo "CLOUD_BAR_DOMAIN=https://cloudbar.dev.botrista.io" >> ./qa-cloudbar/.env
    echo "SWAGGER_ENV=dev" >> ./qa-cloudbar/.env
elif [ "$1" = "qa" ] 
then
    echo "Run in QA Environment"
    echo "BACKEND_HOST=https://api.qa.botrista.io" >> ./qa-cloudbar/.env
    echo "SALES_DASHBOARD_HOST=https://api-sales-dashboard.qa.botrista.io" >> ./qa-cloudbar/.env
    echo "CLOUD_BAR_DOMAIN=https://cloudbar.qa.botrista.io" >> ./qa-cloudbar/.env
    echo "SWAGGER_ENV=qa" >> ./qa-cloudbar/.env
elif [ "$1" = "new_beta" ]
then
    echo "Run in New Beta Environment"
    echo "BACKEND_HOST=https://api.beta.botrista.io" >> ./qa-cloudbar/.env
    echo "SALES_DASHBOARD_HOST=https://api-sales-dashboard.beta.botrista.io" >> ./qa-cloudbar/.env
    echo "CLOUD_BAR_DOMAIN=https://test.beta.botrista.io" >> ./qa-cloudbar/.env
    echo "SWAGGER_ENV=qa" >> ./qa-cloudbar/.env
elif [ "$1" = "local" ]
then
    echo "Run in Local Environment"
    echo "BACKEND_HOST=http://host.docker.internal:9527" >> ./qa-cloudbar/.env
    echo "LEGACY_BACKEND_HOST=http://host.docker.internal:7777" >> ./qa-cloudbar/.env
    echo "SALES_DASHBOARD_HOST=http://host.docker.internal:3000" >> ./qa-cloudbar/.env
    echo "CLOUD_BAR_DOMAIN=http://host.docker.internal:8888/" >> ./qa-cloudbar/.env
    echo "SWAGGER_ENV=dev" >> ./qa-cloudbar/.env
elif [ "$1" = "tokyo" ]
then
    echo "Run in Tokyo Environment"
    echo "BACKEND_HOST=https://ap-orderbws.botrista.io" >> ./qa-cloudbar/.env
    echo "LEGACY_BACKEND_HOST=https://ap-bws.botrista.io" >> ./qa-cloudbar/.env
    echo "SALES_DASHBOARD_HOST=https://ap-sales-dashboard.botrista.io" >> ./qa-cloudbar/.env
    echo "SWAGGER_ENV=qa" >> ./qa-cloudbar/.env
fi

if [ "$2" = "smoke_test" ]
then 
    echo "Smoke testing start"
    python3 qa-script/robot_runner run -I qa-cloudbar -O --include=smoke_test $3
elif [ "$2" = "regression" ]
then
    echo "Regression testing start"
    python3 qa-script/robot_runner run -I qa-cloudbar -i web,api_external $3
elif [ "$2" = "migration" ]
then
    echo "Regression testing start"
    python3 qa-script/robot_runner run -I qa-cloudbar -i migration $3
elif [ "$2" = "file" ]
then
    echo "Regression testing start"
    python3 qa-script/robot_runner run -I qa-cloudbar -O --suite=$3
else
    echo "Run test case with tag $2"
    python3 qa-script/robot_runner run -I qa-cloudbar -O --include=$2 -r 0
fi

exit 0