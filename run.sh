bash shell_scripts/gen_auth_key.sh
docker build -f dockerfiles/terraform_setup_dockerfile -t data_download_and_terraform_setup .
docker run data_download_and_terraform_setup
docker build -f dockerfiles/dataform_dockerfile -t dataform_models .
docker run dataform_models