terraform {
  required_version = ">= 1.9.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.10"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.10"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.9"
    }
  }
}

locals {
  project_id = var.project_id
  region     = var.region
  umsa       = var.umsa
  umsa_fqn   = "${local.umsa}@${local.project_id}.iam.gserviceaccount.com"
  composer_roles = [
    "roles/pubsub.admin",
    "roles/eventarc.eventReceiver",
    "roles/eventarc.admin",
    "roles/run.admin",
    "roles/dataproc.worker",
    "roles/composer.worker",
    "roles/composer.user",
    "roles/composer.admin",
    "roles/dataproc.editor",
    "roles/iam.serviceAccountAdmin",
    "roles/artifactregistry.reader",
    "roles/compute.networkAdmin",
    "roles/logging.admin",
    "roles/container.clusterViewer",
    "roles/storage.objectAdmin",
    "roles/storage.objectViewer",
    "roles/storage.objectCreator",
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser"
  ]
  composer_apis = [
    "dataproc.googleapis.com",
    "composer.googleapis.com",
    "compute.googleapis.com",
    "storage.googleapis.com",
    "iam.googleapis.com",
    "container.googleapis.com",
    "sqladmin.googleapis.com",
    "servicenetworking.googleapis.com",
    "bigquery.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudfunctions.googleapis.com",
    "pubsub.googleapis.com",
    "eventarc.googleapis.com",
    "artifactregistry.googleapis.com",
    "run.googleapis.com",
    "serviceusage.googleapis.com",
    "logging.googleapis.com",
    "cloudbilling.googleapis.com",
    "secretmanager.googleapis.com",
    "workflows.googleapis.com",
    "workflowexecutions.googleapis.com"
  ]
}

resource "google_project_service" "enable_resource_manager" {
  project                    = var.project_id
  service                    = "cloudresourcemanager.googleapis.com"
  disable_dependent_services = true
}

resource "google_project_service" "enable_composer_required_apis" {
  for_each                   = toset(local.composer_apis)
  project                    = local.project_id
  service                    = each.key
  disable_dependent_services = true
  depends_on                 = [google_project_service.enable_resource_manager]
}

resource "time_sleep" "wait_for_composer_apis" {
  create_duration = "180s"
  depends_on      = [google_project_service.enable_composer_required_apis]
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

resource "time_sleep" "wait_for_roles" {
  create_duration = "120s"
  depends_on      = [google_project_iam_member.composer_roles]
}

resource "google_artifact_registry_repository" "repo" {
  project       = local.project_id
  location      = local.region
  repository_id = "ml-builds"
  format        = "DOCKER"
  depends_on    = [time_sleep.wait_for_composer_apis]
}

module "vpc_creation" {
  source       = "terraform-google-modules/network/google"
  project_id   = local.project_id
  network_name = "corpor-sales-vpc"
  version      = "~> 7.0"

  subnets = [
    {
      subnet_name                         = "corpor-sales-subnet"
      subnet_ip                           = "10.0.0.0/16"
      subnet_region                       = local.region
      subnet_private_access               = true
      subnet_enable_private_google_access = true
    }
  ]
  secondary_ranges = {
    "corpor-sales-subnet" = [
      {
        range_name    = "pods"
        ip_cidr_range = "10.1.0.0/17"
      },
      {
        range_name    = "services"
        ip_cidr_range = "10.2.0.0/22"
      }
    ]

  }
  depends_on = [time_sleep.wait_for_roles]
}

resource "google_compute_global_address" "reserved_ip_for_psa" {
  provider      = google-beta
  name          = "psa-ips"
  purpose       = "VPC_PEERING"
  network       = "projects/${local.project_id}/global/networks/corpor-sales-vpc"
  address_type  = "INTERNAL"
  prefix_length = 16
  depends_on = [
    module.vpc_creation
  ]
}

resource "google_service_networking_connection" "private_connection_with_service_networking" {
  network                 = "projects/${local.project_id}/global/networks/corpor-sales-vpc"
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.reserved_ip_for_psa.name]
  depends_on = [
    time_sleep.wait_for_composer_apis,
    module.vpc_creation,
    google_compute_global_address.reserved_ip_for_psa
  ]
}

resource "google_compute_firewall" "allow_ingress_on_all" {
  project       = local.project_id
  name          = "allow-intra-to-all"
  network       = "corpor-sales-vpc"
  direction     = "INGRESS"
  source_ranges = ["10.0.0.0/16"]
  allow {
    protocol = "all"
  }
  priority    = 100
  description = "allow ingress traffic from within subnet to services on all ports and protocols"
  depends_on = [time_sleep.wait_for_roles,
  module.vpc_creation]
}

resource "google_compute_firewall" "allow_egress_on_all" {
  name               = "allow-egress-internal"
  network            = "corpor-sales-vpc"
  direction          = "EGRESS"
  destination_ranges = ["10.0.0.0/16"]
  allow {
    protocol = "all"
  }
  priority    = 100
  description = "Allow egress to internal network"
  depends_on = [time_sleep.wait_for_roles,
  module.vpc_creation]
}

resource "google_compute_firewall" "allow_egress_on_google_apis" {
  name               = "allow-google-apis-egress"
  network            = "corpor-sales-vpc"
  direction          = "EGRESS"
  destination_ranges = ["199.36.153.8/30"]
  allow {
    protocol = "all"
  }
  priority    = 110
  description = "Allow egress to Google APIs"
  depends_on = [time_sleep.wait_for_roles,
  module.vpc_creation]
}

resource "time_sleep" "wait_for_network_and_firewall_creation" {
  create_duration = "120s"
  depends_on = [module.vpc_creation,
    google_compute_firewall.allow_ingress_on_all,
    google_compute_firewall.allow_egress_on_all,
    google_compute_firewall.allow_egress_on_google_apis
  ]
}

resource "google_storage_bucket" "build_ctx_bucket" {
  name                        = "${local.project_id}-${local.region}-cb-build"
  location                    = local.region
  uniform_bucket_level_access = true
  force_destroy               = true
}

resource "google_storage_bucket" "corporacion_data_bucket_creation" {
  project                     = local.project_id
  name                        = "corpor-sales-data"
  location                    = local.region
  uniform_bucket_level_access = true
  force_destroy               = true
  depends_on                  = [time_sleep.wait_for_network_and_firewall_creation]
}

resource "google_storage_bucket" "corporacion_lib_bucket_creation" {
  project                     = local.project_id
  name                        = "corpor-sales-lib"
  location                    = local.region
  uniform_bucket_level_access = true
  force_destroy               = true
  depends_on                  = [time_sleep.wait_for_network_and_firewall_creation]
}

resource "google_storage_bucket" "corporacion_scripts_bucket_creation" {
  project                     = local.project_id
  name                        = "corpor-sales-scripts"
  location                    = local.region
  uniform_bucket_level_access = true
  force_destroy               = true
  depends_on                  = [time_sleep.wait_for_network_and_firewall_creation]
}

resource "google_storage_bucket" "corporacion_cloud_function_creation" {
  project                     = local.project_id
  name                        = "${local.project_id}-cloudfunction-bucket"
  location                    = local.region
  uniform_bucket_level_access = true
  force_destroy               = true
  depends_on                  = [time_sleep.wait_for_network_and_firewall_creation]
}

resource "time_sleep" "sleep_after_buckets_creation" {
  create_duration = "60s"
  depends_on = [google_storage_bucket.corporacion_data_bucket_creation,
    google_storage_bucket.corporacion_lib_bucket_creation,
    google_storage_bucket.corporacion_scripts_bucket_creation,
  google_storage_bucket.build_ctx_bucket]
}
/*
resource "google_storage_bucket_object" "corpor_datasets_upload_to_gcs" {
  for_each   = fileset("../data/", "*")
  source     = "../data/${each.value}"
  name       = each.value
  bucket     = google_storage_bucket.corporacion_data_bucket_creation.name
  depends_on = [time_sleep.sleep_after_buckets_creation]
}

resource "time_sleep" "wait_for_data_upload" {
  create_duration = "30s"
  depends_on      = [google_storage_bucket_object.corpor_datasets_upload_to_gcs]
}
*/
resource "null_resource" "download_and_upload_gcs_connector" {
  provisioner "local-exec" {
    command     = <<EOT
      wget -O gcs-connector-hadoop3-latest.jar "https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar" &&
      gsutil cp gcs-connector-hadoop3-latest.jar "gs://${google_storage_bucket.corporacion_lib_bucket_creation.name}/libs/"
    EOT
    interpreter = ["bash", "-c"]
  }
  depends_on = [time_sleep.sleep_after_buckets_creation]
}

data "google_project" "current" {}

data "archive_file" "dataform_dockerfile_zip" {
  type        = "zip"
  output_path = "${path.module}/dataform_files.zip"

  source {
    content  = file(abspath("../dockerfiles/dataform_dockerfile_automation"))
    filename = "Dockerfile"
  }
  source {
    content  = file("../shell_scripts/cloud_run_dataform.sh")
    filename = "cloud_run_dataform.sh"
  }

  dynamic "source" {
    for_each = fileset("../corpor_sales_dataform", "**")
    content {
      content  = file("../corpor_sales_dataform/${source.value}")
      filename = "corpor_sales_dataform/${source.value}"
    }
  }
}

locals {
  dataform_zip_sha256 = filebase64sha256(data.archive_file.dataform_dockerfile_zip.output_path)
  cloud_build_sa      = "${data.google_project.current.number}@cloudbuild.gserviceaccount.com"
  base_image          = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.repository_id}/dataform"
  image_tag           = "1.0.0"
  image_uri           = "${local.base_image}:${local.image_tag}"
}

resource "google_artifact_registry_repository_iam_member" "cb_ar_writer" {
  location   = local.region
  repository = google_artifact_registry_repository.repo.repository_id
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${local.cloud_build_sa}"
}

resource "google_storage_bucket_iam_member" "cb_gcs_obj_viewer" {
  bucket = google_storage_bucket.build_ctx_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${local.cloud_build_sa}"
}
/*
locals {
  local_promo_dir   = "${path.module}/df_promo_long"
  local_promo_files = fileset(local.local_promo_dir, "*.parquet")
  local_sales_dir   = "${path.module}/df_sales_long"
  local_sales_files = fileset(local.local_sales_dir, "*.parquet")
}

resource "google_storage_bucket_object" "promo_parquet_objects" {
  for_each   = local.local_promo_files
  bucket     = google_storage_bucket.corporacion_data_bucket_creation.name
  name       = "df_promo_long/${each.value}"            # GCS object path
  source     = "${local.local_promo_dir}/${each.value}" # local file (absolute)
  depends_on = [time_sleep.sleep_after_buckets_creation]
}

resource "google_storage_bucket_object" "sales_parquet_objects" {
  for_each   = local.local_sales_files
  bucket     = google_storage_bucket.corporacion_data_bucket_creation.name
  name       = "df_sales_long/${each.value}"            # GCS object path
  source     = "${local.local_sales_dir}/${each.value}" # local file (absolute)
  depends_on = [time_sleep.sleep_after_buckets_creation]
}
*/
resource "google_storage_bucket_object" "dataform_run_src" {
  name           = "source/dataform_run.zip"
  bucket         = google_storage_bucket.build_ctx_bucket.name
  source         = data.archive_file.dataform_dockerfile_zip.output_path
  detect_md5hash = local.dataform_zip_sha256
  depends_on     = [time_sleep.sleep_after_buckets_creation]
}

resource "google_storage_bucket_object" "train_data_process_script_upload" {
  name       = "preprocess/train_data_process.py"
  source     = "../data_preprocess/train_data_process.py"
  bucket     = google_storage_bucket.corporacion_scripts_bucket_creation.name
  depends_on = [time_sleep.sleep_after_buckets_creation]
}

resource "google_storage_bucket_object" "train_test_concat_script_upload" {
  name       = "preprocess/train_test_concat.py"
  source     = "../data_preprocess/train_test_concat.py"
  bucket     = google_storage_bucket.corporacion_scripts_bucket_creation.name
  depends_on = [time_sleep.sleep_after_buckets_creation]
}

resource "google_storage_bucket_object" "unit_sales_nan_fill_script_upload" {
  name       = "preprocess/unit_sales_nan_fill.py"
  source     = "../data_preprocess/unit_sales_nan_fill.py"
  bucket     = google_storage_bucket.corporacion_scripts_bucket_creation.name
  depends_on = [time_sleep.sleep_after_buckets_creation]
}

resource "google_storage_bucket_object" "promo_nan_fill_script_upload" {
  name       = "preprocess/promo_nan_fill.py"
  source     = "../data_preprocess/promo_nan_fill.py"
  bucket     = google_storage_bucket.corporacion_scripts_bucket_creation.name
  depends_on = [time_sleep.sleep_after_buckets_creation]
}

resource "google_storage_bucket_object" "final_process_script_upload" {
  name       = "preprocess/final_process.py"
  source     = "../data_preprocess/final_process.py"
  bucket     = google_storage_bucket.corporacion_scripts_bucket_creation.name
  depends_on = [time_sleep.sleep_after_buckets_creation]
}

resource "null_resource" "container_built_and_push" {
  triggers = {
    src = data.archive_file.dataform_dockerfile_zip.output_md5
    tag = "1.0.0"
  }
  provisioner "local-exec" {
    command = <<-EOT
      set -eu
      gcloud builds submit \
        --project ${var.project_id} \
        --region ${var.region} \
        --tag ${local.image_uri} \
        gs://${google_storage_bucket.build_ctx_bucket.name}/${google_storage_bucket_object.dataform_run_src.name}
      EOT
  }
}

resource "google_composer_environment" "cc3_env_creation" {
  name     = "${local.project_id}-cc3"
  region   = local.region
  provider = google-beta
  config {
    software_config {
      image_version = "composer-3-airflow-2.10.5"
      env_variables = {
        GCP_PROJECT_ID = local.project_id
        GCP_REGION     = local.region
        SUBNET_NM      = "corpor-sales-subnet"
        UMSA           = local.umsa
      }
    }
    workloads_config {
      scheduler {
        cpu        = 2
        memory_gb  = 4
        storage_gb = 20
        count      = 1
      }

      web_server {
        cpu        = 1
        memory_gb  = 2
        storage_gb = 10
      }

      worker {
        cpu        = 4
        memory_gb  = 8
        storage_gb = 50
        min_count  = 3
        max_count  = 6
      }
    }
    environment_size = "ENVIRONMENT_SIZE_MEDIUM"

    node_config {
      network         = "corpor-sales-vpc"
      subnetwork      = "corpor-sales-subnet"
      service_account = local.umsa_fqn
      ip_allocation_policy {
        cluster_secondary_range_name  = "pods"
        services_secondary_range_name = "services"
      }
    }
  }
  depends_on = [time_sleep.wait_for_roles,
  time_sleep.wait_for_network_and_firewall_creation]
}

resource "time_sleep" "sleep_after_composer_creation" {
  create_duration = "180s"
  depends_on      = [google_composer_environment.cc3_env_creation]
}

provider "archive" {}

data "archive_file" "function_package" {
  type        = "zip"
  source_dir  = "../cloud_function"
  output_path = "${path.module}/function.zip"
}

locals {
  function_zip_sha256 = filebase64sha256(data.archive_file.function_package.output_path)
}

resource "google_storage_bucket_object" "upload_function_zip" {
  name           = "function.zip"
  source         = data.archive_file.function_package.output_path
  bucket         = google_storage_bucket.corporacion_cloud_function_creation.name
  detect_md5hash = local.function_zip_sha256
}

resource "google_pubsub_topic" "dags_upload" {
  name       = "cc3-bucket-events"
  depends_on = [time_sleep.wait_for_composer_apis]
}

resource "google_pubsub_topic" "preprocess_all_done" {
  name = "all-preprocess-dags-complete"
}

data "google_storage_project_service_account" "gcs" {
  project    = var.project_id
  depends_on = [time_sleep.wait_for_composer_apis]
}

resource "google_pubsub_topic_iam_binding" "gcs_publisher" {
  topic   = google_pubsub_topic.dags_upload.name
  role    = "roles/pubsub.publisher"
  members = ["serviceAccount:${data.google_storage_project_service_account.gcs.email_address}"]
  depends_on = [time_sleep.wait_for_roles,
  google_pubsub_topic.dags_upload]
}

resource "google_storage_notification" "on_dags_upload" {
  bucket             = split("/", substr(google_composer_environment.cc3_env_creation.config[0].dag_gcs_prefix, 5, -1))[0]
  topic              = google_pubsub_topic.dags_upload.id
  event_types        = ["OBJECT_FINALIZE"]
  object_name_prefix = "dags/_trigger/"
  payload_format     = "JSON_API_V1"
  depends_on         = [google_pubsub_topic_iam_binding.gcs_publisher]
  lifecycle {
    replace_triggered_by = [google_composer_environment.cc3_env_creation]
  }
}

resource "time_sleep" "wait_for_notification" {
  create_duration = "60s"
  depends_on      = [google_storage_notification.on_dags_upload]
}

resource "google_bigquery_dataset" "bq_dataset_creation" {
  dataset_id = "corpor_sales_prediction_dataset"
  location   = local.region
  lifecycle {
    ignore_changes        = [labels]
    create_before_destroy = true
  }
}

resource "google_service_account" "dataform_runner" {
  account_id   = "dataform-runner"
  display_name = "Dataform Runner"
}

resource "google_project_iam_member" "dataform_job_user" {
  project = local.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.dataform_runner.email}"
}

resource "google_project_iam_member" "dataform_ds_creator" {
  project = local.project_id
  role    = "roles/bigquery.user"
  member  = "serviceAccount:${google_service_account.dataform_runner.email}"
}

resource "google_bigquery_dataset_iam_member" "dst_editor" {
  dataset_id = google_bigquery_dataset.bq_dataset_creation.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.dataform_runner.email}"
}

resource "google_storage_bucket_iam_member" "bq_read_gcs" {
  bucket = google_storage_bucket.corporacion_data_bucket_creation.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.dataform_runner.email}"
}

resource "google_artifact_registry_repository_iam_member" "cr_ar_repo_reader" {
  location   = local.region
  repository = google_artifact_registry_repository.repo.repository_id
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.dataform_runner.email}"
}

resource "google_secret_manager_secret" "df_creds" {
  secret_id = "df-credentials"
  replication {
    user_managed {
      replicas {
        location = local.region
      }
    }
  }
  depends_on = [time_sleep.wait_for_composer_apis]
}

resource "google_secret_manager_secret_version" "df_creds_version" {
  secret = google_secret_manager_secret.df_creds.name
  secret_data = jsonencode({
    projectId = local.project_id
    location  = local.region
  })
}

resource "google_secret_manager_secret_iam_member" "df_creds_access" {
  secret_id = google_secret_manager_secret.df_creds.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.dataform_runner.email}"
}

resource "google_cloud_run_v2_job" "dataform_run_job" {
  name     = "corpor-cloud-run"
  location = local.region

  template {
    template {
      service_account = google_service_account.dataform_runner.email

      volumes {
        name = "dfcreds"
        secret {
          secret = google_secret_manager_secret.df_creds.name
          items {
            path    = ".df-credentials.json" # file name inside mount
            version = "latest"
            mode    = 0440
          }
        }
      }

      containers {
        image = local.image_uri

        volume_mounts {
          name       = "dfcreds"
          mount_path = "/run/secrets"
        }

        env {
          name  = "TAGS"
          value = "prod"
        }
        env {
          name  = "ACTIONS"
          value = ""
        }
        env {
          name  = "EXTRA_ARGS"
          value = ""
        }

        resources {
          limits = {
            memory = "8Gi"
            cpu    = "2"
          }
        }
      }

      timeout     = "3600s"
      max_retries = 3
    }

    task_count  = 1
    parallelism = 1
  }
  depends_on = [null_resource.container_built_and_push,
  google_secret_manager_secret_iam_member.df_creds_access]
}


resource "google_service_account" "workflow_sa" {
  account_id   = "workflow-sa"
  display_name = "service account of workflow"
}

resource "google_cloud_run_v2_job_iam_member" "job_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_job.dataform_run_job.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.workflow_sa.email}"
}

resource "google_project_service_identity" "create_workflows_sa" {
  project    = local.project_id
  service    = "workflows.googleapis.com"
  provider   = google-beta # add this if your provider requires beta for this resource
  depends_on = [time_sleep.wait_for_composer_apis]
}

resource "google_workflows_workflow" "start_dataform_job" {
  name            = "start-dataform-job"
  region          = local.region
  service_account = google_service_account.workflow_sa.email
  source_contents = <<-YAML
    main:
      steps:
      - runJob:
          call: http.request
          args:
            url: "https://run.googleapis.com/v2/projects/${local.project_id}/locations/${local.region}/jobs/${google_cloud_run_v2_job.dataform_run_job.name}:run"
            method: POST
            auth: { type: OAuth2 }
          result: runResp
      - done:
          return: $${runResp.body}
  YAML
  depends_on = [time_sleep.wait_for_composer_apis,
  google_project_service_identity.create_workflows_sa]
}

resource "google_service_account" "dags_completion_trigger" {
  account_id   = "eventarc-trigger-sa"
  display_name = "Eventarc trigger service account"
}

resource "google_project_iam_member" "eventarc_workflow_invoker" {
  project = local.project_id
  role    = "roles/workflows.invoker"
  member  = "serviceAccount:${google_service_account.dags_completion_trigger.email}"
}

resource "google_pubsub_topic_iam_member" "eventarc_subscriber" {
  topic  = google_pubsub_topic.preprocess_all_done.name
  role   = "roles/pubsub.subscriber"
  member = "serviceAccount:service-${data.google_project.current.number}@gcp-sa-eventarc.iam.gserviceaccount.com"
}

resource "google_pubsub_topic_iam_member" "composer_publisher" {
  topic  = google_pubsub_topic.preprocess_all_done.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${local.umsa_fqn}"
}

resource "google_eventarc_trigger" "dataform_on_airflow_completion" {
  name     = "trigger-after-all-dags-done"
  location = local.region

  matching_criteria {
    attribute = "type"
    value     = "google.cloud.pubsub.topic.v1.messagePublished"
  }

  destination {
    workflow = google_workflows_workflow.start_dataform_job.id
  }

  transport {
    pubsub {
      topic = google_pubsub_topic.preprocess_all_done.id
    }
  }

  service_account = google_service_account.dags_completion_trigger.email

  depends_on = [google_project_iam_member.eventarc_workflow_invoker,
    google_pubsub_topic_iam_member.eventarc_subscriber,
  google_pubsub_topic_iam_member.composer_publisher]
}

resource "google_cloudfunctions2_function" "trigger_dag" {
  name     = "cc3-trigger-dags"
  location = local.region
  project  = local.project_id

  build_config {
    runtime     = "python310"
    entry_point = "handler"
    source {
      storage_source {
        bucket = google_storage_bucket.corporacion_cloud_function_creation.name
        object = google_storage_bucket_object.upload_function_zip.name
      }
    }
  }

  service_config {
    available_memory = "256M"
    timeout_seconds  = 120
    ingress_settings = "ALLOW_INTERNAL_ONLY"

    environment_variables = {
      PROJECT_ID   = local.project_id
      REGION       = local.region
      COMPOSER_ENV = "${local.project_id}-cc3"
      DAG_ID       = "corpor-sales-prediction"
      #      DAG_ID = "test_preprocess_done_signal"
    }
    service_account_email = local.umsa_fqn
  }

  event_trigger {
    trigger_region = local.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.dags_upload.id
  }

  depends_on = [time_sleep.wait_for_composer_apis,
    google_storage_notification.on_dags_upload,
    google_storage_bucket_object.upload_function_zip,
    google_pubsub_topic_iam_binding.gcs_publisher
  ]
}

resource "time_sleep" "wait_for_cloud_function" {
  create_duration = "60s"
  depends_on      = [google_cloudfunctions2_function.trigger_dag]
}

resource "google_storage_bucket_object" "upload_dag_to_cc3" {
  name   = "dags/data_airflow.py"
  source = "../data_preprocess/data_airflow.py"
  #  name = "dags/dummy_run.py"
  #  source = "../data_preprocess/dummy_run.py"
  bucket = split("/", substr(google_composer_environment.cc3_env_creation.config[0].dag_gcs_prefix, 5, -1))[0]
  #  metadata = { ci_build = var.build_id }
  depends_on = [time_sleep.sleep_after_composer_creation,
    time_sleep.wait_for_notification,
    time_sleep.wait_for_cloud_function
  ]
}
#time_sleep.wait_for_data_upload