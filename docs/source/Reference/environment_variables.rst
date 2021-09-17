
Environment Variables
=====================
When running batch scripts on RCC style platforms and when running in-line commands on GCE clusters, some environment variables are provided for you to use during runtime.

Since RCC clusters use a Slurm job scheduler, you also have access to common `Slurm environment variables <https://hpcc.umd.edu/hpcc/help/slurmenv.html>`_ when `--cluster-type=rcc-static` or `--cluster-type=rcc-ephemeral`.

===================   ==================================================================
Variable              Description
===================   ==================================================================
WORKSPACE             The path to the working directory where your job is executed.
PROJECT               The Google Cloud project hosting your test cluster.
GIT_SHA               The git sha associated with the run test.
SINGULARITY_IMAGE     The full path to the Singularity image on the test cluster.
===================   ==================================================================

Example Job Script (Singularity)
---------------------------------
When writing a job script to test your application, you can use the provided environment variables to reference the working directory and the full path to the Singularity image produced during the build phase in Cloud Build. The example below provides a basic demonstration for using environment variables in your test scripts.

.. code-block:: shell

    #!/bin/bash

    cd ${WORKSPACE}
    spack load singularity
    singularity exec ${SINGULARITY_IMAGE} /usr/games/cowsay "Great.. I'm self aware."
