#!/usr/bin/env python
from datetime import datetime, timedelta
import os
import sys
import pandas as pd

def daterange(start_date, end_date, frequency=6):
    delta = timedelta(hours=frequency)
    while start_date < end_date:
        yield start_date
        start_date += delta

def main():
    jobid     = sys.argv[3]
    frequency = int(sys.argv[4])
    start = pd.to_datetime( sys.argv[1], format='%Y-%m-%d' )
    end   = pd.to_datetime( sys.argv[2], format='%Y-%m-%d' ) + timedelta(days=1)

    path='./'
    out=open(os.path.join(path,f'array_dates_{jobid}'),'w')

    ends=[]
    for single_date in daterange(start, end, frequency=frequency):
        x = single_date.strftime("%Y%m%d%H%M")
        ends.append(x)
    
    until_start = start - timedelta(days=10)
    until_end   = end   - timedelta(days=10)
    starts=[]
    for single_date in daterange(until_start, until_end, frequency=frequency):
        x = single_date.strftime("%Y%m%d%H%M")
        starts.append(x)

    for i in range(len(starts)):
        out.write(starts[i]+' '+ends[i]+'\n')

if __name__=="__main__":
    main()
