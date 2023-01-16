#!/usr/bin/env python3
#SBATCH --time=00:01:00
#SBATCH --mem=500mb
#SBATCH --job-name=FLEXPART_run
#SBATCH --partition=nodes
#SBATCH --output=Logs/FP_shell_%A.log

import os
import sys
import datetime
import pandas as pd
sys.path.insert(1, './python_scripts/')

def setup_flexpart_run( job_id, njobs, start, coords, nparticles):
    year = start[:4]
    sed_cmd_0 = (f'sed -i "s/#SBATCH --array.*/#SBATCH --array=1-{njobs}/" ./job_array')
    sed_cmd_1 = (f'sed -i "s/JOBID=.*/JOBID={job_id}/" ./job_array')
    sed_cmd_2 = (f'sed -i "s/YEAR=.*/YEAR={year}/" ./job_array')

    coords_0  = (f'sed -i "s/LLLON=.*/LLLON="{coords[0]}"/" ./job_array') 
    coords_1  = (f'sed -i "s/LLLAT=.*/LLLAT="{coords[1]}"/" ./job_array')
    coords_2  = (f'sed -i "s/ALT=.*/ALT="{coords[2]}"/" ./job_array')
    nparts_0  = (f'sed -i "s/NPARTICLES=.*/NPARTICLES="{nparticles}"/" ./job_array')

    os.system(sed_cmd_0)
    os.system(sed_cmd_1)
    os.system(sed_cmd_2)

    os.system(coords_0)
    os.system(coords_1)
    os.system(coords_2)
    os.system(nparts_0)
    return

def write_dates(start, end, job_id):
    cmd = f"python python_scripts/array_dates.py {start} {end} {job_id}"
    os.system( cmd )
    return

def submit_flexpart_run():
    flexpart_cmd=("sbatch job_array")
    os.system(flexpart_cmd)

def find_njobs(start, end):
    s = pd.to_datetime( start, format="%Y-%m-%d" )
    e = pd.to_datetime( end  , format="%Y-%m-%d" )
    njobs = ((e - s).days + 1) * 4
    return njobs

##------------------------------------------------ MAIN SCRIPT ----------------------------------------------------##
def main():
    # Select dates to run FLEXPART trajectories in format "YYYY-MM-DD (end date is inclusive)
    start_date = '2019-11-01'
    end_date   = '2019-11-03'
    njobs      = find_njobs( start_date, end_date )
    job_id     = 'third_test_run'
    
    # Set coordinates of particles to be released
    lon_of_release = -24.9
    lat_of_release = 16.9
    alt_of_release = 10
    n_particles    = 1001
    coords=[lon_of_release,lat_of_release,alt_of_release]
    
    # Setup config files and submit FLEXPART run
    write_dates(start_date, end_date, job_id)
    setup_flexpart_run( job_id, njobs, start_date, coords, n_particles )
    submit_flexpart_run()

if __name__=="__main__":
    main()
