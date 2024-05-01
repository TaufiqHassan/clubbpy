import time
import argparse
import logging
import shutil
import os

from src.clubbCompile import compile_clubb_standalone
from src.clubbUtil import exec_shell, assert_len, manage_clubb_dirs, get_caseNoutPath

def main():
    
    parser = argparse.ArgumentParser(
            prog="scm_test",
            description="Python scripts to compile and run clubb standalone model",
            formatter_class=argparse.RawTextHelpFormatter
            )
    
    general = parser.add_argument_group("General arguments","Takes single or no input")
    general.add_argument("-c", help="CLUBB Case.\nDefault case: dycoms2_rf01", default='dycoms2_rf01')
    general.add_argument("-d", help="CLUBB model directory.\nDefault directory is defined by $CLUBBHOME", default=None)
    general.add_argument("-compile", "--compile", help="Clean and compile CLUBB first. (No input)", action='store_true', default=None)
    general.add_argument("-plot", "--plot", help="Produce pypaescal plots. (No input)", action='store_true', default=None)
    general.add_argument("-taus", help="Control 'l_diag_Lscale_from_tau' Flag.", default='on')
    general.add_argument("-prog_upwp", help="Control 'l_predict_upwp_vpwp' Flag.", default='on')
    
    param = parser.add_argument_group("Case parameters","Allows multiple inputs")
    param.add_argument("-e", nargs='+', type=str, help="User-defined experiment names.\nBy default names are assigned based on dz/dt etc.", default=[''])
    param.add_argument("-zmax", nargs='+', type=int, help="Number of vertical levels.", default=[132])
    param.add_argument("-grid", nargs='+', type=int, \
                       help="Select grid type:\n1 ==> evenly-spaced grid levels\n2 ==> stretched (unevenly-spaced) grid\nentered on thermodynamic grid levels;\n3 ==> stretched (unevenly-spaced) grid\nentered on momentum grid levels;",\
                       default=[1])
    param.add_argument("-dz", nargs='+', type=int, help="Distance between grid levels on evenly-spaced grid (m).", default=[10])
    param.add_argument("-zbtm", nargs='+', type=float, help="Minimum Altitude of lowest momentum level on any grid (m).", default=[0.0])
    param.add_argument("-ztop", nargs='+', type=float, help="Maximum Altitude of highest momentum level on any grid (m).", default=[5000.0])
    param.add_argument("-ztfname", nargs='+', type=str, help="Path and filename of data file that contains\nthermodynamic level altitudes (in meters).", default=[''])
    param.add_argument("-zmfname", nargs='+', type=str, help="Path and filename of data file that contains\nmomentum level altitudes (in meters).", default=[''])
    param.add_argument("-dt", nargs='+', type=float, help="Model timestep (s)", default=[60.0])
    param.add_argument("-rad_scheme", nargs='+', type=str, help='Radiation scheme.\nThe schemes are: "bugsrad", simplified", "simplified_bomex", or "none".', default=["simplified"])
    param.add_argument("-tinit", nargs='+', type=float, help="Time_initial (s)", default=[21600.0])
    param.add_argument("-tfinal", nargs='+', type=float, help="Time_initial (s)", default=[36000.0])
    param.add_argument("-dtout", nargs='+', type=float, help="Frequency of statistical output (s)", default=[60.0])
    
    conv = parser.add_argument_group("Convergence configuration","Run Convergence tests.")
    conv.add_argument("-ctest", help="Run convergence test.\n3 different groups of settings:\n(1) default,\n(2) baseline,\n(3) revall", default=None)
    conv.add_argument("-ref", nargs='+', type=int, help="use a stretched grid with specified number of refinement.", default=[0])
    
    args = parser.parse_args()

    paramGroup = parser._action_groups[3]._group_actions
    paramGroup = parser._action_groups[3]
    paramLists = [getattr(args,a.dest,None) for a in paramGroup._group_actions]

    ## Making sure that the default lists has the max length
    paramLists = assert_len(paramLists)
    
    ## on/off to true/false
    on_off_switch = {'on':'.true.','off':'.false.'}

    ## CLUBB directories and run script management
    clubb_dir, clubb_config, clubb_compile, \
    case_file, clubb_cases, clubb_scripts, \
    tunable_dir, stat_dir = manage_clubb_dirs(args.d,args.c)

    # Setting up a logfile to track compilation
    clubbpydir = clubb_dir / 'paescal_scripts' / 'clubbpy'
    logging.basicConfig(filename = clubbpydir / 'log.clubb', level=logging.INFO, \
                        format='%(asctime)8s %(message)s',\
                        datefmt='%Y-%m-%d %H:%M:%S')
        
    start = time.perf_counter()
    logging.info('\n################################## Process Started ##################################')
    
    if args.compile:
        compile_clubb_standalone(clubb_dir,clubb_config,clubb_compile)

    if args.ctest != None:
        logging.info('\n==Convergence Tests Starting==')           
        outdirnames = []
        for ref,dt,t0,tf,dtout in zip(args.ref,args.dt,args.tinit,args.tfinal,args.dtout):
            if args.ctest == 'default':
                config_string = f'python {str(clubbpydir)}/src/convergence_config_clubbpy.py \
                               {args.c}  -micro-off -rad-off -splat-off -standard-aterms \
                               -ref {ref} -dt {dt} -ti {t0} -tf {tf} -dto {dtout}'
            elif args.ctest == 'baseline':
                config_string = f'python {str(clubbpydir)}/src/convergence_config_clubbpy.py \
                                {args.c}  -micro-off -rad-off -splat-off -standard-aterms \
                                -new-ic -new-bc -ref {ref} -dt {dt} -ti {t0} -tf {tf} -dto {dtout}'
            elif args.ctest == 'revall':
                config_string = f'python {str(clubbpydir)}/src/convergence_config_clubbpy.py \
                                {args.c}  -micro-off -rad-off -splat-off -standard-aterms \
                                -new-ic -new-bc -new-lim -smooth-tau -lin-diff -new-wp3cl \
                                -ref {ref} -dt {dt} -ti {t0} -tf {tf} -dto {dtout}'
            else:
                logging.info('\nConvergence test settings: default or baseline or revall')
                raise SystemExit
            
            exec_shell(config_string)
            
            outdirname = args.c+'_dt'+str((float(dt)))+'-ref'+str(int(float(ref)))+'-ctest-'+str(args.ctest)
            outdirname = outdirname.replace('.','p')
            casefiles_path, output_path = get_caseNoutPath(args.d,outdirname)
            outdir = clubb_dir / 'paescal_exp' / outdirname / 'output'
            outdirnames.append(outdir)

            exec_shell(f'{str(clubb_scripts)}/run_scm_paescal.bash {args.c} -o {outdir}')

            shutil.move(os.path.join(str(tunable_dir),'configurable_model_flags.in.template'), os.path.join(str(casefiles_path),'configurable_model_flags.in'))
            shutil.move(os.path.join(str(tunable_dir),'tunable_parameters.in.template'), os.path.join(str(casefiles_path),'tunable_parameters.in'))
            shutil.move(os.path.join(str(stat_dir),'standard_stats.in.template'), os.path.join(str(casefiles_path),'standard_stats.in'))
            shutil.move(os.path.join(str(clubb_cases),str(args.c+'_model.in.template')), os.path.join(str(casefiles_path),str(args.c+'_model.in')))
        
        logging.info('\n==Convergence Tests Finished==')
    else:
        # "case" file
        origFile = open(case_file,'r')
        lines = origFile.readlines()
        origFile.close()

        # "parameter" file
        param_file = open(tunable_dir / 'tunable_parameters.in', 'r')
        param_lines = param_file.readlines()
        param_file.close()
        
        # "FLAGS" file
        flags_file = open(tunable_dir / 'configurable_model_flags.in', 'r')
        flag_lines = flags_file.readlines()
        flags_file.close()
        
        # "stats" file
        stats_file = open(stat_dir / 'standard_stats.in', 'r')
        stat_lines = stats_file.readlines()
        stats_file.close()

        for i in range(len(flag_lines)):
            flag_lines[i] = flag_lines[i].rstrip()
            if flag_lines[i].startswith('l_diag_Lscale_from_tau'):
                flag_lines[i] = 'l_diag_Lscale_from_tau = '+on_off_switch[args.taus]+','
            if flag_lines[i].startswith('l_predict_upwp_vpwp'):
                flag_lines[i] = 'l_predict_upwp_vpwp = '+on_off_switch[args.prog_upwp]+','
        
        with open(tunable_dir / 'configurable_model_flags.in.template','w') as file:
            for line in flag_lines:
                file.write(line+"\n")
        
        with open(tunable_dir / 'tunable_parameters.in.template','w') as file:
            for line in param_lines:
                file.write(line+"\n")

        with open(stat_dir / 'standard_stats.in.template','w') as file:
            for line in stat_lines:
                file.write(line+"\n")

        outdirnames = []
        for outdirname,z,g,dz,btm,top,tname,mname,dt,rad,ts,tf,st in zip(*paramLists):
            
            if mname != '':
                with open(mname,'r') as file:
                    filedata = file.read().strip()
                    z = len(filedata.split('\n'))
            if tname != '':
                with open(tname,'r') as file:
                    filedata = file.read().strip()
                    z = len(filedata.split('\n'))
                    
            for i in range(len(lines)):
                lines[i] = lines[i].rstrip()
                if lines[i].startswith('zt_grid_fname'):
                    lines[i] = 'zt_grid_fname = '+ "'"+str(tname)+"'"
                if lines[i].startswith('zm_grid_fname'):
                    lines[i] = 'zm_grid_fname = '+ "'"+str(mname)+"'"
                if lines[i].startswith('nzmax'):
                    lines[i] = 'nzmax = '+ str(z)
                if lines[i].startswith('grid_type'):
                    lines[i] = 'grid_type = '+ str(g)
                if lines[i].startswith('deltaz'):
                    lines[i] = 'deltaz = '+ str(dz)
                if lines[i].startswith('zm_init'):
                    lines[i] = 'zm_init = '+ str(btm)
                if lines[i].startswith('zm_top'):
                    lines[i] = 'zm_top = '+ str(top)
                if lines[i].startswith('dt_main'):
                    lines[i] = 'dt_main = '+ str(dt)
                if lines[i].startswith('dt_rad'):
                    lines[i] = 'dt_rad = '+ str(dt)
                if lines[i].startswith('time_initial'):
                    lines[i] = 'time_initial = '+ str(ts)
                if lines[i].startswith('time_final'):
                    lines[i] = 'time_final = '+ str(tf)
                if lines[i].startswith('stats_tsamp'):
                    lines[i] = 'stats_tsamp = '+ str(st)
                if lines[i].startswith('stats_tout'):
                    lines[i] = 'stats_tout = '+ str(st)
                if lines[i].startswith('rad_scheme'):
                    lines[i] = 'rad_scheme = "'+ str(rad) + '"'
                    if rad == "none":
                        lines[i] = 'rad_scheme = "'+ str(rad) + '"' + '\n' + 'l_calc_thlp2_rad = .false.'
        
            with open(clubb_cases / str(args.c+'_model.in.template'),'w') as file:
                for line in lines:
                    file.write(line+"\n")
                    
            if outdirname == '':
                outdirname = args.c+'_dt'+str(int(float(dt)))+'-zmax'+str(int(float(z)))+'-dz'+str(int(float(dz)))+'-'+str((rad))+'-'+str(int(g))+'-taus'+args.taus+'-prog_upwp'+args.prog_upwp
            casefiles_path, output_path = get_caseNoutPath(args.d,outdirname)
            outdir = clubb_dir / 'paescal_exp' / outdirname / 'output'
            outdirnames.append(outdir)
            
            exec_shell(f'{str(clubb_scripts)}/run_scm_paescal.bash {args.c} -o {outdir}')

            shutil.move(os.path.join(str(tunable_dir),'configurable_model_flags.in.template'), os.path.join(str(casefiles_path),'configurable_model_flags.in'))
            shutil.move(os.path.join(str(tunable_dir),'tunable_parameters.in.template'), os.path.join(str(casefiles_path),'tunable_parameters.in'))
            shutil.move(os.path.join(str(stat_dir),'standard_stats.in.template'), os.path.join(str(casefiles_path),'standard_stats.in'))
            shutil.move(os.path.join(str(clubb_cases),str(args.c+'_model.in.template')), os.path.join(str(casefiles_path),str(args.c+'_model.in')))
    
    if args.plot:
        pypaescal_dir = clubb_dir / 'paescal_scripts' / 'pypaescal'
        cases = ' '.join(outdirnames)
        exec_shell(f'python {str(pypaescal_dir)}/pypaescal.py -datapath {str(clubb_dir)}/output -c {cases} -o {str(clubb_dir)}/output --pdf')
    
    finish = time.perf_counter()

    logging.info(f'\nFinished in {round(finish-start, 2)} second(s)')
    logging.info('\n################################## Process Finished ##################################')
    logging.info('######################################################################################\n')
    
    print(f'\nFinished in {round(finish-start, 2)} second(s)')

