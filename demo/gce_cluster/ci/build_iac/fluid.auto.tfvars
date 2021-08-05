project = "hpc-apps"
zone = "us-west1-b"
github_owner = "FluidNumerics"
github_repo = "fluid-cicb"
cloudbuild_path = "demo/ci/cloudbuild.yaml"

builds = [{name="main-build-demo",
           description="Demo build of a main branch",
           branch="main",
           zone="us-west1-b",
           node_count=1,
           machine_type="n1-standard-2",
           gpu_count=0,
           gpu_type="",
           nproc=1,
           task_affinity="",
           mpi="",
           profile=""}]

