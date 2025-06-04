locals {
project_id         = "${var.project_id}"
project_nbr        = "${var.project_nbr}"
umsa               = "${var.umsa}"
umsa_fqn           = "${local.umsa}@${local.project_id}.iam.gserviceaccount.com"
}

resource "google_project_service" "composer_required_services" {
  for_each = toset([
    "composer.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "compute.googleapis.com",
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "servicenetworking.googleapis.com",
    "vpcaccess.googleapis.com",
    "storage.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "secretmanager.googleapis.com",      # optional
    "cloudfunctions.googleapis.com"      # optional
  ])
  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}
