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
variable "project_nbr" {
  type        = string
  description = "project nbr number"
}
variable "credential_key_json" {
  type      = string
  sensitive = true
  defaul    = null
}