bash shell_scripts/gen_auth_key.sh
docker build -f dockerfiles/terraform_setup_dockerfile -t data_download_and_creation .
docker run data_download_and_creation
docker build -f dockerfiles/dataform_dockerfile -t dataform_models .
docker run dataform_models