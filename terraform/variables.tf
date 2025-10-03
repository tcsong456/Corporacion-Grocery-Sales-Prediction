variable "project_id" {
  type        = string
  description = "project id required"
}
variable "region" {
  type        = string
  description = "GCP region"
}
variable "umsa" {
  type        = string
  description = "user managed service account"
}
variable "credential_key_json" {
  type      = string
  sensitive = true
  default   = null
}
variable "gcp_credential_file" {
  type    = string
  default = null
}
variable "trainer_sa" {
  type = string
  description = "training service account"
}
variable "pipeline_sa" {
  type = string
  description = "pipeline service account"
}
variable "kfp_sa" {
  type = string
  description = "kfp service account"
}
variable "preds_dataset" {
  type = string
}
variable "preds_table" {
  type = string
}