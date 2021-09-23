########################
Command Line Interface
########################

*************************
Usage
*************************
The fluid-run container is intended to be used as a build step in Google Cloud Build. Once you create the fluid-run container image, you can call it in your cloud build configuration file using something like the following:


.. code-block:: yaml

  - id: CI/CB
    name: 'gcr.io/${PROJECT_ID}/fluid-run'
    args: 
    - '--build-id=${BUILD_ID}'
    - '--git-sha=${COMMIT_SHA}'
    - '--singularity-image=cowsay.sif'
    - '--project=${PROJECT_ID}'

In this example, a minimal set of arguments are provided to fluid-run to run tests on a singularity image called `cowsay.sif`. By default, fluid-run would look for a CI file at `./fluid-run.yaml` in your repository. Additionally, it would use a `rcc-ephemeral` cluster type for testing and only expose a limited set of machine types for running tests and benchmarks.

*************************
CLI Arguments
*************************

There are a number of options to customize the behavior of fluid-run. The table below provides a complete summary of the arguments along with their default values.

==========================   ========  ==============   =============   =========================================================
Argument                     Required  Cluster Type     Artifact Type   Default Value
==========================   ========  ==============   =============   =========================================================
--build-id                   Yes       All              All             ""
--cluster-type               No        All              All             rcc-ephemeral
--git-sha                    Yes       All              All             ""
--ci-file                    No        All              All             ./fluid-run.yaml
--node-count                 No        GCE              All             1
--machine-type               No        GCE              All             c2-standard-8
--compiler                   No        All              All             ""
--target-arch                No        All              All             ""
--gpu-count                  Yes       GCE              All             0
--gpu-type                   Yes       GCE              All             ""
--nproc                      No        GCE              All             1
--task-affinity              Yes       GCE              All             ""
--mpi                        Yes       GCE              All             false 
--vpc-subnet                 No        All              All             "" 
--service-account            No        GCE              All             fluid-run@${PROJECT}.iam.gserviceaccount.com
--artifact-type              Yes       All              All             singularity
--singularity-image          Yes       All              singularity     ""
--gce-image                  No        All              All             project/research-computing-cloud/global/images/rcc-foss
--project                    Yes       All              All             ""
--zone                       No        All              All             us-west1-b
--rcc-controller             Yes       RCC-Static       All             ""
--rcc-tfvars                 No        RCC-Ephemeral    All             ./fluid.auto.tfvars
--save-results               No        All              All             false
--ignore-exit-code           No        All              All             false
--ignore-job-dependencies    No        All              All             false
==========================   ========  ==============   =============   =========================================================

This next table gives a description for each of the command line arguments.
