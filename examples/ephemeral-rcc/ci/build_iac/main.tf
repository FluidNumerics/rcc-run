
/*
terraform {
  backend "gcs" {
    bucket  = "my-codes-terraform"
    prefix  = "fluid-cicb"
  }
}
*/

locals {
  bld_description = {for bld in var.builds : bld.name => bld.description}
  bld_branch = {for bld in var.builds : bld.name => bld.branch}
  bld_image = {for bld in var.builds : bld.name => bld.image}
  bld_zone = {for bld in var.builds : bld.name => bld.zone}
}

resource "google_cloudbuild_trigger" "builds" {
  for_each = local.bld_description
  name = each.key
  project = var.project
  description = each.value
  github {
    owner = var.github_owner
    name = var.github_repo
    push {
      branch = local.bld_branch[each.key]
    }
  }
  substitutions = {
  _ZONE = local.bld_zone[each.key]
  _IMAGE = local.bld_gce_image[each.key]
  }
  filename = var.cloudbuild_path
}


module "fluid_cicb" {
  source = "github.com/FluidNumerics/fluid-cicb-tf//modules/"
  bq_location = var.bq_location
  project = var.project
  subnet_cidr = var.subnet_cidr
  whitelist_ssh_ips = var.whitelist_ssh_ips
}
