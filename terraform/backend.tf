terraform {
  backend "gcs" {
    bucket = "tfstate-corporacion-sales-forecasting"
    prefix = "infra"
  }
}