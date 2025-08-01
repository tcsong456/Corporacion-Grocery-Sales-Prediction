locals {
  creds = coalesce(
    var.credential_key_json,
    var.gcp_credential_file != null ? file(var.gcp_credential_file) : null
  )
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
  #  credentials = file("${path.module}/../key.json")
  credentials = local.creds
}

provider "google" {
  project = var.project_id
  region  = var.region
  #  credentials = file("${path.module}/../key.json")
  credentials = local.creds
}