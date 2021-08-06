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

// Service Accounts //
resource "google_service_account" "slurm_controller" {
  account_id = "slurm-gcp-controller"
  display_name = "Slurm-GCP Controller Service Account"
  project = var.project
}

resource "google_service_account" "slurm_compute" {
  account_id = "slurm-gcp-compute"
  display_name = "Slurm-GCP Compute Service Account"
  project = var.project
}

// **** IAM Permissions **** ///
resource "google_project_iam_member" "project_compute_image_users" {
  project = var.project
  role = "roles/compute.imageUser"
  member = "serviceAccount:${google_service_account.slurm_controller.email}"
}

resource "google_project_iam_member" "project_compute_admins" {
  project = var.project
  role = "roles/compute.admin"
  member = "serviceAccount:${google_service_account.slurm_controller.email}"
}

resource "google_project_iam_member" "service_account_user" {
  project = var.project
  role = "roles/iam.serviceAccountUser"
  member = "serviceAccount:${google_service_account.slurm_controller.email}"
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
  target_tags = ["fluid-cicb","controller","compute"]
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
  source_tags = ["fluid-cicb","compute","controller"]
  target_tags = ["fluid-cicb","compute","controller"]
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

//locals {
//  region_router_list = [for part in var.partitions : trimsuffix(part.zone,substr(part.zone,-2,-2))]
//}

resource "google_compute_router" "cluster_router" {
  //count = length(local.region_router_list)
  name = "fluid-cicb-router"
  project=var.project
  //region = local.region_router_list[count.index]
  region = local.region
  network =  google_compute_network.vpc_network.self_link
}

resource "google_compute_router_nat" "cluster_nat" {
//  count = length(google_compute_router.cluster_router)
  project=var.project
  depends_on = [google_compute_subnetwork.fluid-cicb]
  name = "fluid-cicb-nat"
//  router                             = google_compute_router.cluster_router[count.index].name
//  region                             = google_compute_router.cluster_router[count.index].region
  router                             = google_compute_router.cluster_router.name
  region                             = google_compute_router.cluster_router.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"
  subnetwork {
//    name                    = local.region_router_list[count.index].subnet
    name                    = google_compute_subnetwork.fluid-cicb.self_link
    source_ip_ranges_to_nat = ["PRIMARY_IP_RANGE"]
  }

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
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
  _REGION = local.region
  _SLURM_CONTROLLER = module.slurm_cluster_controller.controller_node_name
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

module "slurm_cluster_controller" {
  source = "github.com/FluidNumerics/slurm-gcp//tf/modules/controller"
  boot_disk_size                = var.controller_disk_size_gb
  boot_disk_type                = var.controller_disk_type
  image                         = var.controller_image
  instance_template             = var.controller_instance_template
  cluster_name                  = "fluid-cicb"
  compute_node_scopes           = ["https://www.googleapis.com/auth/cloud-platform"]
  compute_node_service_account  = google_service_account.slurm_compute.email
  disable_compute_public_ips    = true
  disable_controller_public_ips = var.disable_controller_public_ips
  labels                        = var.controller_labels
  login_network_storage         = []
  login_node_count              = 0
  machine_type                  = var.controller_machine_type
  munge_key                     = null
  jwt_key                       = null
  network_storage               = []
  partitions                    = var.partitions
  project                       = var.project
  region                        = local.region
  secondary_disk                = var.controller_secondary_disk
  secondary_disk_size           = var.controller_secondary_disk_size
  secondary_disk_type           = var.controller_secondary_disk_type
  shared_vpc_host_project       = var.project
  scopes                        = ["https://www.googleapis.com/auth/cloud-platform"]
  service_account               = google_service_account.slurm_controller.email
  subnet_depend                 = google_compute_subnetwork.fluid-cicb.name
  subnetwork_name               = google_compute_subnetwork.fluid-cicb.name
  suspend_time                  = var.suspend_time
  zone                          = var.zone
}
