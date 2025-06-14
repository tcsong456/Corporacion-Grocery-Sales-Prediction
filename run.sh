bash shell_scripts/gen_auth_key.sh
docker build -f dockerfiles/terraform_setup_dockerfile -t data_download_and_upload:v1 .
docker run data_download_and_upload:v1
