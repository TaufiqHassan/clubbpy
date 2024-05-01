## clubbpy
**Python scripts to compile and run clubb standalone model**

Installation
------------
Git clone the repo and activate e3sm-unified environment for compiling and running the model
```bash
source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh
```
To use the `-plot` option which calls `pypaescal` we need to activate [`pypaescal` environment](https://github.com/PAESCAL-SciDAC5/CLUBB-fork/tree/thbranch/paescal_scripts/pypaescal#installation) as well
```bash
conda activate pypaescal
```
Optional: Users may export $CLUBBHOME env variable in the `.bashrc` file.
```bash
vi ~/.bashrc
export CLUBBHOME='/directory/to/CLUBB-fork/
```
This way they do not need to use `-d` option (as described below) to define the CLUBB directory.

Usage
-----
```console
python scm_test.py -h
```
```bash
usage: scm_test [-h] [-c C] [-d D] [-compile] [-plot] [-zmax ZMAX [ZMAX ...]] [-grid GRID [GRID ...]] [-dz DZ [DZ ...]] [-zbtm ZBTM [ZBTM ...]]
                [-ztop ZTOP [ZTOP ...]] [-ztfname ZTFNAME [ZTFNAME ...]] [-zmfname ZMFNAME [ZMFNAME ...]] [-dt DT [DT ...]]
                [-rad_scheme RAD_SCHEME [RAD_SCHEME ...]] [-tinit TINIT [TINIT ...]] [-tfinal TFINAL [TFINAL ...]] [-dtout DTOUT [DTOUT ...]]
                [-ctest CTEST] [-ref REF [REF ...]]

Python scripts to compile and run clubb standalone model

options:
  -h, --help            show this help message and exit

General arguments:
  Takes single or no input

  -c C                  CLUBB Case.
                        Default case: dycoms2_rf01
  -d D                  CLUBB model directory.
                        Default directory is defined by $CLUBBHOME
  -compile, --compile   Clean and compile CLUBB first. (No input)
  -plot, --plot         Produce pypaescal plots. (No input)

Case parameters:
  Allows multiple inputs

  -e E [E ...]          User-defined experiment names.
                        By default names are assigned based on dz/dt etc.
  -zmax ZMAX [ZMAX ...]
                        Number of vertical levels.
  -grid GRID [GRID ...]
                        Select grid type:
                        1 ==> evenly-spaced grid levels
                        2 ==> stretched (unevenly-spaced) grid
                        entered on thermodynamic grid levels;
                        3 ==> stretched (unevenly-spaced) grid
                        entered on momentum grid levels;
  -dz DZ [DZ ...]       Distance between grid levels on evenly-spaced grid (m).
  -zbtm ZBTM [ZBTM ...]
                        Minimum Altitude of lowest momentum level on any grid (m).
  -ztop ZTOP [ZTOP ...]
                        Maximum Altitude of highest momentum level on any grid (m).
  -ztfname ZTFNAME [ZTFNAME ...]
                        Path and filename of data file that contains
                        thermodynamic level altitudes (in meters).
  -zmfname ZMFNAME [ZMFNAME ...]
                        Path and filename of data file that contains
                        momentum level altitudes (in meters).
  -dt DT [DT ...]       Model timestep (s)
  -rad_scheme RAD_SCHEME [RAD_SCHEME ...]
                        Radiation scheme.
                        The schemes are: "bugsrad", simplified", "simplified_bomex", or "none".
  -tinit TINIT [TINIT ...]
                        Time_initial (s)
  -tfinal TFINAL [TFINAL ...]
                        Time_initial (s)
  -dtout DTOUT [DTOUT ...]
                        Frequency of statistical output (s)

Convergence configuration:
  Run Convergence tests.

  -ctest CTEST          Run convergence test.
                        3 different groups of settings:
                        (1) default,
                        (2) baseline,
                        (3) revall
  -ref REF [REF ...]    use a stretched grid with specified number of refinement.
```

Example usage
-------------
To clean, compile, and running 3 no radiation simulations with dz of 10, 100, and user defined values from `zm_E50.txt` file, we can use the following command
```bash
python scm_test.py -dz 10 100 10 -zmfname '' '' /user/input/file/directory/zm_E50.txt -grid 1 1 3 -rad_scheme none none none -compile
```
It will generate a log.clubb file and produce the outputs in $CLUBBHOME/output directory.
