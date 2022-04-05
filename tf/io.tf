
variable "cloudbuild_roles" {
  type = list(string)
  description = "List of IAM roles to grant your Cloud Build service Account"
  default = ["roles/compute.admin",
             "roles/bigquery.admin",
             "roles/iam.serviceAccountUser",
             "roles/compute.osAdminLogin"]
}

variable "services" {
  type=list(string)
  description="List of services to enable for use with RCC-Run"
  default=["bigquery.googleapis.com",
           "cloudbuild.googleapis.com",
           "compute.googleapis.com",
           "containerregistry.googleapis.com",
           "iam.googleapis.com"]
}
variable "bq_location" {
  type = string
  description = "Valid location for Big Query Dataset. https://cloud.google.com/bigquery/docs/locations"
  default = "US"
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
