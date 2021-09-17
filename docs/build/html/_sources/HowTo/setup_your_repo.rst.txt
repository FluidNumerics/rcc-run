Set Up your Repository
=======================
To use fluid-run, you need to have (at a minimum) a Google Cloud Build configuration file and a fluid-run pipeline file. The simplest location for these files is in the root directory of your repository.

.. code-block:: shell

    Repository Root
    o
    |
    |
    o ./cloudbuild.yaml
    |
    |
    o ./fluid-run.yaml


The :code:`cloudbuild.yaml` configuration file specifies the steps necessary to build your application and includes a call to fluid-run to test and benchmark your application. Currently, fluid-run is able to test Singularity and Google Compute Engine (GCE) VM Images. If you're able to create a Docker image for your application, you can easily convert to a Singularity image within your build process before calling fluid-run.

The :code:`fluid-run.yaml` pipeline file specifies a set of commands or scripts to execute, where to direct output, and the compute partitions to run on.


Containerize your application with Singularity
-------------------------------------------------
Containers are a lightweight virtual environment where you install your application and all of it's depedencies. They are ideal for improving portability of your application and can help developers reproduce issues reported by their end users. Singularity is a container format made specifically for high performance computing and research computing environments, where users often share common compute resources. Singularity has some advantages over other container options, such as Docker, including built in support for exposing AMD and Nvidia GPUs and running on multi-VM / cluster environments.

A Singularity image can be created by writing a `Singularity definition file <https://sylabs.io/guides/3.0/user-guide/definition_files.html>`_. The definition file is essentially a set of instructions that dictate the container image to start from and the commands to run to install your application. We recommend that you review the Singularity documentation to learn more about writing a Singularity definition file. If you have not containerized your application yet, this is a good place to start.

Some users have already containerized their application with Docker. If you fall into this category, but would still like to use fluid-run to test and benchmark your application, you can easily convert your Docker image to a Singularity image. In your :code:`cloudbuild.yaml`, you will simply add a step to call :code:`singularity build` using the local docker-daemon as a source. The example below shows a two stage process that creates a Docker image and a Singularity image. After the build completes, the Docker image is posted to `Google Container Registry <https://cloud.google.com/container-registry>`_ and the Singularity image is posted to `Google Cloud Storage <https://cloud.google.com/storage>`_.

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
Tests for your application are specified in the :code:`execution_command` field of the :code:`fluid-run.yaml` pipeline file. The fluid-run build step is able to determine if the provided execution command is a script or a single command. This allows you to either specify all of your tests in a set of scripts in your repository or set individual commands in the :code:`fluid-run.yaml` file. Currently, when using the :code:`rcc-ephemeral` or :code:`rcc-static` cluster types, you must specify a script to run; when using the :code:`gce` cluster type, you must specify individual commands.

As an example, the :code:`fluid-run.yaml` file below runs an inline command on the :code:`c2-standard-8` partition (a partition provided in the default RCC cluster).

.. code-block:: yaml

    tests:
    - command_group: "hello"
      execution_command: "singularity exec ${SINGULARITY_IMAGE} /usr/games/cowsay \"Hello World\""
      output_directory: "hello/test"
      partition: "c2-standard-8"
      batch_options: "--ntasks=1 --cpus-per-task=1"

Alternatively, you could create a script in your repository (e.g. :code:`test/hello_world.sh`) and reference the path to this script in your :code:`fluid-run.yaml` file. In this case, the contents of the script would have the command(s) you want to run.

.. code-block:: shell

    #!/bin/bash
    singularity exec ${SINGULARITY_IMAGE} /usr/games/cowsay "Hello World"

The :code:`fluid-run.yaml` then references this file in the :code:`execution_command` field.

.. code-block:: yaml

    tests:
    - command_group: "hello"
      execution_command: "test/hello_world.sh"
      output_directory: "hello/test"
      partition: "c2-standard-8"
      batch_options: "--ntasks=1 --cpus-per-task=1"


When writing your tests, keep in mind that you can use :doc:`environment variables <../Reference/environment_variables>` provided by fluid-run. If you are using the :code:`rcc-ephemeral` or :code:`rcc-static` clusters, you can also use `Slurm environment variables <https://hpcc.umd.edu/hpcc/help/slurmenv.html>`_. 


Add a Cloud Build Configuration file
--------------------------------------

