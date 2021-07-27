#!/usr/bin/python3

import json
import os
import subprocess
import shutil
import shlex
from datetime import datetime
import sys

WORKSPACE='/workspace/'


#def createSettingsJson()
#
##END
#
#def concretizeTfvars():
#
##END
#
#def provisionCluster():
#
##END
#
#def uploadWorkspace():
#
##END

def runExeCommands():

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


#END runExeCommands

#def downloadWorkspace():
#
##END
#
#def deprovisionCluster():
#
##END

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

def main():

#    args = parseCli()
#
#    createSettingsJson()
#    
#    concretizeTfvars()
#    
#    provisionCluster()
#    
#    uploadWorkspace()

    runExeCommands()
    
#    downloadWorkspace()
#    
#    deprovisionCluster()

    checkExitCodes()

#END main

if __name__=='__main__':
    main()
