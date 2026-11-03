import satpy
import sys
from satpy import find_files_and_readers, Scene
from pyproj import Proj
from pyresample.geometry import AreaDefinition
from pyresample import get_area_def
import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime,timedelta
import area
from area import get_parameters
import warnings

warnings.simplefilter('ignore')
# enable access to custom composites/enhancements 
os.environ['SATPY_CONFIG_PATH']='../'


def define_AOI(min_lon,max_lon,min_lat,max_lat,resolution):
    #using lambert conus conform projection which is appropriate for mid-latitudes, consider changing laea to merc for equatorial regions
    proj, lat_0, lon_0,xsize, ysize, area_extent=get_parameters("custom","merc",min_lon,max_lon,min_lat,max_lat,resolution)
    projection= '+proj=%s +lat_0=%s +lon_0=%s +ellps=%s'%(proj, lat_0, lon_0, 'WGS84')
    AOI = get_area_def("custom", '', proj, projection,xsize, ysize, area_extent)
    print("custom", '', proj, projection,xsize, ysize, area_extent)
    return AOI

if __name__ == '__main__':

    file_location=sys.argv[1]
    ch=sys.argv[2]
    time=sys.argv[3]
    #end=sys.argv[3]
    #step=sys.argv[4] #minutes
    coords=sys.argv[4] # fourtuple (min_lon,max_lon,min_lat,max_lat)
    resolution = sys.argv[5]
    min_lon=max_lon=min_lat=max_lat = 0
    predefined_region=False
    
    if (coords != "0"):
        if(len(coords.split(",")) ==4):
            coord=coords.split(",")
            min_lon = float(coord[0])
            max_lon = float(coord[1])
            min_lat= float(coord[2])
            max_lat = float(coord[3])
        else:
            predefined_region=True
            print("predefined satpy region: ",coords)
    
    print("processing timestep: ",time)
    start_time=datetime.strptime(time,"%Y-%m-%dT%H:%M:%SZ")
    end_time=datetime.strptime(time,"%Y-%m-%dT%H:%M:%SZ")+timedelta(minutes=10) # 10-minute resolution of the data
    
    files = find_files_and_readers(base_dir=file_location, reader='fci_l1c_nc',filter_parameters={'start_time': start_time , 'end_time': end_time})
    scn = Scene(filenames=files)

    scn.load([ch], upper_right_corner='NE')
     
    if (coords != "0" and not predefined_region):
        AOI = define_AOI(min_lon,max_lon,min_lat,max_lat,resolution)
        scn_resample=scn.resample(AOI) # nearest neighbor interpolator
        scn_resample.save_dataset(ch, filename='plots/fci_%s_%s.png' % (ch,datetime.strftime(start_time,"%Y%m%dT%H%M%SZ")),
                       overlay={'coast_dir':'/tmp/gshhg-shp-2.3.7','color':'black','resolution':'l', 'width': 1.5})
    else:
        if (predefined_region):
            scn_resample=scn.resample(coords)
            scn_resample.save_dataset(ch, filename='plots/fci_%s_%s_%s.png' % (ch,coords,datetime.strftime(start_time,"%Y%m%dT%H%M%SZ")),
                       overlay={'coast_dir':'/tmp/gshhg-shp-2.3.7','color':'black','resolution':'l', 'width': 1.5})
        else:
            scn2=scn.resample()
            scn2.save_dataset(ch, filename='plots/fci_%s_%s.png' % (ch,datetime.strftime(start_time,"%Y%m%dT%H%M%SZ")),
                       overlay={'coast_dir':'/tmp/gshhg-shp-2.3.7','color':'black','resolution':'l', 'width': 1.5})
    
