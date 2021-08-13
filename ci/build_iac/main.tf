terraform {
  backend "gcs" {
    bucket  = "research-computing-cloud_cloudbuild"
    prefix  = "fluid-cicb-ci"
  }
}

provider "google" {
}

resource "google_cloudbuild_trigger" "rcc_cluster" {
  count = length(var.builds)
  name = ""
  project = var.builds[count.index].project
  description = var.builds[count.index].description
  github {
    owner = "FluidNumerics"
    name = "fluid-cicb"
    push {
      branch = var.builds[count.index].branch
    }
  }
  filename = "ci/cloudbuild.yaml"
}
