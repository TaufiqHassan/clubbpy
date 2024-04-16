from pathlib import Path
import logging
import time

from clubbUtil import exec_shell

def compile_clubb_standalone(clubb_dir,clubb_config,clubb_compile):
    ## Find current default GNU NETCDF directory
    p = Path('/opt/cray/pe/netcdf-hdf5parallel/default/gnu').glob('*')
    dirs = [x for x in p if x.is_dir()]
    
    ## Update the NETCDF directory in the config file
    with open(clubb_config / 'linux_x86_64_gfortran_perlmutter.bash','r') as file:
        filedata = file.read()
        filedata = filedata.replace('/opt/cray/pe/netcdf-hdf5parallel/4.9.0.1/gnu/9.1',str(dirs[0]))
    with open(clubb_config / 'linux_x86_64_gfortran_perlmutter_updated.bash','w') as file:
            file.write(filedata)
    
    start = time.perf_counter()
    logging.info('\n################################## Compilation Started ##################################')
    # Executing shell commands to: 
    # (1) clean previous compilation and 
    # (2) re-compile with updated config file
    exec_shell(f'{str(clubb_compile)}/clean_all.bash')
    exec_shell(f'{str(clubb_compile)}/compile.bash -c {str(clubb_config)}/linux_x86_64_gfortran_perlmutter_updated.bash')
    if (clubb_dir / 'bin/clubb_standalone').is_file():
        logging.info('\nCLUBB standalone successfully compiled.')
    else:
        logging.info('\nCLUBB failed to compile.')
    
    finish = time.perf_counter()
    logging.info(f'\nFinished in {round(finish-start, 2)} second(s)')
    logging.info('\n################################## Compilation Finished ##################################')
