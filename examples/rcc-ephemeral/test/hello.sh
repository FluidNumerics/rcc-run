#!/bin/bash
# Note : WORKSPACE is a variable that is automatically set by fluid-cicb.
#        If you want to use this script in production, set the WORKSPACE 
#        environment variable to point to the location of the Singularity
#        image file.
#    
#        SINGULARITY_IMAGE is a variable that is automatically set by fluid-cicb
#        that points to your singularity image (full path)
#       

source /etc/profile.d/z10_spack_environment.sh

cd ${WORKSPACE}
singularity exec ${SINGULARITY_IMAGE} /usr/games/cowsay "Great.. I'm self aware."
