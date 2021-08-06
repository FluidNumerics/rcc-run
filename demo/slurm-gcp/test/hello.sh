#!/bin/bash
#SBATCH --ntasks=1

module purge
module load gcc singularity
singularity exec /apps/workspace/cowsay.sif /usr/games/cowsay "Great.. I'm self aware."
    {"command_group":"cowsay","execution_command":"/usr/games/cowsay \"Looks like you're ready for continuous integration and continuous benchmarking!\"","output_directory":"dir1"}
