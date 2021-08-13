#!/bin/bash
#SBATCH --ntasks=1
# Note : WORKSPACE is a variable that is automatically set by fluid-cicb.
#        If you want to use this script in production, set the WORKSPACE 
#        environment variable to point to the location of the Singularity
#        image file.

singularity exec ${WORKSPACE}/cowsay.sif /usr/games/cowsay "Looks like you're ready for continuous integration and continuous benchmarking!"
