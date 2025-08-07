bash shell_scripts/gen_auth_key.sh $1
docker build -f dockerfiles/terraform_setup_dockerfile -t data_download_and_terraform_setup .
docker run --rm --mount type=bind,src="$(pwd)/key.json",dst=/run/secrets/key.json,ro \
                 -e GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/key.json \
                 -e CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE=/run/secrets/key.json \
                 data_download_and_terraform_setup
docker build -f dockerfiles/dataform_dockerfile -t dataform_models .
docker run --rm dataform_models