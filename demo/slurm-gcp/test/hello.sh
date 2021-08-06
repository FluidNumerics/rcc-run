#!/bin/bash
#SBATCH --ntasks=1

singularity exec /apps/workspace/cowsay.sif /usr/games/cowsay "Great.. I'm self aware."
