#!/usr/bin/python3

import errno
import argparse
import json
import os
import subprocess
import shutil
import shlex
from datetime import datetime
import sys
import time
import yaml
import urllib.request


STDOUT_LIMIT=1000
DEFAULT_RETURN_CODE=999
SLEEP_INTERVAL=5

def get_instance_metadata(key):
    """Gets instance metadata given a metadata key"""

    GOOGLE_URL = "http://metadata.google.internal/computeMetadata/v1/instance/attributes"
    req = urllib.request.Request("{}/{}".format(GOOGLE_URL, key))
    req.add_header('Metadata-Flavor', 'Google')
    resp = urllib.request.urlopen(req)

    value = resp.read().decode('utf-8').replace('\t','')
    return value

#END get_instance_metadata

def get_partition(name='default'):
    """Gets the compute partition metadata given the partition name"""

    config = json.loads(get_instance_metadata('config'))
    partitions = config['partitions']
    partition = {}
    if name == 'default':
        partition = partitions[0]
    else:
        for p in partitions:
            if p['name'] == name :
                partition = p
                break
    return partition

#END get_partition

def run(cmd):
    """Runs a command in the local environment and returns exit code, stdout, and stderr"""

    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    stdout, stderr = proc.communicate()

    return stdout, stderr, proc.returncode

#END run

def rccClusterRun(settings,tests):
    """Executes command_groups sequentially on a RCC cluster"""

    WORKSPACE=settings['workspace']
    sbatch = '/usr/local/bin/sbatch '
    squeue = '/usr/local/bin/squeue '
    sacct = '/usr/local/bin/sacct '

    utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
   
    command_groups = {}
    k=0
    nSubmitFailures = 0
    for test in tests['tests'] :

        workdir=WORKSPACE+test['output_directory']
        # Set the WORKSPACE environment variable so that users can reference this
        # in test scripts as the top of their directory tree.
        os.environ["WORKSPACE"] = workdir

        print('Making directory {}\n'.format(workdir),flush=True)
        try:
            os.makedirs(workdir)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
            pass

        os.chdir(workdir)

        cmd = sbatch

        # Create job dependency for job submissions
        if test['command_group'] in command_groups.keys():
            if not settings['ignore_job_dependencies']:
                dependent_job = command_groups[test['command_group']][-1]['job_id']
                cmd += '--dependency=afterany:{} '.format(str(dependent_job))

        # Add partition flag to job submission
        if 'partition' in test.keys():
            print('Submitting {} to partition {}'.format(test['execution_command'],test['partition']),flush=True)
            cmd += '--partition={} '.format(test['partition'])
            # Get the partition metadata
            partition = get_partition(test['partition'])
        else:
            print('Submitting {} to default partition'.format(test['execution_command']),flush=True)
            partition = get_partition("default")

        # Add batch options
        if 'batch_options' in test.keys():
            if test['batch_options']:
                cmd += '{} '.format(test['batch_options'])

        if int(settings['gpu_count']) > 0:
            cmd += '--gres=gpu:{} '.format(settings['gpu_count'])

        # Add stdout/stderr for later parsing
        cmd += '-o {}/{}/stdout '.format(WORKSPACE,test['output_directory'])
        cmd += '-e {}/{}/stderr '.format(WORKSPACE,test['output_directory'])

        # Add batch file to command
        cmd += WORKSPACE+test['execution_command']

        print(cmd,flush=True)

        # Submit the job
        stdout, stderr, returncode = run(cmd)

        # Log information
        tests['tests'][k]['stdout'] = ''
        tests['tests'][k]['stderr'] = ''
        tests['tests'][k]['exit_code'] = DEFAULT_RETURN_CODE
        tests['tests'][k]['build_id'] = settings['build_id']
        tests['tests'][k]['git_sha'] = settings['git_sha']
        tests['tests'][k]['datetime'] = utc
        tests['tests'][k]['node_count'] =int(settings['node_count'])
        tests['tests'][k]['machine_type'] = partition['machine_type']
        tests['tests'][k]['gpu_type'] = partition['gpu_type']
        tests['tests'][k]['gpu_count'] =int(partition['gpu_count'])
        tests['tests'][k]['gvnic'] =partition['gvnic']
        tests['tests'][k]['compact_placement'] = partition['enable_placement']
        tests['tests'][k]['compiler'] = settings['compiler']
        tests['tests'][k]['target_arch'] = settings['target_arch']
        tests['tests'][k]['vm_image'] = settings['gce_image']

        # Check return code
        if returncode == 0:
            # Get the job id
            jobid = int(stdout.decode('utf-8').split(' ')[-1])
            # Record the job id in the command_group
            if test['command_group'] in command_groups.keys():
                command_groups[test['command_group']].append({'job_id':jobid,'index':k,'complete':False})
            else:
                command_groups[test['command_group']] = [{'job_id':jobid,'index':k,'complete':False}]
        else:
            print(stderr.decode('utf-8'),flush=True)
            #tests['tests'][k]['stdout'] = 'sbatch stdout : '+stdout.decode("utf-8")[:STDOUT_LIMIT]
            tests['tests'][k]['stderr'] = 'sbatch stderr : '+stderr.decode("utf-8")
            tests['tests'][k]['exit_code'] = returncode

            # Record the failure in the command_group
            if test['command_group'] in command_groups.keys():
                command_groups[test['command_group']].append({'job_id':-1,'index':k,'complete':True})
            else:
                command_groups[test['command_group']] = [{'job_id':-1,'index':k,'complete':True}]

            # Increment the submission failue
            nSubmitFailures += 1

        k+=1
        time.sleep(0.5)


    # Number of jobs thar were successfully submitted
    njobs = k - nSubmitFailures

    # Initialize a counter for the number of complete jobs
    ncomplete = 0

    # Monitor Jobs
    while True:

        if ncomplete == njobs:
            break

        print('Jobs status : {}/{}'.format(str(ncomplete),str(njobs),flush=True))
        for cg in command_groups.keys():
            k=0
            for test in command_groups[cg]:
                if not test['complete']:
                    jobid = test['job_id']
                    index = test['index']
                    cmd = 'sacct -j {} --format=state%10'.format(str(jobid))
                    stdout, stderr, returncode = run(cmd)
                    status = stdout.decode('utf-8').split('\n')[-2].strip()
                    print('Job {} status : {}'.format(str(jobid),status))
                    if status == 'COMPLETED' or status == 'FAILED' or status == 'CANCELLED':
                        ncomplete += 1
                        command_groups[cg][k]['complete'] = True

                        # Log stdout and stderr
                        with open('{}/{}/stdout'.format(WORKSPACE,tests['tests'][index]['output_directory']),'r') as f:
                            stdout = f.read()

                        with open('{}/{}/stderr'.format(WORKSPACE,tests['tests'][index]['output_directory']),'r') as f:
                            stderr = f.read()

#                        tests['tests'][index]['stdout'] = stdout
                        tests['tests'][index]['stderr'] = stderr

                        # Get return code from sacct
                        cmd = 'sacct -j {} --format=exitCode%10'.format(str(jobid))
                        stdout, stderr, returncode = run(cmd)
                        returncode = stdout.decode('utf-8').split('\n')[2].strip().split(':')[0]
                        tests['tests'][index]['exit_code'] = int(returncode)

                        # Get the number of nodes
                        cmd = 'sacct -j {} --format=NNodes'.format(str(jobid))
                        stdout, stderr, returncode = run(cmd)
                        nnodes = stdout.decode('utf-8').split('\n')[2].strip()
                        tests['tests'][index]['node_count'] = int(nnodes)

                        # Get the elapsed time in seconds
                        cmd = 'sacct -j {} --format=ElapsedRaw'.format(str(jobid))
                        stdout, stderr, returncode = run(cmd)
                        runtime = stdout.decode('utf-8').split('\n')[2].strip()
                        tests['tests'][index]['runtime'] = float(runtime)

                        # Get the number of CPUs used
                        cmd = 'sacct -j {} --format=AllocCPUs'.format(str(jobid))
                        stdout, stderr, returncode = run(cmd)
                        alloc_cpus = stdout.decode('utf-8').split('\n')[2].strip()
                        tests['tests'][index]['allocated_cpus'] = int(alloc_cpus)

                        # Get the max memory used
                        cmd = 'sacct -j {} --format=MaxRSS'.format(str(jobid))
                        stdout, stderr, returncode = run(cmd)
                        maxRss = stdout.decode('utf-8').split('\n')[3].strip()
                        unit = maxRss[-1]
                        if unit == 'K':
                            max_memory = float(maxRss[:-1])/1024.0/1024.0
                        elif unit == 'M':
                            max_memory = float(maxRss[:-1])/1024.0
                        elif unit == 'G' :
                            max_memory = float(maxRss[:-1])

                        tests['tests'][index]['max_memory_gb'] = float(max_memory)

                k+=1

        time.sleep(SLEEP_INTERVAL)

        
    # Change working directory back to /workspace
    os.chdir(WORKSPACE)
    with open(WORKSPACE+'/results.json','w')as f:          
        f.write(json.dumps(tests))


#END rccClusterRun

def parseCli():

    parser = argparse.ArgumentParser(description='Manage execution of CICB workflows using fluid-cicb settings and workspace')
    parser.add_argument('workspace', help='Path to workspace directory for carrying out fluid-cicb workflow', type=str)

    return parser.parse_args()

#END parseCli

def loadTests(WORKSPACE,settings):

    ext = settings['ci_file'].split('.')[-1]

    if ext == 'json':

        try:
            with open(WORKSPACE+settings['ci_file'],'r')as f: 
                tests = json.load(f)
        except:
            print('Error opening CI file {}'.format(settings['ci_file']))
            sys.exit(-1)

    elif ext == 'yaml':

        try:
            with open(WORKSPACE+settings['ci_file'],'r')as f: 
                tests = yaml.load(f, Loader=yaml.FullLoader)
        except:
            print('Error opening CI file {}'.format(settings['ci_file']))
            sys.exit(-1)
    else:
        print('Undefined extension : {}'.format(ext))
        sys.exit(-1)

    return tests

#END loadTests

def setEnvironmentVars(settings):
    """Sets environment variables that can be used during job execution.
       CAUTION : The WORKSPACE environment variable will be overriden in 
       the rccClusterWorkflow
    """
    os.environ["WORKSPACE"] = settings['workspace']
    os.environ["PROJECT"] = settings['project']
    os.environ["GIT_SHA"] = settings['git_sha']

    if settings['docker_image']:
        os.environ["DOCKER_IMAGE"] = settings['docker_image']

    if settings['singularity_image']:
        os.environ['SINGULARITY_IMAGE'] = '{}/{}'.format(settings['workspace'],str(settings['singularity_image']))

    if settings['env_file']:
        os.environ['ENV_FILE'] = '{}/{}'.format(settings['workspace'],str(settings['env_file']))

    os.environ["GCE_IMAGE"] = settings['gce_image']

#END setEnvironmentVars

def main():

    args = parseCli()

    if os.path.isdir(args.workspace):
        print('Found settings in {}'.format(args.workspace),flush=True)
        WORKSPACE = args.workspace
    else:
        print('Workspace on cluster not found. Quitting',flush=True)
        sys.exit(1)

    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)

    setEnvironmentVars(settings)

    tests = loadTests(WORKSPACE,settings)

    rccClusterRun(settings,tests)


#END main

if __name__=='__main__':
    main()
