
variable "builds" {
  type = list(object({
    name = string
    description = string
    branch = string
    image = string
    zone = string}))
  default = []
  description = "List of build triggers and their settings to configure"
}

variable "bq_location" {
  type = string
  description = "Valid location for Big Query Dataset. https://cloud.google.com/bigquery/docs/locations"
  default = "US"
}

variable "cloudbuild_path" {
  type = string
  description = "Path to the cloudbuild.yaml file in the Github repository"
  default = "ci/cloudbuild.yaml"
}

variable "github_owner" {
  type = string
  description = "The owner of the Github repository"
  default = null
}

variable "github_repo" {
  type = string
  description = "The name of the Github repository"
  default = null
}

variable "project" {
  type = string
  description = "GCP Project ID"
}

variable "subnet_cidr" {
  type = string
  description = "CIDR Range for the subnet (if vpc_subnet is not provided)."
  default = "10.10.0.0/16"
}

variable "whitelist_ssh_ips" {
  type = list(string)
  description = "IP addresses that should be added to a whitelist for ssh access"
  default = ["0.0.0.0/0"]
}
