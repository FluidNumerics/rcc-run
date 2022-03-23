#######################
The RCC Run CI File
#######################

************
Overview
************
The RCC Run CI File is a YAML or json file in your repository that specifies the tests/benchmarks you want to run after building your code. Currently, this file consists of the a single list object :code:`tests` that has the following attributes :

* :code:`execution_command` This is the path to a script in your repository to run a specific test
* :code:`command_group` The command group is used to group execution commands that are dependent. Execution commands in the same command group are run sequentially in the order they are placed in the :code:`tests` block, unless the `--ignore-job-dependencies` flag is sent to rcc-run
* :code:`output_directory` The directory on the cluster, relative a unique workspace, where the execution command should be run.
* :code:`partition` The compute partition to run the execution command under. :doc:`See How to Customize the Cluster <../HowTo/customize_cluster>`
* :code:`batch_options` Options to send to `Slurm sbatch <https://slurm.schedmd.com/sbatch.html>`_ to submit the job (excluding the :code:`--partition` option)




************
Example
************
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
