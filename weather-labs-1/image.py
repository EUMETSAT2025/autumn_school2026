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
import datetime
import area2
from area2 import get_parameters

file_location=sys.argv[1]
ch=sys.argv[2]
time=sys.argv[3]
#end=sys.argv[3]
#step=sys.argv[4] #minutes
coords=sys.argv[4] # fourtuple (min_lon,max_lon,min_lat,max_lat)
resolution = sys.argv[5]

#print(coords.split(","))
coord=coords.split(",")
min_lon = float(coord[0])
max_lon = float(coord[1])
min_lat= float(coord[2])
max_lat = float(coord[3])

# NOTE: /data/Weather/ is no longer accessible on TrainHub. Change the /data/Weather/ paths here to where your data is.
path_to_data='/data/Weather/FCI_Autumn_School/'
files = find_files_and_readers(base_dir=file_location, reader='fci_l1c_nc')
scn = Scene(filenames=files)
#ch='true_color_raw_with_corrected_green'
scn.load([ch], upper_right_corner='NE')

proj, lat_0, lon_0,xsize, ysize, area_extent=get_parameters("custom","merc",min_lon,max_lon,min_lat,max_lat,resolution)
print(proj,lat_0,lon_0,xsize,ysize,area_extent)
#%run coord2area_def.py {area_name} {proj} {min_lat} {max_lat} {min_lon} {max_lon} {resolution}
#coord2area_def.main("custom", "merc", min_lat, max_lat, min_lon, max_lon, resolution)
projection= '+proj=%s +lat_0=%s +lon_0=%s +ellps=%s'%(proj, lat_0, lon_0, 'WGS84')
AOI = get_area_def("custom", '', proj, projection,xsize, ysize, area_extent)
print(projection)
print(AOI)
#AOI='eurol'
scn_resample=scn.resample(AOI)

scn_resample.show(ch,{'coast_dir': '/tmp/gshhg-shp-2.3.7', 'color': (255, 255, 255), 'resolution': 'l', 'width': 4.5})
scn_resample.save_dataset(ch, filename='fci_%sRGB_%s.png' % (ch,time),
                   overlay={'coast_dir':'/tmp/gshhg-shp-2.3.7','color':'black','resolution':'l', 'width': 4.5})

