// Service account for CI tests
resource "google_service_account" "fluid_run" {
  account_id = "fluid-run"
  display_name = "Continuous Integration Service account"
  project = var.project
}

// **** Create the Shared VPC Network **** //
resource "google_compute_network" "vpc_network" {
  name = "fluid-run"
  project = var.project
  auto_create_subnetworks = true
}

resource "google_compute_firewall" "default_ssh_firewall_rules" {
  name = "fluid-run-ssh"
  network = google_compute_network.vpc_network.self_link
  target_tags = ["fluid-run"]
  source_ranges = var.whitelist_ssh_ips
  project = var.project

  allow {
    protocol = "tcp"
    ports = ["22"]
  }
}

resource "google_compute_firewall" "default_internal_firewall_rules" {
  name = "fluid-run-all-internal"
  network = google_compute_network.vpc_network.self_link
  source_tags = ["fluid-run"]
  target_tags = ["fluid-run"]
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


// Big Query Dataset for CICB Data
resource "google_bigquery_dataset" "fluid_run" {
  dataset_id = "fluid_cicb"
  friendly_name = "Fluid CI/CB data"
  description = "A dataset containing build information for the Fluid CI/CB pipeline."
  location = var.bq_location
  project = var.project
}

resource "google_bigquery_table" "benchmarks" {
  dataset_id = google_bigquery_dataset.fluid_run.dataset_id
  table_id = "app_runs"
  project = var.project
  deletion_protection=false
  schema = <<EOF
[
  {
    "name": "allocated_cpus",
    "type": "INT64",
    "mode": "NULLABLE",
    "description": "The number of CPUs that are allocated to run the execution_command."
  },
  {
    "name": "allocated_gpus",
    "type": "INT64",
    "mode": "NULLABLE",
    "description": "The number of GPUs that are allocated to run the execution_command."
  },
  {
    "name": "batch_options",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Additional options sent to the batch scheduler."
  },
  {
    "name": "command_group",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "An identifier to allow grouping of execution_commands in reporting. This is particularly useful if you are exercising multiple options for the same CLI command and want to be able to group results and profile metrics for multiple execution commands."
  },
  {
    "name": "controller_machine_type",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Machine type used for the controller, for Slurm based test environments."
  },
  {
    "name": "controller_disk_size_gb",
    "type": "INT64",
    "mode": "NULLABLE",
    "description": "The size of the controller disk in GB."
  },
  {
    "name": "controller_disk_type",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "The type of disk used for the controller."
  },
  {
    "name": "compact_placement",
    "type": "BOOL",
    "mode": "NULLABLE",
    "description": "A flag to indicate if compact placement is used."
  },
  {
    "name": "gvnic",
    "type": "BOOL",
    "mode": "NULLABLE",
    "description": "A flag to indicate if Google Virtual NIC is used."
  },
  {
    "name": "filestore",
    "type": "BOOL",
    "mode": "NULLABLE",
    "description": "A flag to indicated if filestore is used for workspace."
  },
  {
    "name": "filestore_tier",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "The filestore tier used for file IO."
  },
  {
    "name": "filestore_capacity_gb",
    "type": "INT64",
    "mode": "NULLABLE",
    "description": "The size of the filestore disk capacity in GB."
  },
  {
    "name": "lustre",
    "type": "BOOL",
    "mode": "NULLABLE",
    "description": "A flag to indicated if lustre is used for workspace."
  },
  {
    "name": "lustre_image",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "The VM image used for the Lustre deployment."
  },
  {
    "name": "lustre_mds_node_count",
    "type": "INT64",
    "mode": "NULLABLE",
    "description": "Number of Lustre metadata servers"
  },
  {
    "name": "lustre_mds_machine_type",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "The machine type for the Lustre MDS servers."
  },
  {
    "name": "lustre_mds_boot_disk_type",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "The boot disk type for the Lustre MDS servers."
  },
  {
    "name": "lustre_mds_boot_disk_size_gb",
    "type": "INT64",
    "mode": "NULLABLE",
    "description": "The size of the Lustre boot disk in GB."
  },
  {
    "name": "lustre_mdt_disk_type",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "The mdt disk type for the Lustre MDS servers."
  },
  {
    "name": "lustre_mdt_disk_size_gb",
    "type": "INT64",
    "mode": "NULLABLE",
    "description": "The size of the Lustre boot disk in GB."
  },
  {
    "name": "lustre_mdt_per_mds",
    "type": "INT64",
    "mode": "NULLABLE",
    "description": "The number of metadata targets per MDS."
  },
  {
    "name": "lustre_oss_node_count",
    "type": "INT64",
    "mode": "NULLABLE",
    "description": "Number of Lustre metadata servers"
  },
  {
    "name": "lustre_oss_machine_type",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "The machine type for the Lustre OSS servers."
  },
  {
    "name": "lustre_oss_boot_disk_type",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "The boot disk type for the Lustre OSS servers."
  },
  {
    "name": "lustre_oss_boot_disk_size_gb",
    "type": "INT64",
    "mode": "NULLABLE",
    "description": "The size of the Lustre boot disk in GB."
  },
  {
    "name": "lustre_ost_disk_type",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "The ost disk type for the Lustre OSS servers."
  },
  {
    "name": "lustre_ost_disk_size_gb",
    "type": "INT64",
    "mode": "NULLABLE",
    "description": "The size of the Lustre boot disk in GB."
  },
  {
    "name": "lustre_ost_per_oss",
    "type": "INT64",
    "mode": "NULLABLE",
    "description": "The number of object storage targets per OSS."
  },
  {
    "name": "compiler",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Compiler name and version, e.g. `gcc@10.2.0`, used to build application (if applicable)"
  },
  {
    "name": "target_arch",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Architecture targeted by compiler during application build process."
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
    "name": "max_memory_gb",
    "type": "FLOAT64",
    "mode": "NULLABLE",
    "description": "The maximum amount of memory used for the execution_command in GB."
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
  },
  {
    "name": "runtime",
    "type": "FLOAT64",
    "mode": "NULLABLE",
    "description": "The runtime for the execution_command in seconds."
  },
  {
    "name": "vm_image",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "VM image used for the GCE instance running the fluid-run cluster." 
  }
]
EOF
}
