#!/usr/bin/env python3
""" An frun module for handling high level settings for frun """

class settings:
    def __init__( self,
                  bqTable="",
                  saveResults=False )

        self.bqTable = bqTable
        self.saveResults = saveResults

