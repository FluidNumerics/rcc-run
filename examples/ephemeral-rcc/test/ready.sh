#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --time=05:00
# Note : WORKSPACE is a variable that is automatically set by fluid-cicb.
#        If you want to use this script in production, set the WORKSPACE 
#        environment variable to point to the location of the Singularity
#        image file.
#    
#        SINGULARITY_IMAGE is a variable that is automatically set by fluid-cicb
#        that points to your singularity image (full path)
#       

cd ${WORKSPACE}

spack load singularity
singularity exec ${SINGULARITY_IMAGE} /usr/games/cowsay "Looks like you're ready for continuous integration and continuous benchmarking!"
