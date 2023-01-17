#!/usr/bin/env python3
import matplotlib
matplotlib.use('agg')
import sys
import numpy as np
import glob
import re
import datetime
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import matplotlib.colors as colors

import pandas as pd
from datetime import datetime, timedelta
import os
import cartopy.crs as ccrs
import xarray as xr
import matplotlib 

def get_trajectory_list(path, start, end):
    ## Get a list of available back-trajectories in the requested period
    startdate = pd.to_datetime( start, format='%Y-%m-%d' )
    enddate   = pd.to_datetime( end  , format='%Y-%m-%d' )
    days=[]
    for i in range( (enddate-startdate).days +1):
        days.append((startdate + timedelta(days=i)).strftime('%Y%m%d'))
    
    file_list =[]
    for root, directory, files in os.walk(path):
        for f in files:
            for s in days:
                if s in f:
                    file_list.append(os.path.join(root, f))
    file_list.sort()
    return file_list

def plot_trajectory_files( jobid, path, startdate, enddate, pref, xy, polar=False, site="cvao", altplot=False, altlim=1000.):
    ## Reads trajectories from a file list then initiates processing and plotting functions
    file_list=get_trajectory_list(path, startdate, enddate)
    for f in file_list:
        date = f.replace('.nc','').split('/')[-1]
        ds   = xr.open_dataset( f, decode_times=False )
        secs = ds.seconds_since_release.values
        lons = ds.Longitude.mean(dim='particle')
        lats = ds.Latitude.mean( dim='particle')
        alts = ds.Altitude.mean( dim='particle')

        print( f"create plot for {date}")
        plot_by_timestep( jobid, lons, lats, alts, date, xy, pref, polar=polar, site=site, altplot=altplot)
    return 

def plot_by_timestep(jobid, lons, lats, alts, dt, xy, pref='', polar=False, site="cvao", altplot=False):
    ## Creates one trajectory plot at each timestep
    if not polar:
        fig=plt.figure(figsize=(10,5))
        ax=fig.add_subplot(111, projection=ccrs.EqualEarth(), aspect='auto')
        ax.pcolormesh( range( 0,360), range( 0,180), grid,  cmap='inferno', transform=ccrs.PlateCarree(),
                   norm=matplotlib.colors.LogNorm())
        ax.stock_img()
        #ax.set_extent([-180,180,-90,90])
    else:
        fig=plt.figure(figsize=(7,7))
        ax=fig.add_subplot(111, projection=ccrs.NorthPolarStereo(central_longitude=0), aspect='auto')
        ax.scatter( xy[0], xy[1], marker='*', s=200, c='gold', transform=ccrs.PlateCarree() )
        ax.plot( lons, lats, '-', c='k', alpha=.5, transform=ccrs.PlateCarree() )
        im = ax.scatter( lons, lats, c=alts, lw=2, cmap='inferno', linestyle='solid',  transform=ccrs.PlateCarree() ) 
        ax.gridlines(lw=2, ec='black', draw_labels=False)
        ax.set_extent((-180,180,70,90), crs=ccrs.PlateCarree())
        ax.stock_img()

    cbar=fig.colorbar(im, pad=0.01, orientation='horizontal', shrink=.65 )
    cbar.set_label( 'Altitude (m)' )
    ax.coastlines(zorder=3)
    ax.set_title( pd.to_datetime(dt,format="%Y%m%d%H%M").strftime("%H:%Mz %d-%m-%Y") )
    
    plt.tight_layout()
    plt.savefig(f'./{jobid}/plots/{pref}_{dt}.png')
    plt.close()
    return

####-------------------------------------MAIN-SCRIPT------------------------------------------------###

def main():
    jobid = sys.argv[1]
    n     = int( jobid.split('_')[-1] ) - 1
    path = f'./{jobid}/netcdfs/'

    df = pd.read_csv('MOSAiC_LatLong.csv', index_col=0 )
    xy = (df.Longitude[n],df.Latitude[n])
    start = pd.to_datetime( df.index[n], format='%d/%m/%Y %H:%M').strftime( '%Y-%m-%d' )
    end   = start         ## Set last date you want plots for (can be the same as start for 1 day only)
    pref  = jobid         ## Add prefix to outputted filename
    
    ## Extra options
    polar   = True       ## Is the trajectory primaily over Polar regions?
    site    = 'mobile'   ## Only for looking at a different site
    altplot = False      ## Can be used to create plots at certain altitudes i.e. near the surface only
    altlim  = None       ## Set the limit if creating an altitude limited plot 

    plot_trajectory_files(jobid, path, start, end, pref, xy=xy, polar=polar, site=site, altplot=altplot, altlim=altlim)
    print( "done." ) 

if __name__=="__main__":
    main()
