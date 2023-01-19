#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#SBATCH --job-name=plot_monthly_trajectories
#SBATCH --ntasks=1
#SBATCH --mem=1gb
#SBATCH --time=03:00:00
#SBATCH --output=log_plotting_script

"""
Created on Sun Mar 15 15:46:37 2020

@author: mjr583
"""
import os 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import sys
matplotlib.use('agg')
from netCDF4 import Dataset, stringtochar
import datetime 
from scipy.io import FortranFile
import pandas as pd

def find_file_list(path, substrs):
    file_list =[]
    for root, directory, files in os.walk(path):
        for f in files:
            for s in substrs:
                if s in f:
                    file_list.append(os.path.join(root, f))
    file_list.sort()
    return file_list

def read_flexpart_output(JOBID, date):
    all_lons=[] ; all_lats=[] ; all_alts=[]
    filen=f'flex_{date}'
    for filename in sorted( find_file_list( f'{JOBID}/{filen}/output/', ['partposit'] ) ):
        f = FortranFile(filename, 'r')
        print(f.read_record('i4'))
        Ender=False
        counter=0
        lats=np.zeros(10000)
        lons=np.zeros(10000)
        alts=np.zeros(10000)
        
        while not(Ender):
          A=f.read_record('i4','f4','f4','f4','i4','f4','f4','f4','f4','f4','f4','f4','f4')
          if (A[0][0]==-99999):
            Ender=True
          else:
            lons[counter]=A[1][0]
            lats[counter]=A[2][0]
            alts[counter]=A[3][0]
            
            counter=counter+1
        lons=lons[:counter-1]
        lats=lats[:counter-1]
        alts=alts[:counter-1]

        all_lons.append(lons) ; all_lats.append(lats) ; all_alts.append(alts)  
    return all_lons, all_lats, all_alts

def write_netcdf( JOBID, date, dt, lons, lats, alts):
    ncdf_file=Dataset(f'{JOBID}/netcdfs/{date}.nc', 'w', clobber='true')
    ncdf_file.title = (f'FP trajectory data - {dt.strftime("%Y-%m-%d %H:%M")}' )
    ncdf_file.description = 'Trajectories calculated using FLEXPART v10.4, driven by GFS meteorological reanalyses. Number of particles = '+str(len(lons[1]))+'. Point of release = XXXX (XX.XX N, XX.XX E)'
    ncdf_file.references = 'https://www.geosci-model-dev.net/12/4955/2019/gmd-12-4955-2019-discussion.html'

    # Write dimensions
    total_time = len(lons) * 10800
    nparticles = len(lons[1])    
    ncdf_file.createDimension('seconds_since_release', len(lons))
    ncdf_file.createDimension('timestamp',len(lons))
    ncdf_file.createDimension('particle',nparticles)
    step=total_time/len(lats)

    # Write variables
    time = ncdf_file.createVariable('seconds_since_release',np.int32, ('seconds_since_release'))
    time.units = 'Seconds since particles released'
    time[:] = np.arange(step,total_time+step,step)

    datetimes=[]
    for sec in np.arange(step,total_time+step,step):
        DATE = str(dt - datetime.timedelta(seconds=float(sec)))
        datetimes.append(DATE)
    datetimes=np.array(datetimes)

    timestamp = ncdf_file.createVariable('timestamp', str, ('timestamp'))
    timestamp.units = 'Timestamp of model output'
    timestamp[:] = datetimes

    particles = ncdf_file.createVariable('particle',np.int32, ('particle'))
    particles.units = 'Particle number'
    particles[:] = range(1,nparticles+1)

    latitude = ncdf_file.createVariable('Latitude',float, ('seconds_since_release','particle'))
    latitude.units = 'Degrees'
    latitude[:] = np.array(lats)

    longitude = ncdf_file.createVariable('Longitude',float, ('seconds_since_release','particle')) 
    longitude.units = 'Degrees'
    longitude[:] = np.array(lons)

    altitude = ncdf_file.createVariable('Altitude',float, ('seconds_since_release','particle')) 
    altitude.units = 'Metres'
    altitude[:] = np.array(alts)

    return ncdf_file.close()
    #return 

###------------------------------------MAIN-SCRIPT----------------------------------------------------------###
def main():
    NUMBER = int(sys.argv[1]) - 1 
    JOBID  = sys.argv[2]
    
    ### Read date from array_dates and then read FLEXPART output
    array_dates= pd.read_csv( f'{JOBID}/array_dates_{JOBID}' , header=None, delimiter=' ' )
    date  =  array_dates.iloc[NUMBER,1]
    dt=pd.to_datetime( date, format="%Y%m%d%H%M" )
    lons, lats, alts = read_flexpart_output(JOBID, date)
    
    ### Save output as netcdf file 
    write_netcdf( JOBID, date, dt, lons, lats, alts)
    ## Clean up the array job
    os.system( f"rm -rf {JOBID}/flex_{date}" )

if __name__=="__main__":
    main()
