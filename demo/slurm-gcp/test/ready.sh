#!/bin/bash
#SBATCH --ntasks=1

singularity exec /apps/workspace/cowsay.sif /usr/games/cowsay "Looks like you're ready for continuous integration and continuous benchmarking!"
