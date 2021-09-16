Ephemeral RCC Tutorial
======================================

Fluid Run can be used to create ephemeral compute resources for testing HPC applications and to record information about the test for later analysis.
This quickstart guide will introduce you to the necessary ingredients for configuring application tests with fluid-run, using an ephemeral Research Computing Cluster (RCC).

You will start by using the rcc-ephemeral example provided in the fluid-run repository. This example creates a Singularity image with the `cowsay` program installed on it and then runs tests for this image on an ephemeral RCC cluster. You will learn how to set up your Google Cloud project and create the necessary resources to support application testing, benchmarking, and logging. Additionally, you'll set up a basic dashboard with Data Studio to visualize and inspect your test results.

Google Cloud Project Setup
---------------------------
To complete this tutorial, you will need to have an active project on Google Cloud. 
Sign up and create your first project by visiting https://console.cloud.google.com

Once your project is ready, `open Cloud Shell <https://shell.cloud.google.com/?show=terminal>`_

You will need to activate the following Google Cloud APIs

* Compute Engine
* Cloud Build
* Big Query
* Identity & Access Management (IAM) 

.. code-block:: shell

    gcloud config set project PROJECT-ID
    gcloud services enable compute.googleapis.com
    gcloud services enable bigquery.googleapis.com
    gcloud services enable iam.googleapis.com
    gcloud services enable cloudbuild.googleapis.com



Create a fluid-run Docker image
--------------------------------
The fluid-run application is a `Cloud Build builder <https://cloud.google.com/build/docs/cloud-builders>`_. A Cloud builder is a Docker image that provides an environment and entrypoint application for carrying out a step in a Cloud Build pipeline. You can create the fluid-run docker image and store it in your Google Cloud project's `Container Registry <https://cloud.google.com/container-registry>`_.

`Open Cloud Shell <https://shell.cloud.google.com/?show=terminal>`_ and clone the fluid-run repository.

.. code-block:: shell

    $ git clone https://github.com/FluidNumerics/fluid-run.git ~/fluid-run

Once you've cloned the repository, navigate to the root directory of the repo and trigger a build of the docker image.

.. code-block:: shell

    $ cd ~/fluid-run/
    $ gcloud builds submit . --config=ci/cloudbuild.yaml --substitutions=SHORT_SHA=latest

This will cause Google Cloud build to create the fluid-run docker image `gcr.io/${PROJECT_ID}/fluid-run:latest` that you can then use in your project's builds.

Create the CI/CB Dataset
---------------------------
The CI/CB dataset is a `Big Query <https://cloud.google.com/bigquery>`_ dataset that is used to store information about each test run with fluid-run. This includes runtimes for each execution command used to test your application. The fluid-run repository comes with a terraform module that can create this dataset for your project. We've also included an example under the `examples/rcc-ephemeral` directory that you will use for the rest of this tutorial.

Navigate to the `examples/rcc-ephemeral/ci/build_iac` directory

.. code-block:: shell

    $ cd ~/fluid-run/examples/rcc-ephemeral/ci/build_iac

The `ci/build_iac` subdirectory contains the `Terraform <https://terraform.io>`_ infrastructure as code for provisioning a VPC network, firewall rules, service account, and the Big Query dataset that all support using fluid-run. This example Terraform module is a template for creating these resources, and the `fluid.auto.tfvars` file in this directory is used to concretize certain variables in the template, so that you can deploy the resources in your project. 

Open `fluid.auto.tfvars` in a text editor and set `<project>` to your Google Cloud Project ID. The command below will quickly do the search and replace for you.

.. code-block:: shell

    $ sed -i "s/<project>/$(gcloud config get-value project)/g" fluid.auto.tfvars

Now, you will execute a workflow typical of Terraform deployments to initialize, validate, plan, and deploy. All of the commands are shown below, but you should review the output from each command before executing the next.

.. code-block:: shell

    $ terraform init
    $ terraform validate
    $ terraform plan
    $ terraform apply --auto-approve

Once this completes, you're ready to run a build using fluid-run.

Mannually Trigger a build
--------------------------
Cloud Build pipelines for a repository are specified in a `build configuration file <https://cloud.google.com/build/docs/build-config-file-schema>`_ written in YAML syntax. In this example, three build steps are provided that create a Docker image, create a Singularity image, and test the Singularity image on an ephemeral RCC cluster. 




Things to consider
-------------------

* Maybe you're really just interested in continuous integration and continuous benchmarking for your application and don't want to manage all of the infrastructure. Fluid Numerics offers a fully managed solution; simply point us to your repository. We'll pass forward costs of Google Cloud and maintain your infrastructure for at a rate that depends on the number of build minutes and the vCPU and GPU hours used. This way you're only billed when you're using our managed solution.

* If you'd like a quicker method for deploying fluid-run infrastructure on your own project, we have a private catalog with click-to-deploy solutions. Reach out to Fluid Numerics to learn how to get access.

* By default, the RCC cluster deploys with a VM image that is licensed to you for free with no technical support. Fluid Numerics offers technical support as well as cloud architecting and engineering services to help you get up and running quickly. Start a conversation with us and let us help make your transition to cloud easy.
 
