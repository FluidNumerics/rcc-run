#!/usr/bin/env python3
""" A module for frun that is used to define and work with clusters on Google Cloud """


class cluster:
    def __init__( clusterType="gce",
                  serviceAccount="default",
                  vmImage="projects/research-computing-cloud/global/images/family/fluid-run-foss",
                  hostname="",
                  availType="ephemeral",
                  nodeCount=1,
                  machineType="c2-standard-4",
                  gpuType=None,
                  gpuCount=0,
                  project="",
                  vpc_subnet="default",
                  zone="us-west1-b",
                  connectionRetries=300 )
                  
                  
    def describe( self ):
        """ Prints human readable description of the cluster to the screen """

    def provision( self ):
        """ Provisions cluster resources and updated any cluster metadata upon deployment """

    def deprovision( self ):
        """ Removes cluster resources """

    def checkConnection( self ):
        """ Checks for ssh connection to cluster """

    def uploadPath( self, localPath, remotePath ):
        """ Uploads a local path to a remote path on the cluster """





