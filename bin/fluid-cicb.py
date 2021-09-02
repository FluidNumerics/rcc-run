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
import hcl

WORKSPACE='/workspace/'
TFPATH='/opt/fluid-cicb/tf/'
SLEEP_INTERVAL=5
SSH_TIMEOUT=300
N_RETRIES=SSH_TIMEOUT/SLEEP_INTERVAL


def waitForSSH():
    """Repeatedly checks for SSH connection"""

    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)

    hostname = settings['hostname']
    zone = settings['zone']
    project = settings['project']

    command = ['gcloud',
               'compute',
               'ssh',
               hostname,
               '--command="hostname"',
               '--zone={}'.format(zone),
               '--project={}'.format(project),
               '--ssh-key-file=/workspace/sshkey']

    k = 1
    rc = 1
    while True:

        if k > N_RETRIES:
            if settings['cluster_type'] == 'gce':
                deprovisionCluster()

            elif settings['cluster_type'] == 'rcc-ephemeral':
                deprovisionCluster()

            writePassFail(rc)
            if settings['surface_nonzero_exit_code']:
                sys.exit(rc)

        print('Waiting for ssh connection...',flush=True)
        proc = subprocess.Popen(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        stdout, stderr = proc.communicate()
        if proc.returncode == 0:
            print('SSH connection successful!',flush=True)
            rc = 0
            break
        else:
            time.sleep(SLEEP_INTERVAL)
            k+=1

    return rc

#END waitForSSH

def clusterRun(cmd,streamOutput=False):
    """Runs a command over ssh on the head node for the cluster"""

    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)

    hostname = settings['hostname']
    zone = settings['zone']
    project = settings['project']

    command = 'gcloud'
    command += ' compute'
    command += ' ssh '
    command += hostname
    command += ' --command="{}"'.format(cmd)
    command += ' --zone={}'.format(zone)
    command += ' --project={}'.format(project)
    command += ' --ssh-key-file=/workspace/sshkey'

    proc = subprocess.Popen(command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    if streamOutput:
        # Poll process.stdout to show stdout live
        while True:
            output = proc.stdout.readline()
            if proc.poll() is not None:
                break
            if output:
                print(output.strip())
#                time.sleep(1)

            checkReturnCode(proc.returncode,proc.stderr)

    else:
        stdout, stderr = proc.communicate()
        try:
            print(stdout.decode('utf-8').rstrip(),flush=True)
        except:
            print(stdout,flush=True)

        checkReturnCode(proc.returncode,stderr)

        return proc.returncode

#END clusterRun

def localRun(cmd):
    """Runs a command in the local environment and returns exit code, stdout, and stderr"""

    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)

    proc = subprocess.Popen(shlex.split(cmd),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    stdout, stderr = proc.communicate()
    try:
        print(stdout.decode('utf-8').rstrip(),flush=True)
    except:
        print(stdout,flush=True)

    checkReturnCode(proc.returncode,stderr)

    return proc.returncode

#END localRun

def checkReturnCode(returncode,stderr):
    """Checks the return code. If return code is nonzero, stderr is printed to screen and code is halted with nonzero exit code"""

    if returncode != 0:
        print(stderr,flush=True)
        sys.exit(1)

#END checkReturnCode

def createSettingsJson(args):
    """Converts the args namespace to a json dictionary for use in the Cloud Build environment and on the cluster"""

    print(args,flush=True)
    settings = {'artifact_type':args.artifact_type,
                'build_id':args.build_id,
                'docker_image':args.docker_image,
                'compiler':args.compiler,
                'cluster_type':args.cluster_type,
                'target_arch':args.target_arch,
                'git_sha':args.git_sha,
                'gpu_count':args.gpu_count,
                'gpu_type':args.gpu_type,
                'image':args.image,
                'ignore_job_dependencies':args.ignore_job_dependencies,
                'machine_type':args.machine_type,
                'mpi':args.mpi,
                'node_count':args.node_count,
                'nproc':args.nproc,
                'profile':args.profile,
                'project':args.project,
                'rcc_tfvars':args.rcc_tfvars,
                'rcc_ephemeral':args.rcc_ephemeral,
                'service_account':args.service_account,
                'singularity_image':args.singularity_image,
                'rcc_controller':args.rcc_controller,
                'surface_nonzero_exit_code':args.surface_nonzero_exit_code,
                'task_affinity':args.task_affinity,
                'vpc_subnet':args.vpc_subnet,
                'workspace':'/apps/workspace/{}/'.format(args.build_id[0:7]),
                'zone':args.zone,
                'ci_file':args.ci_file,
                'bq_table':'{}:fluid_cicb.app_runs'.format(args.project),
                'hostname':'fcicb-{}-0'.format(args.build_id[0:7])}

    if args.cluster_type == 'rcc-ephemeral':
        settings['hostname'] = 'fcicb-{}-controller'.format(args.build_id[0:7])
    elif args.cluster_type == 'rcc-static':
        settings['hostname'] = args.rcc_controller

    with open(WORKSPACE+'settings.json','w')as f: 
        f.write(json.dumps(settings))

#END createSettingsJson

def concretizeTfvars():

    print('Concretizing tfvars',flush=True)
    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)
    
    clusterType = settings['cluster_type']

    if clusterType == 'gce':

        with open(TFPATH+clusterType+'/fluid.tfvars.tmpl', 'r') as f:
            tfvars = f.read()

    elif clusterType == 'rcc-ephemeral' :

        rccFile = settings['rcc_file']
        with open(rccFile, 'r') as f:
            tfvars = f.read()

        tfvars = tfvars.replace('<name>','fcicb-{}'.format(settings['build_id'][0:7]))

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

    print(tfvars,flush=True)

    with open(TFPATH+clusterType+'/fluid.auto.tfvars', 'w') as f:
        f.write(tfvars)

#END concretizeTfvars

def provisionCluster():
    """Use Terraform and the provided module to create a GCE cluster to execute work on"""

    print('Provisioning Cluster',flush=True)
    os.chdir(TFPATH)
    localRun('terraform init')
    localRun('terraform apply --auto-approve')
    print('Done provisioning cluster',flush=True)

#END provisionCluster

def createSSHKey():
    """Create an ssh key that can be used to connect with the cluster"""

    localRun('ssh-keygen -b 2048 -t rsa -f /workspace/sshkey -q -N ""')

#END createSSHKey

def uploadDirectory(localdir,remotedir):
    """Recursively copies the local:{localdir} to cluster:{remotedir}"""

    print('Transferring local workspace to cluster...',flush=True)
    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)

    hostname = settings['hostname']
    zone = settings['zone']

    command = 'gcloud '
    command += 'compute '
    command += 'scp '
    command += '--recurse '
    command += '{}/* '.format(localdir)
    command += '{}:{}/ '.format(hostname,remotedir)
    command += '--zone={} '.format(zone)
    command += '--ssh-key-file=/workspace/sshkey '

    proc = subprocess.Popen(command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    stdout, stderr = proc.communicate()
    checkReturnCode(proc.returncode,stderr)

    print('Done transferring local workspace to cluster ',flush=True)
    return proc.returncode

#END uploadDirectory

def runExeCommands():
    """Runs the ciRun.py application on the remote cluster"""

    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)

    print('Running CI tests...',flush=True)
    clusterRun('python3 /tmp/bin/ciRun.py {}'.format(settings['workspace']))
    print('Done running CI tests.',flush=True)

#END runExeCommands

def downloadDirectory(localdir,remotedir):
    """Recursively copies the cluster:{remotedir} to local:{localdir}"""

    print('Transferring cluster workspace to local workspace...',flush=True)

    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)

    hostname = settings['hostname']
    zone = settings['zone']

    command = 'gcloud '
    command += 'compute '
    command += 'scp '
    command += '--recurse '
    command += '{}:{}/* '.format(hostname,remotedir)
    command += '{}/ '.format(localdir)
    command += '--zone={} '.format(zone)
    command += '--ssh-key-file=/workspace/sshkey '

    proc = subprocess.Popen(command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    stdout, stderr = proc.communicate()

    checkReturnCode(proc.returncode,stderr)

    print('Done transferring cluster workspace to local workspace...',flush=True)

    return proc.returncode

#END downloadDirectory

def deprovisionCluster():
    """Use Terraform and the provided module to delete the existing cluster"""

    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)
 
    clusterType = settings['cluster_type']
    print('Deprovisioning cluster...',flush=True)
    os.chdir(TFPATH+clusterType)
    localRun('terraform destroy --auto-approve')
    print('Done deprovisioning cluster',flush=True)

#END deprovisionCluster

def checkExitCodes():
    """Parses the results.json output and reports exit code statistics"""

    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)

    with open(WORKSPACE+'results.json','r')as f:          
        tests = json.load(f)

    results = {}
    sysExitCode = 0
    for test in tests['tests'] :
        cli_command = test['command_group']
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

    print('============================',flush=True)
    print('',flush=True)
    print('Exit Code Check',flush=True)
    print('')
    for cli in results.keys():
      npass = results[cli]['npass']
      nfail = results[cli]['nfail']
      print('============================',flush=True)
      print('                        ',flush=True)
      print('  {}'.format(cli),flush=True)
      print('  > PASS : {}/{}'.format(str(npass),str(npass+nfail)),flush=True)
      print('  > FAIL : {}/{}'.format(str(nfail),str(npass+nfail)),flush=True)
      print('  > PASS RATE : {}%'.format(str(npass/(npass+nfail)*100)),flush=True)
      print('                        ',flush=True)

    print('============================',flush=True)

    if settings['surface_nonzero_exit_code']:
        if sysExitCode != 0:
            sys.exit(sysExitCode) 
    else:
        writePassFail(sysExitCode)

#END checkExitCodes

def appendSystemInfo(test):
    """Appends additional system information included in the rcc-tfvars file, if provided"""

    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)

    res = test

    if settings['rcc_tfvars']:
        with open(settings['rcc_tfvars'],'r')as f:
            rcc = hcl.load(f)

        # Filestore
        if 'create_filestore' in rcc.keys():
            res['filestore'] = rcc['create_filestore']
            if res['filestore']:
                res['filestore_tier'] = rcc['filestore']['tier']
                res['filestore_capacity_gb'] = rcc['filestore']['capacity_gb']

        # Lustre
        if 'create_lustre' in rcc.keys():
            res['lustre'] = rcc['create_lustre']
            if res['lustre']:
                res['lustre_image'] = rcc['lustre']['image']
                res['lustre_mds_node_count'] = rcc['lustre']['mds_node_count']
                res['lustre_mds_machine_type'] = rcc['lustre']['mds_machine_type']
                res['lustre_mds_boot_disk_type'] = rcc['lustre']['mds_boot_disk_type']
                res['lustre_mds_boot_disk_size_gb'] = rcc['lustre']['mds_boot_disk_size_gb']
                res['lustre_mdt_disk_type'] = rcc['lustre']['mdt_disk_type']
                res['lustre_mdt_disk_size_gb'] = rcc['lustre']['mdt_disk_size_gb']
                res['lustre_mdt_per_mds'] = rcc['lustre']['mdt_per_mds']
                res['lustre_oss_node_count'] = rcc['lustre']['oss_node_count']
                res['lustre_oss_machine_type'] = rcc['lustre']['oss_machine_type']
                res['lustre_oss_boot_disk_type'] = rcc['lustre']['oss_boot_disk_type']
                res['lustre_oss_boot_disk_size_gb'] = rcc['lustre']['oss_boot_disk_size_gb']
                res['lustre_ost_disk_type'] = rcc['lustre']['ost_disk_type']
                res['lustre_ost_disk_size_gb'] = rcc['lustre']['ost_disk_size_gb']
                res['lustre_ost_per_oss'] = rcc['lustre']['ost_per_oss']

    return res

#END appendSystemInfo

def formatResults():
    """Formats the results.json to Newline Delimited JSON for loading into big query"""

    with open(WORKSPACE+'results.json','r')as f:          
        tests = json.load(f)

    with open(WORKSPACE+'bq-results.json','w')as f:          
        for test in tests['tests'] :
            del test['output_directory']
            
            # Append additional system information from HCL file if provided
            res = appendSystemInfo(test)

            f.write(json.dumps(res))
            print(json.dumps(res),flush=True)
            f.write('\n')
        
#END formatResults

def publishToBQ(): 
    """Publish bq-results.json to Big Query dataset if provided"""

    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)

    if settings['bq_table']:
        print('Publishing results to Big Query Table',flush=True)
        localRun('bq load --source_format=NEWLINE_DELIMITED_JSON {} {}bq-results.json'.format(settings['bq_table'],WORKSPACE))

#END publishToBQ

def parseCli():
    parser = argparse.ArgumentParser(description='Provision remote resources and test HPC/RC applications')
    parser.add_argument('--build-id', help='Cloud Build build ID', type=str)
    parser.add_argument('--cluster-type', help='Type of cluster to use for testing. Either "rcc-static", "rcc-ephemeral", or "gce".', type=str, default='gce')
    parser.add_argument('--git-sha', help='Git sha for your application', type=str)
    parser.add_argument('--node-count', help='Number of nodes to provision for testing', type=int, default=1)
    parser.add_argument('--machine-type', help='GCE Machine type for each node', type=str, default='n1-standard-2')
    parser.add_argument('--compiler', help='The compiler used to build the application (optional)', type=str, default='')
    parser.add_argument('--target-arch', help='The architecture targeted by the application build (optional)', type=str, default='')
    parser.add_argument('--gpu-count', help='The number of GPUs per node', type=int, default=0)
    parser.add_argument('--gpu-type', help='The type of GPU to attach to each compute node', type=str, default='')
    parser.add_argument('--nproc', help='The number of processes to launch (MPI)', type=int, default=1)
    parser.add_argument('--task-affinity', help='Task affinity flags to send to MPI.', type=str)
    parser.add_argument('--mpi', help='Boolean flag to indicate whether or not MPI is used',default=False, action='store_true')
    parser.add_argument('--profile', help='Boolean flag to enable (true) or disable (false) profiling with the hpc toolkit', default=False, action='store_true')
    parser.add_argument('--surface-nonzero-exit-code', help='Boolean flag to surface a nonzero exit code (true) if any of the tests fail', default=False, action='store_true')
    parser.add_argument('--vpc-subnet', help='Link to VPC Subnet to use for deployment. If not provided, an ephemeral subnet is created', type=str, default='')
    parser.add_argument('--service-account', help='Service account email address to attach to GCE instance. If not provided, an ephemeral service account is created', type=str, default='')
    parser.add_argument('--artifact-type', help='Identifies the type of artifact used to deploy your application. Currently only "gce-vm-image", "docker", and "singularity" are supported.', type=str, default='singularity')
    parser.add_argument('--docker-image', help='The name of the docker image. Only used if --artifact-type=docker', type=str)
    parser.add_argument('--singularity-image', help='The name of the singularity image. Only used if --artifact-type=singularity', type=str)
    parser.add_argument('--image', help='GCE VM image selfLink to use or deploying the GCE cluster.', type=str, default='')
    parser.add_argument('--project', help='Google Cloud project ID to deploy the cluster to', type=str)
    parser.add_argument('--zone', help='Google Cloud zone to deploy the cluster to', type=str, default="us-west1-b")
    parser.add_argument('--rcc-controller', help='The name of a slurm controller to schedule CI tasks as jobs on. Only used if cluster-type=rcc-static', type=str)
    parser.add_argument('--ci-file', help='Path to tests file in your repository', type=str, default="./fluidci.json")
    parser.add_argument('--rcc-tfvars', help='Path to research computing cluster tfvars file', type=str, default="./fluid.auto.tfvars")
    parser.add_argument('--ignore-job-dependencies', help='Boolean flag to enable ignorance of job dependencies assumed within a command_group.', default=False, action='store_true')

    return parser.parse_args()

#END parseCli

def writePassFail(exitCode):

    with open(WORKSPACE+'pass-fail.result','w')as f:          
        f.write(str(exitCode))

#END writePassFail

def gceClusterWorkflow():

    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)

    workspace = settings['workspace']

    concretizeTfvars()
    
    createSSHKey()

    provisionCluster()

    rc = waitForSSH()

    if rc == 0:

        clusterRun('mkdir -p {}'.format(workspace))

        uploadDirectory(localdir='/workspace',remotedir='{}/'.format(workspace))

        runExeCommands()

        downloadDirectory(localdir='/workspace',remotedir='{}'.format(workspace))

        deprovisionCluster()

        formatResults()

        publishToBQ()

        checkExitCodes()

#END gceClusterWorkflow

def slurmgcpWorkflow():

    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)

    if settings['rcc_ephemeral']:
        concretizeTfvars()

        provisionCluster()

    createSSHKey()

    rc = waitForSSH()

    workspace = settings['workspace']

    createSSHKey()

    rc = waitForSSH()

    if rc == 0:

        uploadDirectory(localdir='/opt/fluid-cicb',remotedir='/tmp')

        clusterRun('mkdir -p {}'.format(workspace))

        uploadDirectory(localdir='/workspace',remotedir='{}/'.format(workspace))

        runExeCommands()

        downloadDirectory(localdir='/workspace',remotedir='{}'.format(workspace))

        time.sleep(5)

        if settings['rcc_ephemeral']:
            deprovisionCluster()
        else:
            clusterRun('rm -rf {}'.format(workspace))

        formatResults()

        publishToBQ()

        checkExitCodes()

#END slurmgcpWorkflow

def main():

    args = parseCli()

    createSettingsJson(args)

    if args.cluster_type == 'gce':
        gceClusterWorkflow()
    else:
        slurmgcpWorkflow()

#END main

if __name__=='__main__':
    main()
