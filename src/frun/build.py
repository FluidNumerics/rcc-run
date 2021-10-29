#!/usr/bin/env python3
""" An frun module for describing application builds """


class build:
    def __init__( self,
                  artifactType="",
                  buildId=""
                  gitRepo="",
                  gitSha="",
                  compiler="",
                  compilerFlags="",
                  dependencies=[],
                  operatingSystem="",
                  cpuTargetArch="",
                  gpuTargetArch="")

        self.artifactType = artifactType
        self.buildId = buildId
        self.gitRepo = gitRepo
        self.gitSha = gitSha
        self.compiler = compiler
        self.compilerFlags = compilerFlags
        self.dependencies = dependencies
        self.operatingSystem = operatingSystem
        self.cpuTargetArch = cpuTargetArch
        self.gpuTargetArch = gpuTargetArch


    def describe( self ):
        """ Describes your application build in human readable form """

        print("Artifact Type : ".format(self.artifactType))
        print("Build Id : ".format(self.buildId))
        print("Git Repository :".format(self.gitRepo))
        print("Git SHA :".format(self.gitSha))
        print("Compiler : ".format(self.compiler))
        print("Compiler Flags : ".format(self.compilerFlags))
        print("Dependencies : ".format(', '.join(self.dependencies)))
        print("Operating System : ".format(self.operatingSystem))
        print("GPU Target Architecture : ".format(self.cpuTargetArch))
        print("GPU Target Architecture : ".format(self.gpuTargetArch))


    def todict( self ):
        """ Converts the build object to a dictionary """

        build = {"artifact_type":self.artifactType,
                 "build_id":self.buildId,
                 "git_repo":self.gitRepo,
                 "git_sha":self.gitSha,
                 "compiler":self.compiler,
                 "compiler_flags":self.compilerFlags,
                 "dependencies":self.dependencies,
                 "operating_system":self.operatingSystem,
                 "cpu_target":self.cpuTargetArch,
                 "gpu_target":self.gpuTargetArch}

        return build
