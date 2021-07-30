/*
terraform {
  backend "gcs" {
    bucket  = "my-codes-terraform"
    prefix  = "fluid-cicb"
  }
}
*/

provider "google" {
}

locals {
  region = trimsuffix(var.zone,substr(var.zone,-2,-2))
}

// Service account for CI tests
resource "google_service_account" "fluid_cicb" {
  account_id = "fluid-cicb"
  display_name = "Continuous Integration Service account"
  project = var.project
}

// **** Create the Shared VPC Network **** //
resource "google_compute_network" "vpc_network" {
  name = "fluid-cicb"
  project = var.project
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "fluid-cicb" {
  name = "fluid-cicb"
  ip_cidr_range = var.subnet_cidr
  region = local.region
  network = google_compute_network.vpc_network.self_link
  project = var.project
}

resource "google_compute_firewall" "default_ssh_firewall_rules" {
  name = "fluid-cicb-ssh"
  network = google_compute_network.vpc_network.self_link
  target_tags = ["fluid-cicb"]
  source_ranges = var.whitelist_ssh_ips
  project = var.project

  allow {
    protocol = "tcp"
    ports = ["22"]
  }
}

resource "google_compute_firewall" "default_internal_firewall_rules" {
  name = "fluid-cicb-all-internal"
  network = google_compute_network.vpc_network.self_link
  source_tags = ["fluid-cicb"]
  target_tags = ["fluid-cicb"]
  project = var.project

  allow {
    protocol = "tcp"
    ports = ["0-65535"]
  }
  allow {
    protocol = "udp"
    ports = ["0-65535"]
  }
  allow {
    protocol = "icmp"
    ports = []
  }
}

resource "google_cloudbuild_trigger" "builds" {
  count = length(var.builds)
  name = var.builds[count.index].name
  project = var.project
  description = var.builds[count.index].description 
  github {
    owner = var.github_owner
    name = var.github_repo
    push {
      branch = var.builds[count.index].branch
    }
  }
  substitutions = {
  _NODE_COUNT = var.builds[count.index].node_count
  _MACHINE_TYPE = var.builds[count.index].machine_type
  _GPU_COUNT = var.builds[count.index].gpu_count
  _GPU_TYPE = var.builds[count.index].gpu_type
  _NPROC = var.builds[count.index].nproc
  _TASK_AFFINITY = var.builds[count.index].task_affinity
  _MPI = var.builds[count.index].mpi
  _PROFILE = var.builds[count.index].profile
  _IMAGE = var.gce_image
  _ZONE = var.zone
  }
  filename = var.cloudbuild_path
}

// Big Query Dataset for CICB Data
resource "google_bigquery_dataset" "fluid_cicb" {
  dataset_id = "fluid_cicb"
  friendly_name = "Fluid CI/CB data"
  description = "A dataset containing build information for the Fluid CI/CB pipeline."
  location = var.bq_location
  project = var.project
}

resource "google_bigquery_table" "benchmarks" {
  dataset_id = google_bigquery_dataset.fluid_cicb.dataset_id
  table_id = "cloud_build_data"
  project = var.project
  deletion_protection=false
  schema = <<EOF
[
  {
    "name": "command_group",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "An identifier to allow grouping of execution_commands in reporting. This is particularly useful if you are exercising multiple options for the same CLI command and want to be able to group results and profile metrics for multiple execution commands."
  },
  {
    "name": "execution_command",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "The full command used to execute this benchmark"
  },
  {
    "name": "build_id",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "The Cloud Build build ID associated with this build."
  },
  {
    "name": "machine_type",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Node types as classified by the system provider."
  },
  {
    "name": "gpu_type",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "The vendor and model name of the GPU (e.g. nvidia-tesla-v100)"
  },
  {
    "name": "gpu_count",
    "type": "INT64",
    "mode": "NULLABLE",
    "description": "The number of GPUs, per compute node, on this compute system."
  },
  {
    "name": "node_count",
    "type": "INT64",
    "mode": "NULLABLE",
    "description": "The number of nodes used in testing."
  },
  {
    "name": "datetime",
    "type": "DATETIME",
    "mode": "REQUIRED",
    "description" : "The UTC date and time of the build."
  },
  {
    "name": "exit_code",
    "type": "INT64",
    "mode": "REQUIRED",
    "description": "The system exit code thrown when executing the execution_command"
  },
  {
    "name": "git_sha",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "The git SHA associated with the version / commit being tested." 
  },
  {
    "name": "stderr",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Standard error." 
  },
  {
    "name": "stdout",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Standard output." 
  },
  {
    "name": "partition",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "(Optional) The name of the scheduler partition to run the job under. If provided, the execution_command is interpreted as the path to a batch script." 
  }
]
EOF
}
