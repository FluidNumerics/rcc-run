Set Up your Repository
=======================
To use rcc-run, you need to have (at a minimum) a Google Cloud Build configuration file and a rcc-run pipeline file. To help keep your repository organized, we recommend creating a subdirectory to host these files, e.g. :code:`ci/`

.. code-block:: shell

    Repository Root
    o
    |
    |
    o ci/
    |\
    | \
    |  \
    |   o cloudbuild.yaml
    |   |
    |   |
    |   o rcc-run.yaml


The :code:`cloudbuild.yaml` configuration file specifies the steps necessary to build your application and includes a call to rcc-run to test and benchmark your application. Currently, rcc-run is able to test Singularity and Google Compute Engine (GCE) VM Images. If you're able to create a Docker image for your application, you can easily convert to a Singularity image within your build process before calling rcc-run.

The :code:`rcc-run.yaml` pipeline file specifies a set of commands or scripts to execute, where to direct output, and the compute partitions to run on.


Containerize your application with Singularity
-------------------------------------------------
Containers are a lightweight virtual environment where you install your application and all of it's depedencies. They are ideal for improving portability of your application and can help developers reproduce issues reported by their end users. Singularity is a container format made specifically for high performance computing and research computing environments, where users often share common compute resources. Singularity has some advantages over other container options, such as Docker, including built in support for exposing AMD and Nvidia GPUs and running on multi-VM / cluster environments.

A Singularity image can be created by writing a `Singularity definition file <http://docs.ctrliq.com/ctrl-singularity-userdocs/3.7/definition_files.html>`_. The definition file is essentially a set of instructions that dictate the container image to start from and the commands to run to install your application. We recommend that you review the Singularity documentation to learn more about writing a Singularity definition file. If you have not containerized your application yet, this is a good place to start.

Some users have already containerized their application with Docker. If you fall into this category, but would still like to use rcc-run to test and benchmark your application, you can easily convert your Docker image to a Singularity image. In your :code:`cloudbuild.yaml`, you will simply add a step to call :code:`singularity build` using the local docker-daemon as a source. The example below shows a two stage process that creates a Docker image and a Singularity image. After the build completes, the Docker image is posted to `Google Container Registry <https://cloud.google.com/container-registry>`_ and the Singularity image is posted to `Google Cloud Storage <https://cloud.google.com/storage>`_.

.. code-block::  yaml

    steps:
    
    - id: Build Docker Image
      name: 'gcr.io/cloud-builders/docker'
      args: ['build',
             '.',
             '-t',
             'gcr.io/${PROJECT_ID}/cowsay:latest'
      ]
    
    - id: Build Singularity Image
      name: 'quay.io/singularity/singularity:v3.7.1'
      args: ['build',
             'cowsay.sif',
             'docker-daemon://gcr.io/${PROJECT_ID}/cowsay:latest']

    images: ['gcr.io/${PROJECT_ID}/cowsay:latest']
    
    artifacts:
      objects:
        location: 'gs://my-singularity-bucket/latest'
        paths: ['cowsay.sif']


Define Tests
-----------------
Tests for your application are specified in the :code:`execution_command` field of the :code:`rcc-run.yaml` pipeline file. The rcc-run build step is able to determine if the provided execution command is a script or a single command. This allows you to either specify all of your tests in a set of scripts in your repository or set individual commands in the :code:`rcc-run.yaml` file. Currently, when using the :code:`rcc-ephemeral` or :code:`rcc-static` cluster types, you must specify a script to run; when using the :code:`gce` cluster type, you must specify individual commands.

To run tests, you need to create a script in your repository (e.g. :code:`test/hello_world.sh`) and reference the path to this script in your :code:`rcc-run.yaml` file. In this case, the contents of the script would have the command(s) you want to run.

.. code-block:: shell

    #!/bin/bash

    singularity exec ${SINGULARITY_IMAGE} /usr/games/cowsay "Hello World"

The :code:`rcc-run.yaml` then references this file in the :code:`execution_command` field.

.. code-block:: yaml

    tests:
    - command_group: "hello"
      execution_command: "test/hello_world.sh"
      output_directory: "hello/test"
      partition: "c2-standard-8"
      batch_options: "--ntasks=1 --cpus-per-task=1"


When writing your tests, keep in mind that you can use :doc:`environment variables <../Reference/environment_variables>` provided by rcc-run and you can also use `Slurm environment variables <https://hpcc.umd.edu/hpcc/help/slurmenv.html>`_. Further, if you have additional environment variables that need to be defined during execution of your tests, you can use the :code:`ENV_FILE` environment variable,

.. code-block:: shell

    #!/bin/bash

    singularity exec --env-file ${ENV_FILE} ${SINGULARITY_IMAGE} /usr/games/cowsay "Hello World"

The :code:`ENV_FILE` is defined as the path to a file in your repository that defines a set of environment variables passed by using the :code:`--env-file` flag when running :code:`rcc-run`

