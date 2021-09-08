terraform {
  backend "gcs" {
    bucket  = "research-computing-cloud_cloudbuild"
    prefix  = "fluid-cicb-ci"
  }
}

provider "google" {
}


locals {
  bld_branch = {for bld in var.builds : bld.name => bld.branch}
  bld_description = {for bld in var.builds : bld.name => bld.description}
  bld_project = {for bld in var.builds : bld.name => bld.project}
  bld_artifact_tag = {for bld in var.builds : bld.name => bld.artifact_tag}
  bld_disabled = {for bld in var.builds : bld.name => bld.disabled}
}

resource "google_cloudbuild_trigger" "rcc_cluster" {
  for_each = local.bld_description
  name = each.key
  description = each.value
  project = local.bld_project[each.key]
  disabled = local.bld_disabled[each.key]
  github {
    owner = "FluidNumerics"
    name = "fluid-run"
    push {
      branch = local.bld_branch[each.key]
    }
  }
  substitutions = {
    _ARTIFACT_TAG = local.bld_artifact_tag[each.key]
  }
  filename = "ci/cloudbuild.yaml"
}
