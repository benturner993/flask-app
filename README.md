# Objective
The aim for this repository is to create a working prototype flask-app which is to be used in conjunction with the proactive, reactive and win-back modelling strategies.

## Run Configuration

To run the app, please first install and run the `environment.yml` file.

If the app is already running and you need to restart, be sure to first kill the app by running:

- `lsof -i :5000` to find the PID
- `kill -9 PID` where PID is from the command above

## Deployment Configuration

- Login to Azure using `az login` or `az login --identity`
- Build your docker image called `reward` using `docker build -t reward .`
- If ACR doesn't already exist (it does), then create using `az acr create --resource-group name_of_resource_group --name name_of_azure_container_registry --sku Basic`
- Login to ACR `az acr login --name_of_azure_container_registry`
- Tag the docker container `docker tag name_of_azure_container_registry.azurecr.io/reward`
- Go to App Services and create a web app service. Set the resource group, publish docker container, region in UK South and create new plan
- Configure web app `az webapp config container set --name name_of_app --docker-custom-image-name  name_of_azure_container_registry.azurecr.io/reward --docker-registry-server-password PASSWORD --docker-registry-server-user name_of_azure_container_registry`
- Create the web app `az webapp create --resource-group name_of_resource_group --plan web_app_name --name name_of_app --multicontainer-config-type compose --multicontainer-config-file docker-compose.yml`

## Additional notes

Please remember to hide any keys before publishing any apps.

## Author

Ben Turner, 2024 Q1