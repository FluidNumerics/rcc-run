#!/usr/bin/env python3
""" An frun module for handling job pipelines """


class jobs:
    def __init__( jobFile="",
                  joblist=[],
                  stats={} )

    def load( self, filename="" ):
        """ Loads jobs from file. """

    def insert( self, 
                name, 
                group=""
                directory="", 
                partition="", 
                batchOpts="", 
                exeCommand="",
                dependencies=[] )
    """ Inserts a job at the end of the job list """

    def delete( self, name ):
        """ Removes a pipeline step with the given name """
