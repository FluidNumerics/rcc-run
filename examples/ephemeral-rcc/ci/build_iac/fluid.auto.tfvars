project = "<project>"
github_owner = "<github_owner>"
github_repo = "<github_repo>"
cloudbuild_path = "ci/cloudbuild.yaml"

builds = [{name="main-build-demo",
           description="Demo build of a main branch",
           branch="main",
           image="projects/research-computing-cloud/global/images/family/rcc-centos-7-v3",
           zone="us-west1-b"
         }]

