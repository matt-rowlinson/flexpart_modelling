#!/usr/bin/env python3
#SBATCH --partition=nodes
#SBATCH --time=02:00:00
#SBATCH --mem=1gb
#SBATCH --output=LOGS/log_%A.log
#SBATCH --job-name=GFS_download
import sys
import datetime
import urllib.request

def str2date(date):
    year=date[:4]
    month=date[4:6]
    day=date[6:]
    date=datetime.datetime(int(year),int(month),int(day))
    return date

def get_filenames(date):
    filelist=list()
    if date > datetime.datetime(2020,5,17):
        for t in ["0000","0600","1200","1800"]:
            filelist.append("gfs_4_"+date.strftime('%Y%m%d')+"_"+t+"_000.grb2")
    else:
        for t in ["0000","0600","1200","1800"]:
            filelist.append("gfsanl_4_"+date.strftime('%Y%m%d')+"_"+t+"_000.grb2")
    return filelist

start=sys.argv[1]
end=sys.argv[2]
start=str2date(start)
end=str2date(end)

datelist = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days+1)]
for date in datelist:
    filelist=get_filenames(date)
    hour=["00","06","12","18"]
    for h,f in enumerate(filelist):
        if date > datetime.datetime(2020,5,17):
            url='https://www.ncei.noaa.gov/data/global-forecast-system/access/grid-004-0.5-degree/analysis/'
            file_url=url+date.strftime('%Y%m')+'/'+date.strftime('%Y%m%d')+'/'+f
        else:
            url='https://www.ncei.noaa.gov/data/global-forecast-system/access/historical/analysis/'
            file_url=url+date.strftime('%Y%m')+'/'+date.strftime('%Y%m%d')+'/'+f

        try:
            urllib.request.urlretrieve(file_url,'/users/mjr583/scratch/flexpart/preprocess/flex_extract/05x05/GF'+date.strftime('%y%m%d')+hour[h])
            print('Download grib file', f)
            last_working_file=file_url
        except:
            with open('/users/mjr583/scratch/flexpart/preprocess/gfs_data/code/missingfiles_05x05.txt','a') as missfile:
                missfile.write("".join(f)+"\n")
            if not last_working_file:
                pass
            else:
                urllib.request.urlretrieve(last_working_file,'/users/mjr583/scratch/flexpart/preprocess/flex_extract/05x05/GF'+date.strftime('%y%m%d')+hour[h])
                print('Download grib file', f,': Does not exist. Copying previous file.')
print("Finished")
