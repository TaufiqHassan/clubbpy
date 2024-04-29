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
        filedata = filedata.replace('_model.in','_model.in.template')
        filedata = filedata.replace('configurable_model_flags.in','configurable_model_flags.in.template')
        filedata = filedata.replace('tunable_parameters.in','tunable_parameters.in.template')
        filedata = filedata.replace('standard_stats.in.in','standard_stats.in.in.template')
    with open(clubb_scripts / 'run_scm_paescal.bash','w') as file:
            file.write(filedata)
    exec_shell(f'chmod 777 {str(clubb_scripts)}/run_scm_paescal.bash')
    return clubb_dir, clubb_config, clubb_compile, case_file, clubb_cases, clubb_scripts, tunable_dir
