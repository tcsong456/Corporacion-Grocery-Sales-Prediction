terraform {
  backend "gcs" {
    bucket = "tfstate-corporacion-sales-prediction"
    prefix = "infra"
  }
}