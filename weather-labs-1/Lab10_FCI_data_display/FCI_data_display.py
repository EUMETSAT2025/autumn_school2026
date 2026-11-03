#!/usr/bin/env python
# coding: utf-8

# <img src='./logos/EUMETSAT_Logo_WhiteonBlue.png' alt='logo EUMETSAT' align='center' width='30%'></img>

# # Display FCI test data
# 
# > **The purpose of this Jupyter Notebook (JN) is to display FCI test data**<br><br>
# To run this JN you need to activate environment fci_minimal. <br>
# > You can activate the environment either: <br>
# > - in command line: `conda activate MTG`;<br>
# > - in this page, going to the top menu `-> Kernel-> change kernel->MTG` <br><br>
# 
# 
# >## Basic facts <b>
# >    
# >> **Spatial resolution:** 1 or 2 km at nadir (depending on the spectral channel)<br>
# **Spatial coverage:** Latitude: -81 to 81 degrees, Longitude: -79 to 79 degrees <br>
# **Revisit time:** every 10 minutes <br>
# **Data availability:** This test data is available for the 20.09.2017, covering 24 hours, every 10 minutes, i.e, it contains 144 slots<br><br>
# **Data description:**<br>
# *This test package represents a scientifically consistent representation of top of Atmosphere 
# radiance as it will be observed by the FCI instrument. These TOA radiances are computed at 
# each pixel location using a detailed characterisation of the vertical profile of atmospheric 
# constituents and accurate radiative transfer computations.*<br> <br>
# *The output of the TOA radiances simulation framework is in the native SEVIRI spatial 
# resolution (3km grid) and temporal resolution (15 minutes repeat cycle). To generate this FCI 
# dataset, a nearest-neighbour approach was applied to upsample the simulated data to the FCI 
# spatial sampling (1km and 2 km grids)*   <br>
# >   
# >    
# >    ## How to access the data
# >
# >> **Data has been downloaded from:** <br>
# >>
# >> https://sftp.eumetsat.int/public/folder/UsCVknVOOkSyCdgpMimJNQ/User-Materials/Test-Data/MTG>>/MTG_FCI_L1C_SpectrallyRepresentative_TD-360_May2022/<br><br>
# >> **In virtual machines, the data can be found at:**<br>
# >> `/data/Weather/fci_l1c_nc/MTGTD-360/`
# >    
# > ## Module Outline 
# >> - 1. Load required libraries
# >> - 2. Load data
# >> - 3. Browse the pre-defined composites 
# >> - 4. Select a single channel or an RGB composite to be displayed 
# >> - 5. Set up the area for display
# >> - 6. Resample to the set AOI and Display Data
# >> - 7. Save the Image to a png file

# ## 1. Load required libraries

# In[ ]:


# turning off warnings and limiting the number of resources %run ../init_notebook.py
get_ipython().run_line_magic('run', './init_notebook.py')

from satpy.scene import Scene
from satpy import find_files_and_readers
from pyproj import Proj
from pyresample.geometry import AreaDefinition
from pyresample import get_area_def
import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import datetime

# enable access to custom composites/enhancements 
os.environ['SATPY_CONFIG_PATH']='../'


# ## 2. Load data 
#     
# > In the next step we will point to the data location and load desired data using the Scene module from satpy.<br> 
# >
# > The FCI test data is available in 144 ten-minute scans, each of them in a respective directory.  <br> 
# 
# **`What can you change?`**<br> 
# **`Here you will be able to select the slot you want to display`** <br> Please edit the **`HOUR`** and **`MINUTE`** arguments in the `cell bellow` to be able to load the data from the appropriate time slot (directory).

# In[ ]:


HOUR=12
MINUTE=0


# ### 2.1 Search for the selected slot in the folders  

# In[ ]:


start_datetime=datetime.datetime(year=2017,month=9,day=20,hour=0)

scan_time=datetime.datetime(year=2017,month=9,day=20,hour=HOUR,minute=MINUTE)


diff=scan_time-start_datetime
order_nr=int(diff.seconds/600)+1  
directory_name_str=f'RC{order_nr:04}'

# NOTE: /data/Weather/ is no longer accessible on TrainHub. Change the /data/Weather/ paths here to where your data is.
path_to_data = '/data/Weather/fci_l1c_nc/MTGTD-360/%s/'% (directory_name_str)

# find files and assign the FCI reader
files = find_files_and_readers(base_dir=path_to_data, reader='fci_l1c_nc')
scn = Scene(filenames=files)


# In[ ]:


files


# ## 3. Browse the pre-defined composites <b> 
# > All the available pre-defined composites and single-channel image visualizations are presented next. <br>
# >    
# > Note that this takes into consideration both the default imagery for the satpy reader 'fci_l1c_nc' and any custom created composites. To know how to create a custom composite please refer to **3.2 Add a composite**

# In[ ]:


scn.available_composite_names()


# ### 3.1 Add a composite
# 
# > To fine tune composite or single channel images, the following files nedd to be edited:
# > * ./enhancements/fci.yaml
# > * ./composites/fci.yaml
# <br>
# > 
# There we can define a colormap from available ones that can be found in: https://github.com/pytroll/trollimage/blob/main/trollimage/colormap.py . Some of the popular ones are: 'grays', 'blues', and so forth. 
# 

# ## 4. Select a single channel or an RGB composite to be displayed

# **`What can you change?`**<br> 
# **`Here you will be able to select the channel/RGB composite you want to display`** please edit the **`ch`**  in the `cell bellow`:

# In[ ]:


ch='cloud_phase'
scn.load([ch], upper_right_corner='NE')


# In[ ]:


scn.show(ch,{'coast_dir': '/tmp/gshhg-shp-2.3.7', 'color': (255, 255, 255), 'resolution': 'l', 'width': 4.5})


# ## 5. Set up the area for display. <b>
# **`What can you change?`**<br> 
# **`Here you will be able to set up the subset area for display. For this you need to edit the variables in the cell below`**
# 
# >- **`'area_name='`** is the name you want to give to your Area Of Interest (AOI)<br><br>
# >    
# >- **`'proj='`** is the projection to be used to display the data. There are many projections that can be used to display the data, but most popular ones are: <br> <br>
# >    
# >    - *`'laea'`*, or Lambert Azimuthal Equal-Area projection ; <br>
# >    - *`'geos'`*, or Full Disk native-view projection;<br>
# >    - *`'merc'`*, or Mercator projection.<br><br> 
# > - The variables `'min_latitude'`, `'max_latitude'`, `'min_longitude'`, and `'max_longitude'` need to be set to define your AOI to be displayed: <br>
# >- **`'min_latitude='`**
# >- **`'max_latitude='`**
# >- **`'min_longitude='`**
# >- **`'max_longitude='`**
# >    
# >- **`'resolution='`** is the desired horizontal resolution, in Km.
# >    
# >Example of usage: <br>
# >    
# >- **`area_name=`**'Iberian'  
# >- **`proj=`**'laea'           
# >- **`min_latitude=`**-30.
# >- **`max_latitude=`**30.
# >- **`min_longitude=`**-10.
# >- **`max_longitude=`**30.
# >- **`resolution=`**1.0 # km
# 

# In[ ]:


area_name='Iberian'  
proj='laea'           
min_latitude=40.
max_latitude=50.
min_longitude=0.0
max_longitude=20.0
resolution=3.0 # km


# In[ ]:


min_lat=float(min_latitude)
max_lat=float(max_latitude)
min_lon=float(min_longitude)
max_lon=float(max_longitude)
res=float(resolution) 


# In[ ]:


get_ipython().run_line_magic('run', 'coord2area_def.py {area_name} {proj} {min_lat} {max_lat} {min_lon} {max_lon} {resolution}')


# ## 6. Resample to the set AOI and Display Data
# In the next cell we will: <br>
# * generate the necessary parameters by using the function *coord2area_def.py* <br>
# * resample to desired area <br>
# * display the desired image.

# In[ ]:


projection= '+proj=%s +lat_0=%s +lon_0=%s +ellps=%s'%(proj, lat_0, lon_0, 'WGS84')
AOI = get_area_def(name, '', proj, projection,xsize, ysize, area_extent)
#AOI='eurol'
scn_resample=scn.resample(AOI)

#scn_resample.show(ch,{'coast_dir': '/tmp/gshhg-shp-2.3.7', 'color': (255, 255, 255), 'resolution': 'l', 'width': 4.5})



# In[ ]:


get_ipython().run_line_magic('matplotlib', 'notebook')

scn1=scn_resample

imagePath=str('tiffs/'+area_name+ch+'.tif')
scn_resample.save_dataset(ch,imagePath,fill_value=0,
                  overlay={'coast_dir':'/tmp/gshhg-shp-2.3.7','color':'','resolution':'l'})

img1 = plt.imread(imagePath)

crs1=ccrs.PlateCarree()
plt.figure(figsize=(12,6))
crs1 = scn_resample[ch].attrs["area"].to_cartopy_crs()
ax1 = plt.axes(projection=crs1)
ax1.gridlines(linestyle='--', draw_labels=True) 
ax1.coastlines()
states_provinces = cfeature.NaturalEarthFeature(
    category="cultural",
    name="admin_0_countries",
    scale="50m",
    facecolor="none")
ax1.add_feature(states_provinces, edgecolor="white")
image_time=datetime.datetime.strftime(scn_resample[ch].attrs['start_time'],"%Y-%m-%dT%H:%M:%SZ")
#ax1.set_title('%s \n %s' %(ch,image_time))
#ax1.set_title('%s' %(ch))

ax1.imshow(img1, transform=crs1, extent=crs1.bounds, origin="upper",cmap='Greys')
#plt.text(-300000, -700000, image_time, backgroundcolor='white',fontsize='large')#,fontweight='bold') #bbox=dict(fill=True ),
plt.savefig('a.jpg',bbox_inches='tight')
#plt.close()


# ## 7. Save the Image to a png file
# By running the cell below the image will be saved as a file. **It will be saved to directory './plots/'.**

# In[ ]:


scn_resample.save_dataset(ch, filename='plots/fci_%sRGB_%s.png' % (ch,datetime.datetime.strftime(scn_resample[ch].attrs['start_time'],"%Y%m%dT%H%M")),
                   overlay={'coast_dir':'/tmp/gshhg-shp-2.3.7','color':'black','resolution':'l', 'width': 4.5})


# In[ ]:


scn.save_dataset(ch, filename='plots/fci_%sRGB_%s.png' % (ch,datetime.datetime.strftime(scn_resample[ch].attrs['start_time'],"%Y%m%dT%H%M")),
                   overlay={'coast_dir':'/tmp/gshhg-shp-2.3.7','color':'black','resolution':'l', 'width': 4.5})

