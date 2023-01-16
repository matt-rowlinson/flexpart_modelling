#!/usr/bin/env python
from datetime import datetime, timedelta
import os
import sys

def daterange(start_date, end_date):
    delta = timedelta(hours=6)
    while start_date < end_date:
        yield start_date
        start_date += delta

def main():
    jobid = sys.argv[3]
    start = list(map(int,sys.argv[1].split('-')))
    start = datetime( start[0], start[1], start[2] )

    end   = list(map(int,sys.argv[2].split('-')))
    end   = datetime( end[0],   end[1],   end[2] ) + timedelta(days=1)

    path='./'
    out=open(os.path.join(path,f'array_dates_{jobid}'),'w')

    ends=[]
    for single_date in daterange(start, end):
        x = single_date.strftime("%Y%m%d%H%M")
        ends.append(x)

    until_start = start - timedelta(days=10)
    until_end   = end   - timedelta(days=10)
    starts=[]
    for single_date in daterange(until_start, until_end):
        x = single_date.strftime("%Y%m%d%H%M")
        starts.append(x)

    for i in range(len(starts)):
        out.write(starts[i]+' '+ends[i]+'\n')

if __name__=="__main__":
    main()
