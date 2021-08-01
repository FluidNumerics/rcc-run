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

WORKSPACE='/workspace/'


def main():

    with open(WORKSPACE+'settings.json','r')as f: 
        settings = json.load(f)

    with open(WORKSPACE+settings['ci_file'],'r')as f: 
        tests = json.load(f)

    utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

    k=0
    for test in tests['tests'] :

        workdir=WORKSPACE+test['output_directory']
        print('Making directory {}\n'.format(workdir))
        try:
            os.makedirs(workdir)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
            pass

        os.chdir(workdir)

        if settings['artifact_type'] == 'singularity':
            if settings['mpi'] :
  
                cmd = 'mpirun -np {NPROC} {AFFINITY} singularity --bind /workspace:/workspace exec {IMAGE} {CMD}'.format(NPROC=settings['nproc'],
                        AFFINITY=settings['task_affinity'],
                        IMAGE=settings['singularity_image'],

                        CMD=test['execution_command'])

            else:
  
                if int(settings['gpu_count']) > 0:
                    cmd = 'singularity --nv --bind /workspace:/workspace exec {IMAGE} {CMD}'.format(IMAGE=settings['singularity_image'],CMD=test['execution_command'])
                else:
                    cmd = 'singularity exec --bind /workspace:/workspace {IMAGE} {CMD}'.format(IMAGE=settings['singularity_image'],CMD=test['execution_command'])

       
        else:
            cmd = test['execution_command']


        print('Running {}\n'.format(cmd))
        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        print(stdout.decode("utf-8"))
        print(stderr.decode("utf-8"))
        tests['tests'][k]['stdout'] = stdout.decode("utf-8")
        tests['tests'][k]['stderr'] = stderr.decode("utf-8")
        tests['tests'][k]['exit_code'] = proc.returncode
        tests['tests'][k]['build_id'] = settings['build_id']
        tests['tests'][k]['machine_type'] = settings['machine_type']
        tests['tests'][k]['node_count'] =int(settings['node_count'])
        tests['tests'][k]['gpu_type'] = settings['gpu_type']
        tests['tests'][k]['gpu_count'] =int(settings['gpu_count'])
        tests['tests'][k]['git_sha'] = settings['git_sha']
        tests['tests'][k]['datetime'] = utc

        k+=1
                                        
    # Change working directory back to /workspace
    os.chdir(WORKSPACE)

    with open(WORKSPACE+'/results.json','w')as f:          
        for res in tests['tests']:
            f.write(json.dumps(res))
            f.write('\n')

#END main

if __name__=='__main__':
    main()
