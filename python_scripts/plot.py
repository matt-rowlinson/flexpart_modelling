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

def get_grid(lon, lat, alt, altplot=False, altlim=1000):
    ## Creates a simple 1x1 grid and adds 1 for every particle in that grid per timestep.
    grid=np.zeros((180,360))
    for i in range(len(lon)):
        #print( i ) 
        if altplot:
            if alt[i] < altlim:
                grid[int(lat[i]),int(lon[i])]+=1
            else:
                pass
        else:
            #print( lat[i], lon[i] )
            grid[int(lat[i]),int(lon[i])]+=1
    fltr=np.where(grid<=1.) ## Filter out boxes with only n particles (makes for a cleaner plot).
    grid[fltr]=np.nan
    return grid

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

def plot_trajectory_files(path, startdate, enddate, pref, polar=False, site="cvao", altplot=False, altlim=1000.):
    ## Reads trajectories from a file list then initiates processing and plotting functions
    file_list=get_trajectory_list(path, startdate, enddate)
    for f in file_list:
        date = f.replace('.nc','').split('/')[-1]
        ds   = xr.open_dataset( f, decode_times=False )
        secs = ds.seconds_since_release.values
        lats=ds['Latitude'].values
        lons=ds['Longitude'].values
        alts=ds['Altitude'].values
        length=lats.shape[0]*lats.shape[1]
        lat=np.reshape(lats,length)
        lon=np.reshape(lons,length)
        alt=np.reshape(alts,length)
        grid=get_grid(lon,lat,alt, altplot=altplot, altlim=altlim)
        print( f"create plot for {date}")
        plot_by_timestep(grid, lons, lats, date, pref, polar=polar, site=site, altplot=altplot)
    return grid, lons, lats

def plot_by_timestep(grid, lons, lats, dt, pref='', polar=False, site="cvao", altplot=False):
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
        ax.pcolormesh( range( 0,360), range( 0,180), grid,  cmap='inferno', transform=ccrs.PlateCarree(),
                   norm=matplotlib.colors.LogNorm(), zorder=2)
        ax.gridlines(lw=2, ec='black', draw_labels=True)
        ax.set_extent((-180,180,70,90), crs=ccrs.PlateCarree())
    ax.coastlines(zorder=3)
    ax.set_title( dt )

    plt.tight_layout()
    plt.savefig(f'./plots/{pref}{dt}.png')
    plt.close()
    sys.exit()
    return

####-------------------------------------MAIN-SCRIPT------------------------------------------------###

def main():
    rdir = 'MOSAiC_1'
    path = f'./{rdir}/netcdfs/'
    
    start = '2019-11-11' ## Set first date you want plots for (YYYYMMDD)
    end   = '2019-11-11' ## Set last date you want plots for (can be the same as start for 1 day only)
    pref  = rdir         ## Add prefix to outputted filename

    ## Extra options
    polar   = True       ## Is the trajectory primaily over Polar regions?
    site    = 'mobile'   ## Only for looking at a different site
    altplot = False      ## Can be used to create plots at certain altitudes i.e. near the surface only
    altlim  = None       ## Set the limit if creating an altitude limited plot 

    plot_trajectory_files(path, start, end, pref, polar=polar, site=site, altplot=altplot, altlim=altlim)
    print( "done." ) 

if __name__=="__main__":
    main()
