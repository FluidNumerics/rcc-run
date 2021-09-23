####################
Fluid Run Workflow
####################



*********
Examples
*********

Singularity Image Benchmarking
===============================

During the build, Docker and Singularity images will be created and the Singularity image will be passed to fluid-run for testing. The tests that are run are specified in :code:`~/fluid-run/examples/rcc-ephemeral/fluid-run.yaml`. After building the images, fluid-run creates an ephemeral RCC cluster, which provides a Slurm job scheduler and a set of compute partitions that give you access to multiple machine types on Google Cloud. The :code:`fluid-run.yaml` file is used to specify the scripts that are run to test your application, the partition to run them on, the directory to work from (relative to a unique working directory for your build), and any options to send to the batch scheduler. For this example,

.. code-block:: yaml

    tests:
      - command_group: "sleep"
        execution_command: "test/sleep10.sh"
        output_directory: "sleep"
        partition: "c2-standard-8"
        batch_options: "--ntasks=1 --cpus-per-task=1 --time=05:00"
    
      - command_group: "cowsay"
        execution_command: "test/hello.sh"
        output_directory: "cowsay-hello"
        partition: "c2-standard-8"
        batch_options: "--ntasks=1 --cpus-per-task=1 --time=05:00"
    
      - command_group: "cowsay"
        execution_command: "test/ready.sh"
        output_directory: "cowsay-ready"
        partition: "c2-standard-8"
        batch_options: "--ntasks=1 --cpus-per-task=1 --time=05:00"

Execution commands are grouped into "command groups"; by default, commands in a command group are executed sequentially and in the order they are specified in the file. Passing the :code:`--ignore-job-dependencies` flag to :code:`fluid-run` will ignore dependencies in command groups.

