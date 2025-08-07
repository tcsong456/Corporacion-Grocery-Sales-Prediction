locals {
  creds = (
    length(trimspace(try(coalesce(var.credential_key_json,""),""))) > 0 ? var.credential_key_json :
    length(trimspace(try(coalesce(var.gcp_credential_file,""),""))) > 0 ? try(file(var.gcp_credential_file), null) : null
  )
}

provider "google-beta" {
  project     = var.project_id
  region      = var.region
  credentials = local.creds
}

provider "google" {
  project = var.project_id
  region  = var.region
  #  credentials = file("${path.module}/../key.json")
  credentials = local.creds
}