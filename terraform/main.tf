locals {
project_id         = "${var.project_id}"
#project_nbr        = "${var.project_nbr}"
umsa               = "${var.umsa}"
umsa_fqn           = "${local.umsa}@${local.project_id}.iam.gserviceaccount.com"
composer_roles = [
  "roles/composer.worker",
  "roles/composer.admin",
  "roles/iam.serviceAccountAdmin",
  "roles/storage.admin",
  "roles/artifactregistry.reader",
  "roles/compute.networkAdmin",
  "roles/logging.admin",
  "roles/container.clusterViewer",
]
composer_apis = [
    "cloudresourcemanager.googleapis.com",  # Required for IAM operations
    "composer.googleapis.com",             # Cloud Composer API
    "compute.googleapis.com",              # Compute Engine API
    "storage.googleapis.com",              # Cloud Storage API
    "iam.googleapis.com",                  # IAM API
    "container.googleapis.com",            # Kubernetes Engine API
    "sqladmin.googleapis.com"              # Cloud SQL API (if using Airflow database)
  ]
}

resource "google_project_service" "enable_resource_manager" {
  project = var.project_id
  service = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "enable_composer_required_apis" {
  for_each = toset(local.composer_apis)
  project  = local.project_id
  service  = each.key
  disable_on_destroy = true
  depends_on = [google_project_service.enable_resource_manager]
}

resource "time_sleep" "wait_for_composer_apis" {
  create_duration = "180s"
  depends_on = [google_project_service.enable_composer_required_apis]
}

resource "google_project_iam_member" "composer_roles" {
  for_each = toset(local.composer_roles)
  project  = local.project_id
  role     = each.key
  member   = "serviceAccount:${local.umsa_fqn}"
  depends_on = [
                time_sleep.wait_for_composer_apis
                ]
}
