#!/usr/bin/python3

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

    with open(WORKSPACE+'.fluidci.json','r')as f: 
        tests = json.load(f)

    utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

    k=0
    for test in tests :

        workdir=WORKSPACE+test['output_directory']
        print('Making directory {}\n'.format(workdir))
        os.makedirs(workdir)

        os.chdir(workdir)

        if settings['artifact_type'] == 'singularity':
            if settings['mpi'] :
  
                cmd = 'mpirun -np {NPROC} {AFFINITY} singularity exec --bind /workspace:/workspace {IMAGE} {CMD}'.format(NPROC=settings['nproc'],
                        AFFINITY=settings['affinity'],
                        IMAGE=settings['image'],
                        CMD=test['execution_command'])

            else:
  
                if int(settings['gpu_count']) > 0:
                    cmd = 'singularity exec --nv --bind /workspace:/workspace {IMAGE} {CMD}'.format(IMAGE=settings['image'],CMD=test['execution_command'])
                else:
                    cmd = 'singularity exec --bind /workspace:/workspace {IMAGE} {CMD}'.format(IMAGE=settings['image'],CMD=test['execution_command'])

       
        else:
            cmd = test['execution_command']


        print('Running {}\n'.format(cmd))
        proc = subprocess.Popen(shlex.split(cmd),
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        print(stdout.decode("utf-8"))
        print(stderr.decode("utf-8"))
        tests[k]['stdout'] = stdout.decode("utf-8")
        tests[k]['stderr'] = stderr.decode("utf-8")
        tests[k]['exit_code'] = proc.returncode
        tests[k]['build_id'] = settings['build_id']
        tests[k]['machine_type'] = settings['machine_type']
        tests[k]['node_count'] =int(settings['node_count'])
        tests[k]['gpu_type'] = settings['gpu_type']
        tests[k]['gpu_count'] =int(settings['gpu_count'])
        tests[k]['git_sha'] = settings['git_sha']
        tests[k]['datetime'] = utc

        k+=1
                                        
    # Change working directory back to /workspace
    os.chdir(WORKSPACE)

    with open(WORKSPACE+'/results.json','w')as f:          
        for res in tests:
            f.write(json.dumps(res))
            f.write('\n')

#END main

if __name__=='__main__':
    main()
