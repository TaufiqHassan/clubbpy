## Function to execute shell commands
from subprocess import Popen, PIPE, STDOUT, DEVNULL
from pathlib import Path
import os
import logging
import shlex

def exec_shell(cmd,inp='',hide=False):
    logger = logging.getLogger('log.clubb')
    cmd_split = shlex.split(cmd)
    logger.info('\n[cmd]: ' + cmd+ '\n')
    
    if hide:
        p = Popen(cmd_split, stdout=PIPE, stdin=DEVNULL, stderr=STDOUT, universal_newlines=True)
        op, _ =p.communicate()
    else:
        p = Popen(cmd_split, stdout=PIPE, stdin=PIPE, stderr=STDOUT, universal_newlines=True)
        p.stdin.write(inp)
        op, _ =p.communicate()
        items = op.split('\n')
        for line in items:
            logger.info(line)
    return p.returncode

def assert_len(all_vars):
    max_length = max(map(len, all_vars))
    for var in all_vars:
        if len(var) < max_length:
            var.extend(var * (max_length - len(var)))
    return all_vars

def manage_clubb_dirs(path,casename):
    ## CLUBB directories for compilation
    if path == None:
        clubb_dir = Path(os.path.expandvars("$CLUBBHOME"))
    else:
        clubb_dir = Path(path)

    clubb_compile = clubb_dir / 'compile'
    clubb_config = clubb_compile / 'config'

    ## CLUBB directories for model run
    clubb_cases = clubb_dir / 'input' / 'case_setups'
    tunable_dir = clubb_dir / 'input' / 'tunable_parameters'
    case_file = clubb_cases / str(casename+'_model.in')
    clubb_scripts = clubb_dir / 'run_scripts'

    ## Update the run script
    with open(clubb_scripts / 'run_scm.bash','r') as file:
        filedata = file.read()
        filedata = filedata.replace('../',str(clubb_dir)+'/')
        filedata = filedata.replace('/input/','/paescal_exp/')
        filedata = filedata.replace('/tunable_parameters/','/{EXPNAME}/casefiles/')
        filedata = filedata.replace('/stats/','/{EXPNAME}/casefiles/')
        filedata = filedata.replace('/case_setups/','/{EXPNAME}/casefiles/')
        filedata = filedata.replace('/output/','/paescal_exp/{EXPNAME}/output/')
    with open(clubb_scripts / 'run_scm_paescal.bash','w') as file:
        file.write(filedata)
    exec_shell(f'chmod 777 {str(clubb_scripts)}/run_scm_paescal.bash')
    return clubb_dir, clubb_config, clubb_compile, case_file, clubb_cases, clubb_scripts, tunable_dir

def get_caseNoutPath(path,expname):
    if path == None:
        clubb_dir = Path(os.path.expandvars("$CLUBBHOME"))
    else:
        clubb_dir = Path(path)
    
    casefiles_path = clubb_dir / 'paescal_exp' / expname / 'casefiles'
    output_path = clubb_dir / 'paescal_exp' / expname / 'output'
    
    if not os.path.exists(casefiles_path):
        logging.info("\n"+str(casefiles_path)+" doesn't exist. Creating one...\n")
        os.makedirs(str(casefiles_path))
    
    if not os.path.exists(output_path):
        logging.info("\n"+str(output_path)+" doesn't exist. Creating one...\n")
        os.makedirs(str(output_path))
    
    return casefiles_path, output_path
