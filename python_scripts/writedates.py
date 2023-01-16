#!/usr/bin/env python
from datetime import datetime, timedelta
import os
import sys

year=int(sys.argv[1])
month=int(sys.argv[2])

path='/users/mjr583/scratch/flexpart/manchester-supersite/'+str(year)+'/'
out=open(os.path.join(path,'array_dates_'+str(month).zfill(2)),'w')

# Get desired start and end dates
def daterange(start_date, end_date):
    delta = timedelta(hours=1)
    while start_date < end_date:
        yield start_date
        start_date += delta

from_start = datetime(year, month, 1, 00, 00)
from_end = datetime(year, month+1, 1, 00, 00)
ends=[]
for single_date in daterange(from_start, from_end):
    x = single_date.strftime("%Y%m%d%H%M")
    #print( x )
    ends.append(x)

until_start = from_start - timedelta(days=10)
until_end = from_end - timedelta(days=10)
starts=[]
for single_date in daterange(until_start, until_end):
    x = single_date.strftime("%Y%m%d%H%M")
    starts.append(x)

for i in range(len(starts)):
    out.write(starts[i]+' '+ends[i]+'\n')
