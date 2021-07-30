#!/usr/bin/python3

import argparse
import json
import os
import subprocess
import shutil
import shlex
from datetime import datetime
import sys
import time

WORKSPACE='/workspace/'
TFPATH='/opt/fluid-cicb/tf'
SLEEP_INTERVAL=5
SSH_TIMEOUT=300
N_RETRIES=SSH_TIMEOUT/SLEEP_INTERVAL


def clusterRun(cmd):
    """Runs a command over ssh on the head node for the cluster"""

    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)

    hostname = settings['hostname']
    zone = settings['zone']

    command = ['gcloud',
               'compute',
               'ssh',
               hostname,
               '--command="{}"'.format(cmd),
               '--zone={}'.format(zone),
               '--ssh-key-file=/workspace/sshkey']


    proc = subprocess.Popen(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    # Poll process.stdout to show stdout live
    while True:
        output = proc.stdout.readline()
        if proc.poll() is not None:
            break
        if output:
            print(output.decode('utf-8'))

    rc = proc.poll()
    stdout, stderr = proc.communicate()

    checkReturnCode(rc,stderr)

    return rc, stdout, stderr

#END clusterRun

def localRun(cmd):
    """Runs a command in the local environment and returns exit code, stdout, and stderr"""

    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)

    proc = subprocess.Popen(shlex.split(cmd),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    # Poll process.stdout to show stdout live
    while True:
        output = proc.stdout.readline()
        if proc.poll() is not None:
            break
        if output:
            print(output.decode('utf-8'))

    rc = proc.poll()
    stdout, stderr = proc.communicate()

    checkReturnCode(rc,stderr)

    return rc, stdout, stderr

#END localRun

def checkReturnCode(returncode,stderr):
    """Checks the return code. If return code is nonzero, stderr is printed to screen and code is halted with nonzero exit code"""

    if returncode != 0:
        print(stderr)
        sys.exit(1)

def testSSHConnection():
    """Attempts to connect to the head ssh node in a while loop until a connection is made or until timeout"""

    k = 1
    while True:
        
        if k < N_RETRIES :
            print('Waiting for SSH Connection...')
            exit_code,stdout,stderr = clusterRun('hostname')
            if exit_code == 0:
                break
            else:
                time.sleep(SLEEP_INTERVAL)
        else:
            exit_code == -1

    return exit_code

#END testSSHConnection

def createSettingsJson(args):
    """Converts the args namespace to a json dictionary for use in the Cloud Build environment and on the cluster"""

    settings = {'artifact_type':args.artifact_type,
                'build_id':args.build_id,
                'docker_image':args.docker_image,
                'git_sha':args.git_sha,
                'gpu_count':args.gpu_count,
                'gpu_type':args.gpu_type,
                'image':args.image,
                'machine_type':args.machine_type,
                'mpi':args.mpi,
                'node_count':args.node_count,
                'nproc':args.nproc,
                'profile':args.profile,
                'project':args.project,
                'service_account':args.service_account,
                'singularity_image':args.singularity_image,
                'slurm_controller':args.slurm_controller,
                'surface_nonzero_exit_code':args.surface_nonzero_exit_code,
                'task_affinity':args.task_affinity,
                'vpc_subnet':args.vpc_subnet,
                'zone':args.zone,
                'hostname':'fcicb-{}-0'.format(args.build_id[0:7])}

    with open(WORKSPACE+'settings.json','w')as f: 
        f.write(json.dumps(settings))


#END createSettingsJson

def concretizeTfvars():

    print('Concretizing tfvars')
    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)

    with open(TFPATH+'/fluid.tfvars.tmpl', 'r') as f:
        tfvars = f.read()
    
    tfvars = tfvars.replace('<project>',settings['project'])
    tfvars = tfvars.replace('<machine_type>',settings['machine_type'])
    tfvars = tfvars.replace('<node_count>',str(settings['node_count']))
    tfvars = tfvars.replace('<zone>',settings['zone'])
    tfvars = tfvars.replace('<image>',settings['image'])
    tfvars = tfvars.replace('<gpu_type>',settings['gpu_type'])
    tfvars = tfvars.replace('<gpu_count>',str(settings['gpu_count']))
    tfvars = tfvars.replace('<build_id>',settings['build_id'][0:7])
    tfvars = tfvars.replace('<vpc_subnet>',settings['vpc_subnet'])
    tfvars = tfvars.replace('<tags>','fluid-cicb')
    tfvars = tfvars.replace('<service_account>',settings['service_account'])

    print(tfvars)

    with open(TFPATH+'/fluid.auto.tfvars', 'w') as f:
        f.write(tfvars)

#END concretizeTfvars

def provisionCluster():
    """Use Terraform and the provided module to create a GCE cluster to execute work on"""

    print('Provisioning Cluster')
    os.chdir(TFPATH)
    localRun('terraform init')

    localRun('terraform apply --auto-approve')

    exit_code = testSSHConnection()

#END provisionCluster

def createSSHKey():
    """Create an ssh key that can be used to connect with the cluster"""

    localRun('ssh-keygen -b 2048 -t rsa -f /workspace/sshkey -q -N ""')

#END createSSHKey

#def uploadWorkspace():
#
##END

def runExeCommands():
    """Runs the ciRun.py application on the remote cluster"""

    clusterRun('hostname')

#END runExeCommands

#def downloadWorkspace():
#
##END
#
def deprovisionCluster():
    """Use Terraform and the provided module to delete the existing cluster"""

    os.chdir(TFPATH)
    localRun('terraform destroy --auto-approve')

#END deprovisionCluster

def checkExitCodes():
    """Parses the results.json output and reports exit code statistics"""

    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)

    with open(WORKSPACE+'results.json','r')as f:          
        tests = json.load(f)

    results = {}
    sysExitCode = 0
    for test in tests :
        cli_command = test['cli_command']
        if cli_command in results.keys():
            if test['exit_code'] == 0:
                results[cli_command]['npass'] += 1
            else:
                results[cli_command]['nfail'] += 1
                sysExitCode = 1
        else:
            results[cli_command] = {'npass':0,'nfail':0}
            if test['exit_code'] == 0:
                results[cli_command]['npass'] += 1
            else:
                results[cli_command]['nfail'] += 1
                sysExitCode = 1

    print('============================')
    print('')
    print('Exit Code Check')
    print('')
    for cli in results.keys():
      npass = results[cli]['npass']
      nfail = results[cli]['nfail']
      print('============================')
      print('                        ')
      print('  {}'.format(cli))
      print('  > PASS : {}/{}'.format(str(npass),str(npass+nfail)))
      print('  > FAIL : {}/{}'.format(str(nfail),str(npass+nfail)))
      print('  > PASS RATE : {}%'.format(str(npass/(npass+nfail)*100)))
      print('                        ')

    print('============================')

    if settings['exit_on_failure']:
        sys.exit(sysExitCode) 
    else:
        sys.exit(0)

#END checkExitCodes

def parseCli():
    parser = argparse.ArgumentParser(description='Provision remote resources and test HPC/RC applications')
    parser.add_argument('--build-id', help='Cloud Build build ID', type=str)
    parser.add_argument('--git-sha', help='Git sha for your application', type=str)
    parser.add_argument('--node-count', help='Number of nodes to provision for testing', type=int, default=1)
    parser.add_argument('--machine-type', help='GCE Machine type for each node', type=str, default='n1-standard-2')
    parser.add_argument('--gpu-count', help='The number of GPUs per node', type=int, default=0)
    parser.add_argument('--gpu-type', help='The type of GPU to attach to each compute node', type=str, default='')
    parser.add_argument('--nproc', help='The number of processes to launch (MPI)', type=int, default=1)
    parser.add_argument('--task-affinity', help='Task affinity flags to send to MPI.', type=str)
    parser.add_argument('--mpi', help='Boolean flag to indicate whether or not MPI is used', type=bool, default=False)
    parser.add_argument('--profile', help='Boolean flag to enable (true) or disable (false) profiling with the hpc toolkit', type=bool, default=False)
    parser.add_argument('--surface-nonzero-exit-code', help='Boolean flag to surface a nonzero exit code (true) if any of the tests fail', type=bool, default=True)
    parser.add_argument('--vpc-subnet', help='Link to VPC Subnet to use for deployment. If not provided, an ephemeral subnet is created', type=str, default='')
    parser.add_argument('--service-account', help='Service account email address to attach to GCE instance. If not provided, an ephemeral service account is created', type=str, default='')
    parser.add_argument('--artifact-type', help='Identifies the type of artifact used to deploy your application. Currently only "gce-vm-image", "docker", and "singularity" are supported.', type=str, default='singularity')
    parser.add_argument('--docker-image', help='The name of the docker image. Only used if --artifact-type=docker', type=str)
    parser.add_argument('--singularity-image', help='The name of the singularity image. Only used if --artifact-type=singularity', type=str)
    parser.add_argument('--image', help='GCE VM image selfLink to use or deploying the GCE cluster.', type=str, default='projects/hpc-apps/global/images/family/fluid-cicb-gcp-foss-latest')
    parser.add_argument('--project', help='Google Cloud project ID to deploy the GCE cluster to', type=str)
    parser.add_argument('--zone', help='Google Cloud zone to deploy the GCE cluster to', type=str, default="us-west1-b")
    parser.add_argument('--slurm-controller', help='The name of a slurm controller to schedule CI tasks as jobs on', type=str)

    return parser.parse_args()

def main():

    args = parseCli()

    createSettingsJson(args)
    
    concretizeTfvars()
    
    createSSHKey()

    provisionCluster()
#    
#    uploadWorkspace()

    runExeCommands()
    
#    downloadWorkspace()
#    
    deprovisionCluster()

#    checkExitCodes()

#END main

if __name__=='__main__':
    main()
