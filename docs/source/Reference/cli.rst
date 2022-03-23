########################
Command Line Interface
########################

*************************
Usage
*************************
The rcc-run container is intended to be used as a build step in Google Cloud Build. Once you create the rcc-run container image, you can call it in your cloud build configuration file using something like the following:


.. code-block:: yaml

  - id: CI/CB
    name: 'gcr.io/${PROJECT_ID}/rcc-run'
    args: 
    - '--build-id=${BUILD_ID}'
    - '--git-sha=${COMMIT_SHA}'
    - '--singularity-image=cowsay.sif'
    - '--project=${PROJECT_ID}'

In this example, a minimal set of arguments are provided to rcc-run to run tests on a singularity image called `cowsay.sif`. By default, rcc-run looks for a CI file at `./rcc-run.yaml` in your repository. 


*************************
CLI Arguments
*************************

There are a number of options to customize the behavior of rcc-run. The table below provides a complete summary of the arguments along with their default values.

==========================   ========    =============   =========================================================
Argument                     Required    Artifact Type   Default Value
==========================   ========    =============   =========================================================
--build-id                   Yes         All             ""
--cluster-type               No          All             rcc-ephemeral
--git-sha                    Yes         All             ""
--ci-file                    No          All             ./rcc-run.yaml
--node-count                 No          All             1
--machine-type               No          All             c2-standard-8
--compiler                   No          All             ""
--target-arch                No          All             ""
--gpu-count                  Yes         All             0
--gpu-type                   Yes         All             ""
--nproc                      No          All             1
--task-affinity              Yes         All             ""
--mpi                        Yes         All             false 
--vpc-subnet                 No          All             "" 
--service-account            No          All             rcc-run@${PROJECT}.iam.gserviceaccount.com
--artifact-type              Yes         All             singularity
--singularity-image          Yes         singularity     ""
--gce-image                  No          All             project/research-computing-cloud/global/images/rcc-foss
--project                    Yes         All             ""
--zone                       No          All             us-west1-b
--rcc-controller             Yes         All             ""
--rcc-tfvars                 No          All             ./fluid.auto.tfvars
--save-results               No          All             false
--ignore-exit-code           No          All             false
--ignore-job-dependencies    No          All             false
==========================   ========    =============   =========================================================

This next table gives a description for each of the command line arguments.
