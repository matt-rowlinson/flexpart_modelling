#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#SBATCH --job-name=create_csv
#SBATCH --time=02:00:00
#SBATCH --mem=8gb
#SBATCH --output=LOGS/get_csv_%A.log

"""
Created on Wed Apr 22 15:02:05 2020
@author: matthewrowlinson
"""
import sys
import os
from netCDF4 import Dataset
import glob
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

sys.path.append(os.getcwd())
sys.path.append('/users/mjr583/scratch/python_lib/')
import boxes as boxes
import RowPy as rp

def gen_file_list(year, month, end=False,res='05x05',add=''):
    print('Get file list')
    file_list=[]
    year=str(year)
    month=str(datetime(int(year), int(month), 1).strftime('%m'))
    
    traj='/users/mjr583/scratch/flexpart/'+RES+'_gfs/CV_ARRAYJOBS/'+year+'/netcdfs/'+year+month+'*.nc'
    for nfile in sorted(glob.glob(traj)):
        file_list.append(nfile)

    return file_list

def get_datetimes(file_list):
    datetimes=[]
    import dateutil.parser as dparser
    import re
    from datetime import datetime
    for f in file_list:
        match=re.search(r'\d{4}\d{2}\d{2}\d{2}', f)
        date = datetime.strptime(match.group(),"%Y%m%d%H")#.date()
        date = datetime.strftime(date,"%d/%m/%Y %H:%M")
        datetimes.append(date)
    return datetimes


def get_coords(file_list):
    print('Get particle coordinates')
    lats=[] ; lons=[] ; alts=[]
    for infile in file_list:
        print(infile) 
        fh=Dataset(infile)
        
        lon=fh.variables['Longitude'][:]
        lat=fh.variables['Latitude'][:]
        alt=fh.variables['Altitude'][:]
        
        lons.append(lon)
        lats.append(lat)
        alts.append(alt)

    lons=np.array(lons)
    lats=np.array(lats)
    alts=np.array(alts)

    return lons,lats,alts


def npart(file_list):
    for infile in file_list[:1]:
        fh=Dataset(infile)
        lon=fh.variables['Longitude'][:]
        nparticles=lon.shape[1]
    return nparticles


def gen_savename(start, end=False, res=False, limit=False,note=False, add=''):
    txt=str(start)
    if end:
        txt+=('-'+str(end))
    if res:
        txt+=('_'+str(res))
    if limit:
        txt+=('_'+str(limit)+'m')
    if note:
        txt+=('_'+str(note))
    if add != '':
        txt+=('_'+str(add))

    txt+=('.csv')
    return txt


##-------------------MAIN---------------------------------------##

global options,args
import optparse
parser = optparse.OptionParser(
        formatter = optparse.TitledHelpFormatter(),
        usage = globals()['__doc__'])

parser.add_option('-y', '--year',
        dest = 'YEAR',
        help = 'Year String (YYYY)')

parser.add_option('-m', '--month',
        dest = 'MONTH',
        help = 'MONTH Number (String)')

parser.add_option('-e', '--enddate',
        dest = 'END',
        default = '',
        help = 'End year (YYYY)')

parser.add_option('-r', '--resolution',
        dest = 'RES',
        default = '05x05',
        help = 'Met data resolution (1x1 or 05x05)')

parser.add_option('-a', '--altitude',
        dest = 'limit',
        default = 100,
        help = 'Altitude cut off in metres (Default is 100)')

parser.add_option('-n', '--note',
        dest = 'note',
        default = '',
        help = 'Optional additional string to be added to filename')

parser.add_option('-A', '--add',
        dest = 'add',
        default = '',
        help = 'Optional additional string to specify experimental runs')

parser.add_option('-b', '--boxes',
        dest = 'boxes',
        default = 1,
        help = '0=Old boxes (NAME), 1=New boxes')
(options, args) = parser.parse_args()

try:
    year=options.YEAR
    month=options.MONTH
except:
    'Must give year/years to be processed'
    sys.exit()
END=options.END
RES=options.RES
limit=int(options.limit)
note=options.note
add=options.add
box=int(options.boxes)

outpath='/users/mjr583/scratch/flexpart/manchester-supersite/airmass_files/'
file_list=gen_file_list(year, month, end=END,res=RES, add=add)
dt=get_datetimes(file_list)
lons,lats,alts=get_coords(file_list)
nparticles=npart(file_list)

hold=[]
print('Calculating airmass %')
for i in range(len(lats)):
    print(i)
    if box==0:
        number, pc, over = boxes.new_boxes_0(lats[i], lons[i], alts[i],nparticles,limit=limit)
    elif box==1:
        number, pc, over = boxes.boxes_1(lats[i], lons[i], alts[i],nparticles,limit=limit)
    pc = np.round(pc, 2)
    hold.append(pc)
hold_pc = np.array(hold)

print('Arranging columns and saving')
df = pd.DataFrame(hold_pc)
df.columns=['Upwelling','Sahel','Sahara','West Africa','North Africa','Europe','North America',
                'South America','North Atlantic','South Atlantic']
df.index = dt
df.index.name='Datetime'

import os
savename=gen_savename(year,END,RES,limit,note,add)

if not os.path.exists(outpath+savename):
    print('Creating')
    df.to_csv(outpath+savename,sep=",",header='column_names') 
else:
    print('Appending')
    df.to_csv(outpath+savename,sep=",",mode='a', header=False) 
print('Done')
