locals {
project_id         = "${var.project_id}"
project_nbr        = "${var.project_nbr}"
region             = "${var.region}"
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
  "roles/storage.objectAdmin",
  "roles/storage.bucketCreator",
  "roles/storage.objectCreator"
]
composer_apis = [
    "cloudresourcemanager.googleapis.com",  # Required for IAM operations
    "composer.googleapis.com",             # Cloud Composer API
    "compute.googleapis.com",              # Compute Engine API
    "storage.googleapis.com",              # Cloud Storage API
    "iam.googleapis.com",                  # IAM API
    "container.googleapis.com",            # Kubernetes Engine API
    "sqladmin.googleapis.com",           # Cloud SQL API (if using Airflow database)
    "servicenetworking.googleapis.com"
  ]
}

resource "google_project_service" "enable_resource_manager" {
  project = var.project_id
  service = "cloudresourcemanager.googleapis.com"
  disable_dependent_services = true
}

resource "google_project_service" "enable_composer_required_apis" {
  for_each = toset(local.composer_apis)
  project  = local.project_id
  service  = each.key
  disable_dependent_services = true
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

resource "time_sleep" "wait_for_roles" {
  create_duration = "120s"
  depends_on = [google_project_iam_member.composer_roles]
}

module "vpc_creation" {
  source         = "terraform-google-modules/network/google"
  project_id     = local.project_id
  network_name   = "corpor-sales-vpc"
  
  subnets = [
             {
               subnet_name   = "corpor-sales-subnet"
               subnet_ip     = "10.0.0.0/16"
               subnet_region = "${local.region}"
               subnet_private_access = true
               subnet_enable_private_google_access = true
               }
              ]
  secondary_ranges = {
     "corpor-sales-subnet" = [
       {
          range_name      = "pods"
          ip_cidr_range   = "10.1.0.0/17"
          
          range_name      = "services"
          ip_cidr_range   = "10.2.0.0/22"
                       }
     ]
  
  }
  depends_on = [time_sleep.wait_for_roles]
}

resource "google_compute_global_address" "reserved_ip_for_psa" {
  provider       = google-beta
  name           = "psa-ips"
  purpose        = "VPC_PEERING"
  network        = "projects/${local.project_id}/global/networks/corpor-sales-vpc"
  address_type   = "INTERNAL"
  prefix_length  = 16
  depends_on = [
                 module.vpc_creation
                  ]
}

resource "google_service_networking_connection" "private_connection_with_service_networking" {
  network = "projects/${local.project_id}/global/networks/corpor-sales-vpc"
  service = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.reserved_ip_for_psa.name]
  depends_on = [
               time_sleep.wait_for_composer_apis,
               module.vpc_creation,
               google_compute_global_address.reserved_ip_for_psa
                ]
}

resource "google_compute_firewall" "allow_ingress_on_tcp" {
  project = local.project_id
  name    = "allow-intra-to-tcp"
  network = "corpor-sales-vpc"
  direction = "INGRESS"
  source_ranges = ["10.0.0.0/16"]
  allow {
         protocol = "tcp"
         ports    = [5432]
  }
  description = "allow ingress traffic from within subnet to services listen on port 5432"
  depends_on = [time_sleep.wait_for_roles,
                module.vpc_creation]
}

resource "time_sleep" "wait_for_network_and_firewall_creation" {
  create_duration = "120s"
  depends_on = [module.vpc_creation,
                google_compute_firewall.allow_ingress_on_tcp
                  ]
}


resource "google_composer_environment" "cloud_composer_env_creation" {
  name   = "${local.project_id}-cc3"
  region = local.region
  provider  = google-beta
  config {
     software_config {
         image_version = "composer-3-airflow-2.10.5"
         env_variables = {
              AIRFLOW_VAR_PROJECT_ID  = "${local.project_id}"
              AIRFLOW_VAR_PROJECT_NBR = "${local.project_nbr}"
              AIRFLOW_VAR_REGION      = "${local.region}"
              AIRFLOW_VAR_SUBNET      = "corpor-sales-subnet"
              AIRFLOW_VAR_UMSA_FQN    = "${local.umsa_fqn}"
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
      network    = "corpor-sales-vpc"
      subnetwork = "corpor-sales-subnet"
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


