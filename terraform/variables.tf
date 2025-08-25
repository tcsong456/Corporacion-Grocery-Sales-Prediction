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