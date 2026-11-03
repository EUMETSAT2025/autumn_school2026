import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy
#from glob import glob
import xarray as xr
import numpy as np
from datetime import datetime
import re
import os
import matplotlib as mpl
import pickle
 
from satpy.scene import Scene
from satpy.utils import debug_on
#debug_on()

class Area:
    def __init__(self, north=None, south=None, west=None, east=None, ):
        self.north = north
        self.south = south
        self.west = west
        self.east = east


def grid_totals(llats, llons, area=None, reso=1):
    """
    Computes the totals of lightning LGR/LFL lat/lon points per grid cell.
    Args:
      llats, llons = xarray data arrays of latitudes and longitudes.
      area = an area class object representing the area of interest.
      reso = grid resolution in degrees.
    Returns:
      totals = xarray data array containing the latitudes, longitudes and
        totals of lightning observations for each grid cell.
    """

    # The lat/lon bounds of the grid.
    if area is not None:
        latn, lats, lonw, lone = area.north, area.south, area.west, area.east
    else:
        latn, lats, lonw, lone = 85, -85, -85, 85

    # All lat and lon bins as 1d arrays.
    lat_bins = np.arange(lats, latn + reso, reso)
    lon_bins = np.arange(lonw, lone + reso, reso)

    totals = np.histogram2d(llons, llats, bins=(lon_bins, lat_bins),
                            range=[(lonw, lone), (lats, latn)])[0]

    totals = xr.DataArray(totals.T, coords=[lat_bins[:-1], lon_bins[:-1]],
        dims=['latitude', 'longitude'])

    totals['latitude'] = totals['latitude'] + reso / 2
    totals['longitude'] = totals['longitude'] + reso / 2

    return totals


def plot_li_fov_polygons(ax, projection=ccrs.PlateCarree()):
    """
    Plot the polygons of LI camera field-of-views on a map.
    Args:
      ax: axis with cartopy map to plot the polygons on.
    Returns:
      None, plots the polygons on the map.
    """

    polygons = [{'name': 'west', 'color': 'dodgerblue', 'file_path': './li_fov/LI_west.p'},
                {'name': 'north', 'color': 'darkorange', 'file_path': './li_fov/LI_north.p'},
                {'name': 'east', 'color': 'green', 'file_path': './li_fov/LI_east.p'},
                {'name': 'south', 'color': 'darkred', 'file_path': './li_fov/LI_south.p'}]

    for polygon in polygons:
        file_path = polygon['file_path']
        with open(file_path, 'rb') as pickle_file:
            poly = pickle.load(pickle_file)
        color = polygon['color']
        ax.add_geometries(poly, crs=projection, facecolor='none', edgecolor=color, lw=2)

    return


def plot_accmap(acc_grid, projection=ccrs.PlateCarree(), gridlines=True,
    vmax=None, area=None, plot_fov=False, title='', fname=None):
    """
    Plot the accumulated lightning locations heatmap.
    Args:
      acc_grid = xarray ready-to-plot lightning accumulation array.
      projection = map projection.
      gridlines = if True then plot map gridlines.
      vmax  = maximum value of observations per grid cell for colour scale.
      area = list defing the bounding box of the area or interest like [north, south, west, east].
      plot_fov = if True then plot the 4 LI camera field-of-views on the map.
      title = plot title str.
      fname = output file name, if given then save plot as file.
    Returns:
      None, displays and/or saves the plot.
    """

    if area is None:
        area = Area(85, -85, -85, 85)
    else:
        area = Area(area[0], area[1], area[2], area[3])

    # Create the figure, plot background map and title.
    fig, ax = plt.subplots(subplot_kw=({'projection': projection}))
    format_fig_size(fig, area)
    ax = plotmap(ax, gridlines=gridlines, area=area)
    fig.suptitle(title, y=0.92)

    # Plot the heatmap.
    if not vmax:
        vmax=10**5
    acc_grid.plot(ax=ax, transform=ccrs.PlateCarree(),
        norm=mpl.colors.LogNorm(vmin=1, vmax=vmax), cmap='gist_rainbow_r')

    # Plot area ploygons if required.
    if plot_fov:
        plot_li_fov_polygons(ax, projection=projection)

    # Save if file name is given.
    if fname:
        fig.savefig(fname, dpi=300, bbox_inches='tight')
        print(f'Saved the plot as {fname}!')

    return


def plotmap(ax, set_global=False, gridlines=False, area=None):
    """
    Initializes the figure and plots cartopy map with coastlines, country
    borders and gridlines.
    Args:
      ax = matplotlib axis object to plot the map on.
      set_global = if True then set the extent of the ax to the limits of the
        projection (can be actually smaller than global if national projection).
      gridlines = if True then plot gridlines.
      area = an area class object representing the area of interest.
    Returns:
      ax = input matplotlib axis object with the map.
    """
 
    # Add main map features.
    ax.add_feature(cartopy.feature.LAND)
    ax.add_feature(cartopy.feature.COASTLINE, zorder=2)
    ax.add_feature(cartopy.feature.BORDERS)
    ax.set_xlabel('lon')
    ax.set_ylabel('lat')
 
    # Set to the extent of the projection if required.
    if set_global:
        ax.set_global()
 
    # Plot gridlines if required.
    if gridlines:
        try:
            gridlines = ax.gridlines(draw_labels=True)
            gridlines.top_labels = None
            gridlines.right_labels = None
        except TypeError:
            gridlines = ax.gridlines()
 
    # Zoom into a sepecific area.
    if area:
        ax.set_xlim(area.west, area.east)
        ax.set_ylim(area.south, area.north)
 
    return ax
 
 
def format_fig_size(fig, area):
    """
    Spatial regions can be horizontal or vertical in shape. This function
    measures the sides of the lat/lon box in degrees and formats the figure
    size for best layout in the saved image (not so optimal for the live image
    window.
    Args:
      fig = matplotlib fig object to format.
      area = an area class object representing the area of interest.
    Returns:
      None, sets the figure width and height to the computed value, based
      on the shape of the area.
    """
 
    y_x_ratio = (area.north - area.south) / (area.east - area.west)
    # 8 and 6 are experimental and work best on saved plots.
    width = int(8 / y_x_ratio)
    height = 6
    fig.set_figwidth(width)
    fig.set_figheight(height)
 
 
def plot_lmap(lats, lons, time, projection=ccrs.PlateCarree(), gridlines=True,
              area=None, area_nswe=None, plot_fov=False, title=None):
    """
    Plot events/groups/flashes, coloured by hour of occurrence.
    Args:
      lats = xarray of latitudes
      lons = array of longitudes
      time = array of time information
      projection = map projection.
      gridlines = if True then plot map gridlines.
      area = an area class object defining the map extent in space.
      area_nswe = 4-element list of North South West East limits for area plot
      plot_fov = if True then plot the 4 LI camera field-of-views on the map.
      title = plot title str.
    Returns:
      None, displays and/or saves the plot.
    """

    if area_nswe is not None:
       area = Area(north=area_nswe[0], south=area_nswe[1], west=area_nswe[2], east=area_nswe[3])
 
    # Create the figure, plot background map and title.
    fig, ax = plt.subplots(subplot_kw=({'projection': projection}))
    format_fig_size(fig, area)
    ax = plotmap(ax, gridlines=gridlines, area=area)
    if title is not None:
        ax.set_title(title)
 
    # Create the colour bar.
    #sm = plt.cm.ScalarMappable(cmap=plt.get_cmap('gist_rainbow_r', 24))
    sm = plt.cm.ScalarMappable(cmap=plt.get_cmap('rainbow', 24))
    sm.set_clim(0, 24)
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_ticks([h + 0.5 for h in range(24)])
    cbar.set_ticklabels([str(h).zfill(2) if h % 2 == 0 else "" for h in range(24)])
    cbar.set_label('Hour of Day')

    # Plot lightning observations.
    #ax.scatter(lons, lats, transform=ccrs.PlateCarree(), cmap='gist_rainbow_r',
    ax.scatter(lons, lats, transform=ccrs.PlateCarree(), cmap='rainbow',               
               marker='x', s=6, c=time.dt.hour, vmin=0, vmax=23)

        # Plot area ploygons if required.
    if plot_fov:
        plot_li_fov_polygons(ax, projection=projection)
 
    return fig,ax
 
 
def plot_lmap_from_filenames(filenames, time_dataset_name, area_nswe=None, title=None, plot_fov=False):
    """
    Plot events/groups/flashes, coloured by hour of occurrence.
    Args:
      filenames = list of files to process
      time_dataset_name = string of time dataset in files
      area_nswe = 4-element list of North South West East limits for area plot
      title = string of plot title
      plot_fov = if True then plot the 4 LI camera field-of-views on the map.
    Returns:
      None, displays and/or saves the plot.
    """
   
    if area_nswe:
       area = Area(north=area_nswe[0], south=area_nswe[1], west=area_nswe[2], east=area_nswe[3])
    else:
       area = Area(85, -85, -85, 85)
        
    if not filenames:
       raise ValueError("No files found. Please check your file path.")
    else:    
        for n, filename in enumerate(filenames):
            scn = Scene([filename], reader="li_l2_nc")
            scn.load([time_dataset_name])
            (lons, lats) = scn[time_dataset_name].attrs['area'].get_lonlats()
            if n == 0:
                times_acc = scn[time_dataset_name].compute()
                lons_acc = xr.DataArray(lons).compute() 
                lats_acc = xr.DataArray(lats).compute() 
            else:
                times_acc = xr.concat([times_acc, scn[time_dataset_name].compute()], dim='y')
                lons_acc = np.concatenate([lons_acc, xr.DataArray(lons).compute() ]) 
                lats_acc = np.concatenate([lats_acc, xr.DataArray(lats).compute() ])

        fig,ax=plot_lmap(lats_acc, lons_acc, times_acc, area=area, title=title, plot_fov=plot_fov)

    return fig,ax

# Function to filter filenames within the given time range
def filter_filenames(filenames, start_dt, end_dt):
    filtered_files = []
    for fname in filenames:
        # Extract the start and end date fields using regex after '_OPE_'
        match = re.search(r'_OPE_(\d{14})_(\d{14})', fname)
        if match:
            # Extract the two date-time strings
            start_str, end_str = match.groups()

            # Convert them to datetime objects
            start_time = datetime.strptime(start_str[:12], "%Y%m%d%H%M")
            end_time = datetime.strptime(end_str[:12], "%Y%m%d%H%M")
            
            # Check if the file is within the desired time range
            
            
            if (start_dt <= start_time <= end_dt) and (start_dt <= end_time <= end_dt):
              
                #print('Filename:',start_time, ' - ', end_time)
                filtered_files.append(fname)
                
    
    return filtered_files




def time_bin_colours(times, bin_minutes=5, t_start=None):
    """
    Assigns a colour to each group according to which 5-minute time bin it
    falls into, matching the ESSL Weather Displayer 'Geometry and density'
    product, where LI group data is displayed in 5-minute bins and the
    flash geometry lines are coloured by bin (so that the time evolution of
    a storm is visible at a glance), rather than by flash identity. The
    palette uses muted earth tones (khaki, tan, dusty rose, mauve, olive,
    etc.), matching the reference product, and deliberately avoids the
    black-purple-red-orange-yellow-white spectrum used for the group
    density heatmap, so that the two layers stay visually distinct.
    Args:
      times = array-like of np.datetime64 group times.
      bin_minutes = width of each time bin, in minutes.
      t_start = reference time to anchor the bin calculation (e.g. the
        requested start_dt of the displayed window). If None, the minimum
        group time in the data is used, which can cause extra bins to appear
        if the data contains groups timestamped before the requested window.
    Returns:
      colours = (len(times), 4) array of RGBA colours, one per input time.
      bin_index = array of integer bin indices, one per input time.
    """

    palette = ['khaki', 'darkkhaki', 'tan', 'goldenrod', 'olive',
        'darkgoldenrod', 'burlywood', 'olivedrab']
    palette_rgba = np.array([mpl.colors.to_rgba(c) for c in palette])

    times = np.asarray(times, dtype='datetime64[ns]')
    t0 = np.datetime64(t_start, 'ns') if t_start is not None else times.min()
    minutes_since_start = (times - t0) / np.timedelta64(1, 'm')
    bin_index = np.floor(minutes_since_start / bin_minutes).astype(int)
    n_bins = int(np.ceil(10.0 / bin_minutes))  # max bins for a 10-min window
    bin_index = np.clip(bin_index, 0, n_bins - 1)

    colours = palette_rgba[bin_index % len(palette)]

    return colours, bin_index


def flash_geometry_segments(lats, lons, flash_ids, times, bin_minutes=2, t_start=None):
    """
    Computes the geometry of each LI flash as a minimum-spanning-tree (MST)
    connecting all the groups belonging to that flash. This reproduces the
    branching, dendritic-looking outline used in the ESSL Weather Displayer
    'Geometry and density' product (Groenemeijer/ESSL), where the line
    segments approximate the shape of the lightning channel as seen from
    space - as opposed to a filled convex hull, which over-simplifies the
    true (often elongated, branching) shape of a flash. Each segment is
    coloured according to the 5-minute time bin of its midpoint group time,
    matching the reference product (rather than colouring by flash
    identity).
    Args:
      lats, lons = arrays of group latitudes/longitudes (one value per group).
      flash_ids = array of flash_id values (one value per group), linking
        each group to its parent flash.
      times = array of np.datetime64 group times (one value per group).
      bin_minutes = width of each time bin, in minutes (default 2, giving 5
        bins across a 10-minute LGR chunk).
    Returns:
      segments = list of ((lon1, lat1), (lon2, lat2)) tuples, one per MST
        edge, across all flashes.
      colours = list of RGBA colours, one per entry in segments, set by the
        5-minute time bin of that segment.
    """

    from scipy.sparse.csgraph import minimum_spanning_tree
    from scipy.spatial.distance import pdist, squareform

    lats = np.asarray(lats)
    lons = np.asarray(lons)
    flash_ids = np.asarray(flash_ids)
    times = np.asarray(times, dtype='datetime64[ns]')

    group_colours, _ = time_bin_colours(times, bin_minutes=bin_minutes, t_start=t_start)

    segments = []
    colours = []
    for fid in np.unique(flash_ids):
        mask = flash_ids == fid
        flon = lons[mask]
        flat = lats[mask]
        fcolours = group_colours[mask]
        if len(flon) < 2:
            continue
        pts = np.column_stack([flon, flat])
        dist_matrix = squareform(pdist(pts))
        mst = minimum_spanning_tree(dist_matrix).tocoo()
        for i, j in zip(mst.row, mst.col):
            segments.append(((pts[i, 0], pts[i, 1]), (pts[j, 0], pts[j, 1])))
            # Colour the segment by the time bin of its earlier endpoint.
            colours.append(fcolours[i])

    return segments, colours


def group_density_grid(lats, lons, area_nswe, cell_km=1.0, min_count=2,
    smooth_km=2.5):
    """
    Computes the density of LI groups per square kilometre, on a regular
    grid, matching the 'groups per km^2' density product shown in the ESSL
    Weather Displayer 'Geometry and density' visualisation. The raw, binned
    counts are smoothed with a Gaussian filter, reproducing the diffuse,
    blurred-looking density blobs seen in the reference product (rather
    than sharp-edged individual grid cells).
    Args:
      lats, lons = arrays of group latitudes/longitudes.
      area_nswe = 4-element list of North South West East limits, in degrees,
        defining the grid extent.
      cell_km = grid cell size, in kilometres (approximate, using a local
        degrees-per-km conversion at the centre latitude of the area).
      min_count = minimum smoothed density required for a cell to be shown;
        cells below this are left empty (NaN) so the background remains
        visible.
      smooth_km = standard deviation of the Gaussian smoothing kernel, in
        kilometres. Set to 0 to disable smoothing and return raw counts.
    Returns:
      density = xarray DataArray of (smoothed) group counts per km^2, with
        latitude and longitude coordinates, NaN where there are no groups
        (so the background image remains visible through those cells when
        plotted).
    """

    from scipy.ndimage import gaussian_filter

    north, south, west, east = area_nswe
    lat0 = (north + south) / 2.0
    km_per_deg_lat = 111.0
    km_per_deg_lon = 111.0 * np.cos(np.radians(lat0))
    dlat = cell_km / km_per_deg_lat
    dlon = cell_km / km_per_deg_lon

    lat_bins = np.arange(south, north + dlat, dlat)
    lon_bins = np.arange(west, east + dlon, dlon)

    counts, _, _ = np.histogram2d(lons, lats, bins=[lon_bins, lat_bins])
    counts = counts.T  # rows = latitude, cols = longitude

    if smooth_km > 0:
        sigma_cells = smooth_km / cell_km
        counts = gaussian_filter(counts, sigma=sigma_cells)

    density = xr.DataArray(counts, coords=[lat_bins[:-1] + dlat / 2,
        lon_bins[:-1] + dlon / 2], dims=['latitude', 'longitude'])
    density = density.where(density >= min_count)

    return density


def density_colormap():
    """
    Builds the discrete 'groups per km^2' colour scale used in the ESSL
    Weather Displayer 'Geometry and density' product: black-purple-red-
    orange-yellow-white, with bin edges at 1, 2, 4, 8, 16, 32, 64 (log2
    scale).
    Returns:
      cmap, norm = matplotlib ListedColormap and BoundaryNorm objects, ready
        to use with pcolormesh/imshow/contourf.
    """

    colours = ['black', 'indigo', 'magenta', 'red', 'orangered', 'gold', 'white']
    bounds = [1, 2, 4, 8, 16, 32, 64, 1e6]
    cmap = mpl.colors.ListedColormap(colours)
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    return cmap, norm


def plot_flash_geometry_density(lats, lons, flash_ids, times, area_nswe,
    cell_km=1.0, smooth_km=2.5, bin_minutes=2, t_start=None, gridlines=True,
    plot_fov=False, title=None, background_ax=None):
    """
    Plot LI flash geometry (MST of groups per flash) together with LI group
    density (groups per km^2, discrete log2 colour scale), reproducing the
    ESSL Weather Displayer 'Geometry and density' product (see
    plot_flash_geometry_density_on_ir to add a satellite IR background).
    Args:
      lats, lons = arrays of group latitudes/longitudes.
      flash_ids = array of flash_id values (one value per group).
      times = array of np.datetime64 group times (one value per group),
        used to colour the flash geometry lines by time bin.
      area_nswe = 4-element list of North South West East limits, in degrees.
      cell_km = density grid cell size in kilometres.
      smooth_km = standard deviation of the Gaussian smoothing kernel
        applied to the density grid, in kilometres, giving the diffuse,
        blurred-blob look of the reference product (set to 0 to disable).
      bin_minutes = width of each time bin used to colour the flash
        geometry lines, in minutes (default 2).
      gridlines = if True then plot map gridlines.
      plot_fov = if True then plot the 4 LI camera field-of-views on the map.
      title = plot title str.
      background_ax = an existing cartopy axis to plot onto (e.g. one
        already showing an IR background); if None, a new figure/axis with
        a plain map is created.
    Returns:
      fig, ax = the matplotlib figure and axis objects of the plot.
    """

    area = Area(north=area_nswe[0], south=area_nswe[1], west=area_nswe[2], east=area_nswe[3])

    if background_ax is None:
        fig, ax = plt.subplots(subplot_kw=({'projection': ccrs.PlateCarree()}))
        format_fig_size(fig, area)
        ax = plotmap(ax, gridlines=gridlines, area=area)
    else:
        fig = background_ax.figure
        ax = background_ax

    if title is not None:
        ax.set_title(title)

    # Group density heatmap, smoothed and contoured for a diffuse,
    # blurred-blob look matching the reference product.
    density = group_density_grid(lats, lons, area_nswe, cell_km=cell_km,
        smooth_km=smooth_km)
    cmap, norm = density_colormap()
    levels = [1, 2, 4, 8, 16, 32, 64, max(float(density.max()), 65)]
    mesh = density.fillna(0).plot.contourf(ax=ax, x='longitude', y='latitude',
        transform=ccrs.PlateCarree(), cmap=cmap, norm=norm, levels=levels,
        add_colorbar=False, add_labels=False, zorder=3, extend='neither')
    cbar = fig.colorbar(mesh, ax=ax, ticks=[1, 2, 4, 8, 16, 32, 64])
    cbar.set_label('groups per km$^2$')
    if title is not None:
        ax.set_title(title)

    # Flash geometry (MST per flash), coloured by time bin.
    segments, colours = flash_geometry_segments(lats, lons, flash_ids, times,
        bin_minutes=bin_minutes, t_start=t_start)
    lc = mpl.collections.LineCollection(segments, colors=colours,
        linewidths=1.6, transform=ccrs.PlateCarree(), zorder=2)
    ax.add_collection(lc)

    # Time-bin colour legend — placed outside the plot to the right.
    _, bin_index = time_bin_colours(times, bin_minutes=bin_minutes, t_start=t_start)
    palette = ['khaki', 'darkkhaki', 'tan', 'goldenrod', 'olive',
        'darkgoldenrod', 'burlywood', 'olivedrab']
    legend_handles = []
    for b in sorted(np.unique(bin_index)):
        label = '%d–%d min' % (b * bin_minutes, (b + 1) * bin_minutes)
        colour = mpl.colors.to_rgba(palette[b % len(palette)])
        legend_handles.append(mpl.lines.Line2D([0], [0], color=colour,
            linewidth=2.5, label=label))
    ax.legend(handles=legend_handles, title='Flash geometry\ntime bin',
        loc='upper left', bbox_to_anchor=(1.18, 1.0),
        fontsize=8, title_fontsize=8,
        framealpha=0.9, fancybox=False)

    if plot_fov:
        plot_li_fov_polygons(ax, projection=ccrs.PlateCarree())

    return fig, ax


def plot_ir_background(ax, fci_filenames, area_nswe, channel='ir_105',
    width=1500, height=1500, border_colour='darkred'):
    """
    Loads an FCI channel or composite, resamples it to area_nswe, and plots
    it as the background of an existing cartopy map axis, with coastlines
    and country borders on top. Single-band channels (e.g. 'ir_105',
    'ir_38', 'wv_63') are plotted as inverted grayscale brightness
    temperature (cold cloud tops = bright/white, warm surface = dark),
    matching the satellite IR background used in the ESSL Weather Displayer
    'Geometry and density' product. Multi-band composites (e.g.
    'true_color', 'cloud_phase', 'natural_color') are plotted as their
    normal enhanced RGB image instead.
    Args:
      ax = matplotlib/cartopy axis to plot the background on (must already
        be set to the same area_nswe extent, e.g. via plotmap).
      fci_filenames = list of FCI L1c BODY chunk files covering area_nswe.
      area_nswe = 4-element list of North South West East limits, in degrees.
      channel = name of the FCI channel or composite to load, e.g. 'ir_105'
        (default), 'ir_38', 'wv_63', 'true_color', 'cloud_phase', etc.
      width, height = number of pixels of the resampled background grid.
      border_colour = colour of the coastline and country border overlay.
    Returns:
      ax = input axis, with the background image, coastlines and borders
        plotted.
    """

    from satpy.writers import get_enhanced_image

    area_def = area_def_from_nswe(area_nswe, width=width, height=height)

    scn = Scene(reader='fci_l1c_nc', filenames=fci_filenames)
    scn.load([channel])
    resampled_scn = scn.resample(area_def, resampler='nearest')

    data = resampled_scn[channel].compute()
    north, south, west, east = area_nswe

    if 'bands' in data.dims and data.sizes['bands'] > 1:
        # Multi-band composite (RGB or palettized output, e.g. 'true_color'
        # or 'cloud_phase') - use satpy's own enhancement/colour handling
        # and plot as a normal image.
        img = get_enhanced_image(resampled_scn[channel]).data
        img = img.transpose('y', 'x', 'bands')
        ax.imshow(img.values, extent=(west, east, south, north), origin='upper',
            transform=ccrs.PlateCarree(), zorder=1)
    else:
        # Single-band channel (e.g. a plain IR/VIS/WV channel) - plot as
        # inverted grayscale brightness temperature/reflectance.
        values = data.values
        if values.ndim == 3:
            values = values[0]
        ax.imshow(values, extent=(west, east, south, north), origin='upper',
            transform=ccrs.PlateCarree(), cmap='gray_r', zorder=1)

    ax.add_feature(cartopy.feature.COASTLINE, edgecolor=border_colour, lw=1, zorder=2)
    ax.add_feature(cartopy.feature.BORDERS, edgecolor=border_colour, lw=1, zorder=2)

    return ax


def check_lgr_filenames(filenames):
    """
    Raise a ValueError if any of the files is not an LI-2-LGR product, since
    flash_id and group_time are only present in LGR files.
    Args:
      filenames = list of file paths.
    """
    not_lgr = [f for f in filenames if 'LI-2-LGR' not in os.path.basename(f)]
    if not_lgr:
        raise ValueError("Only LI-2-LGR files can be used here, but got %d other "
            "file(s), e.g. %s. Please narrow your file path to LGR files."
            % (len(not_lgr), os.path.basename(not_lgr[0])))


def plot_flash_geometry_density_from_filenames(filenames, area_nswe, cell_km=1.0,
    smooth_km=2.5, bin_minutes=2, t_start=None, title=None, plot_fov=False):
    """
    Plot LI flash geometry (MST of groups per flash, coloured by time bin)
    together with LI group density (groups per km^2), reading group/flash/
    time data straight from LI-2-LGR product file(s), without any satellite
    background (see plot_flash_geometry_density_on_ir to add one).
    Args:
      filenames = list of LI-2-LGR BODY files to process.
      area_nswe = 4-element list of North South West East limits, in degrees.
      cell_km = density grid cell size in kilometres.
      smooth_km = standard deviation of the Gaussian smoothing kernel
        applied to the density grid, in kilometres.
      bin_minutes = width of each time bin used to colour the flash
        geometry lines, in minutes.
      t_start = reference datetime to anchor the time bins (e.g. start_dt
        of the displayed window). If None, the earliest group time in the
        data is used, which may cause spurious extra bins if the files
        contain groups slightly before the requested window.
      title = string of plot title.
      plot_fov = if True then plot the 4 LI camera field-of-views on the map.
    Returns:
      fig, ax = the matplotlib figure and axis objects of the plot.
    """

    if not filenames:
        raise ValueError("No files found. Please check your file path.")
    check_lgr_filenames(filenames)

    for n, filename in enumerate(filenames):
        scn = Scene([filename], reader="li_l2_nc")
        scn.load(['latitude', 'longitude', 'flash_id', 'group_time'])
        lats_n = scn['latitude'].compute().values
        lons_n = scn['longitude'].compute().values
        flash_ids_n = scn['flash_id'].compute().values
        times_n = scn['group_time'].compute().values

        if n == 0:
            lats_acc = lats_n
            lons_acc = lons_n
            flash_ids_acc = flash_ids_n
            times_acc = times_n
        else:
            lats_acc = np.concatenate([lats_acc, lats_n])
            lons_acc = np.concatenate([lons_acc, lons_n])
            flash_ids_acc = np.concatenate([flash_ids_acc, flash_ids_n])
            times_acc = np.concatenate([times_acc, times_n])

    fig, ax = plot_flash_geometry_density(lats_acc, lons_acc, flash_ids_acc,
        times_acc, area_nswe, cell_km=cell_km, smooth_km=smooth_km,
        bin_minutes=bin_minutes, t_start=t_start, title=title, plot_fov=plot_fov)

    return fig, ax


def plot_flash_geometry_density_on_ir(lgr_filenames, fci_filenames, area_nswe,
    channel='ir_105', title=None, plot_fov=False, cell_km=1.0,
    t_start=None, fci_width=1500, fci_height=1500):
    """
    Reproduces the ESSL Weather Displayer 'Geometry and density' product:
    LI flash geometry (MST of groups per flash) and LI group density
    (groups per km^2) plotted together on top of an FCI background (single
    IR/VIS/WV channel as inverted grayscale, or a multi-band composite as a
    normal RGB image), with coastlines and country borders.
    Args:
      lgr_filenames = list of LI-2-LGR BODY files covering area_nswe.
      fci_filenames = list of FCI L1c BODY chunk files covering area_nswe.
      area_nswe = 4-element list of North South West East limits, in degrees.
      channel = name of the FCI channel or composite to use as background,
        e.g. 'ir_105' (default), 'ir_38', 'wv_63', 'true_color',
        'cloud_phase', etc.
      title = plot title str.
      plot_fov = if True then plot the 4 LI camera field-of-views on the map.
      cell_km = density grid cell size in kilometres.
      t_start = reference datetime to anchor the time bins (e.g. start_dt
        of the displayed window). If None, the earliest group time in the
        data is used, which may cause spurious extra bins if the files
        contain groups slightly before the requested window.
      fci_width, fci_height = number of pixels of the resampled background.
    Returns:
      fig, ax = the matplotlib figure and axis objects of the plot.
    """

    if not lgr_filenames:
        raise ValueError("No LI-2-LGR files found. Please check your file path.")
    check_lgr_filenames(lgr_filenames)
    if not fci_filenames:
        raise ValueError("No FCI files found. Please check your file path.")

    area = Area(north=area_nswe[0], south=area_nswe[1], west=area_nswe[2], east=area_nswe[3])

    fig, ax = plt.subplots(subplot_kw=({'projection': ccrs.PlateCarree()}))
    format_fig_size(fig, area)
    ax.set_xlim(area.west, area.east)
    ax.set_ylim(area.south, area.north)
    if title is not None:
        ax.set_title(title)

    plot_ir_background(ax, fci_filenames, area_nswe, channel=channel,
        width=fci_width, height=fci_height)

    for n, filename in enumerate(lgr_filenames):
        scn = Scene([filename], reader="li_l2_nc")
        scn.load(['latitude', 'longitude', 'flash_id', 'group_time'])
        lats_n = scn['latitude'].compute().values
        lons_n = scn['longitude'].compute().values
        flash_ids_n = scn['flash_id'].compute().values
        times_n = scn['group_time'].compute().values

        if n == 0:
            lats_acc = lats_n
            lons_acc = lons_n
            flash_ids_acc = flash_ids_n
            times_acc = times_n
        else:
            lats_acc = np.concatenate([lats_acc, lats_n])
            lons_acc = np.concatenate([lons_acc, lons_n])
            flash_ids_acc = np.concatenate([flash_ids_acc, flash_ids_n])
            times_acc = np.concatenate([times_acc, times_n])

    plot_flash_geometry_density(lats_acc, lons_acc, flash_ids_acc, times_acc,
        area_nswe, cell_km=cell_km, plot_fov=plot_fov, t_start=t_start,
        background_ax=ax)

    return fig, ax


def plot_flash_timeseries(filenames, product_type='flash', bin_minutes=1,
    area_nswe=None, title=None, fname=None):
    """
    Count LI detections (flashes, groups, or events) per time bin and plot
    the resulting time series curve, following the approach used in LI-STAR
    (S.-E. Enno, EUMETSAT): simply count all observations per time unit and
    plot the curve. The plot acts both as a visualisation of the diurnal
    cycle of lightning activity and as a data completeness / sanity check —
    any gap in the local dataset appears immediately as a drop in the curve.
    Args:
      filenames = list of LI Level 2 BODY files to process (LFL, LGR, or LE).
      product_type = one of 'flash', 'group', or 'event', controlling which
        time variable is read: 'flash_time' for LFL, 'group_time' for LGR,
        'event_time' for LE.
      bin_minutes = width of each time bin in minutes (default 1).
      area_nswe = optional 4-element list of North South West East limits,
        in degrees. If provided, only detections within the bounding box are
        counted.
      title = plot title string.
      fname = output file path. If provided, the plot is saved to this path.
    Returns:
      fig, ax = the matplotlib figure and axis objects of the plot.
    """

    time_var = {'flash': 'flash_time', 'group': 'group_time',
        'event': 'event_time'}.get(product_type, 'flash_time')
    lat_var  = 'latitude'
    lon_var  = 'longitude'

    if not filenames:
        raise ValueError("No files found. Please check your file path.")

    times_all = []
    for n, filename in enumerate(filenames):
        scn = Scene([filename], reader="li_l2_nc")
        datasets = [time_var]
        if area_nswe is not None:
            datasets += [lat_var, lon_var]
        scn.load(datasets)
        times_n = scn[time_var].compute().values

        if area_nswe is not None:
            lats_n = scn[lat_var].compute().values
            lons_n = scn[lon_var].compute().values
            north, south, west, east = area_nswe
            mask = ((lats_n >= south) & (lats_n <= north) &
                    (lons_n >= west) & (lons_n <= east))
            times_n = times_n[mask]

        times_all.append(times_n)

    times_all = np.concatenate(times_all).astype('datetime64[ns]')

    if times_all.size == 0:
        raise ValueError("No detections found in the provided files/area.")

    t0 = times_all.min().astype('datetime64[m]')
    t1 = times_all.max().astype('datetime64[m]')
    bin_edges = np.arange(t0, t1 + np.timedelta64(bin_minutes + 1, 'm'),
        np.timedelta64(bin_minutes, 'm')).astype('datetime64[ns]')

    counts, _ = np.histogram(times_all.astype(np.int64),
        bins=bin_edges.astype(np.int64))
    bin_centres = (bin_edges[:-1].astype('datetime64[m]').astype(object))

    import matplotlib.dates as mdates
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(bin_centres, counts, color='steelblue', linewidth=0.8)
    ax.set_xlabel('Time UTC')
    ax.set_ylabel('Flash count' if product_type == 'flash' else
        'Group count' if product_type == 'group' else 'Event count')
    ax.set_ylim(bottom=0)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))
    plt.xticks(rotation=45, ha='right')
    if title is not None:
        ax.set_title(title)
    fig.tight_layout()

    if fname:
        fig.savefig(fname, dpi=150, bbox_inches='tight')
        print('Saved plot as', fname)

    return fig, ax



    """
    Assigns a distinct, repeatable colour to each unique flash, following the
    same approach as the ESSL Weather Displayer 'Geometry and density'
    visualisation (each flash given a different colour).
    Args:
      flash_ids = array-like of flash_id values (one per group).
    Returns:
      colour_map = dict mapping each unique flash_id to an RGBA colour.
    """

    unique_flashes = np.unique(flash_ids)
    cmap = plt.get_cmap('tab20', max(len(unique_flashes), 1))
    colour_map = {fid: cmap(i % 20) for i, fid in enumerate(unique_flashes)}

    return colour_map


def plot_flash_geometry(lats, lons, flash_ids, projection=ccrs.PlateCarree(),
    gridlines=True, area=None, area_nswe=None, plot_fov=False, title=None,
    min_points_for_hull=3):
    """
    Plot the geometry of LI flashes, i.e. connect all the LI groups that
    belong to the same flash, following the same logic as the ESSL Weather
    Displayer 'Geometry and density' product: LI groups (connected pixel
    detections within one 1 ms acquisition frame) that are correlated in
    space and time within 330 ms form a single LI flash, and the outline
    that connects them is a proxy for the geometry of the flash, as seen
    from space. Each flash is plotted with a different colour.
    Args:
      lats, lons = arrays of group latitudes/longitudes (one value per group).
      flash_ids = array of flash_id values (one value per group), linking
        each group to its parent flash.
      projection = map projection.
      gridlines = if True then plot map gridlines.
      area = an area class object defining the map extent in space.
      area_nswe = 4-element list of North South West East limits for area plot.
      plot_fov = if True then plot the 4 LI camera field-of-views on the map.
      title = plot title str.
      min_points_for_hull = minimum number of groups in a flash required to
        draw a filled convex-hull polygon; flashes with fewer groups are
        drawn as a line (2 groups) or a single marker (1 group).
    Returns:
      fig, ax = the matplotlib figure and axis objects of the plot.
    """

    if area_nswe is not None:
        area = Area(north=area_nswe[0], south=area_nswe[1], west=area_nswe[2], east=area_nswe[3])

    # Create the figure, plot background map and title.
    fig, ax = plt.subplots(subplot_kw=({'projection': projection}))
    format_fig_size(fig, area)
    ax = plotmap(ax, gridlines=gridlines, area=area)
    if title is not None:
        ax.set_title(title)

    lats = np.asarray(lats)
    lons = np.asarray(lons)
    flash_ids = np.asarray(flash_ids)

    colour_map = _flash_colours(flash_ids)

    # Connect the groups belonging to each flash.
    for fid in np.unique(flash_ids):
        mask = flash_ids == fid
        flash_lons = lons[mask]
        flash_lats = lats[mask]
        colour = colour_map[fid]

        points = np.column_stack([flash_lons, flash_lats])

        if len(points) >= min_points_for_hull:
            try:
                from scipy.spatial import ConvexHull
                hull = ConvexHull(points)
                hull_points = points[hull.vertices]
                polygon = mpl.patches.Polygon(hull_points, closed=True,
                    facecolor=colour, edgecolor=colour, alpha=0.4, lw=1.2,
                    transform=ccrs.PlateCarree())
                ax.add_patch(polygon)
            except Exception:
                # Fall back to a simple connecting line if the hull cannot
                # be computed (e.g. collinear points).
                ax.plot(flash_lons, flash_lats, '-', color=colour, lw=1,
                    transform=ccrs.PlateCarree())
        elif len(points) == 2:
            ax.plot(flash_lons, flash_lats, '-', color=colour, lw=1.5,
                transform=ccrs.PlateCarree())

        # Always mark the individual groups too.
        ax.scatter(flash_lons, flash_lats, color=colour, marker='.', s=10,
            transform=ccrs.PlateCarree())

    # Plot area polygons if required.
    if plot_fov:
        plot_li_fov_polygons(ax, projection=projection)

    return fig, ax


def plot_flash_geometry_from_filenames(filenames, area_nswe=None, title=None,
    plot_fov=False):
    """
    Plot the geometry of LI flashes, reading group/flash data straight from
    LI-2-LGR product file(s).
    Args:
      filenames = list of LI-2-LGR BODY files to process.
      area_nswe = 4-element list of North South West East limits for area plot.
      title = string of plot title.
      plot_fov = if True then plot the 4 LI camera field-of-views on the map.
    Returns:
      fig, ax = the matplotlib figure and axis objects of the plot.
    """

    if not filenames:
        raise ValueError("No files found. Please check your file path.")

    for n, filename in enumerate(filenames):
        scn = Scene([filename], reader="li_l2_nc")
        scn.load(['latitude', 'longitude', 'flash_id'])
        lats_n = scn['latitude'].compute().values
        lons_n = scn['longitude'].compute().values
        flash_ids_n = scn['flash_id'].compute().values

        if n == 0:
            lats_acc = lats_n
            lons_acc = lons_n
            flash_ids_acc = flash_ids_n
        else:
            lats_acc = np.concatenate([lats_acc, lats_n])
            lons_acc = np.concatenate([lons_acc, lons_n])
            flash_ids_acc = np.concatenate([flash_ids_acc, flash_ids_n])

    fig, ax = plot_flash_geometry(lats_acc, lons_acc, flash_ids_acc,
        area_nswe=area_nswe, title=title, plot_fov=plot_fov)

    return fig, ax


def area_def_from_nswe(area_nswe, width=1500, height=1500, area_id='roi'):
    """
    Builds a pyresample AreaDefinition (equirectangular, lat/lon) from a
    North-South-West-East bounding box, in the same area_nswe format used
    throughout this notebook collection.
    Args:
      area_nswe = 4-element list of North South West East limits, in degrees.
      width, height = number of pixels of the resampled grid.
      area_id = identifier string for the area definition.
    Returns:
      area_def = pyresample AreaDefinition object covering the requested area.
    """

    from pyresample import create_area_def

    north, south, west, east = area_nswe
    area_def = create_area_def(area_id,
        {'proj': 'eqc', 'lat_ts': 0, 'lat_0': 0, 'lon_0': 0},
        area_extent=(west, south, east, north), units='degrees',
        width=width, height=height)

    return area_def


def plot_fci_background(ax, fci_filenames, composite='true_color',
    area_nswe=None, width=1500, height=1500):
    """
    Loads and resamples an FCI composite and plots it as the background of
    an existing cartopy map axis, so that LI flash geometry can be plotted
    on top of it.
    Args:
      ax = matplotlib/cartopy axis to plot the background on (must already
        be set to the same area_nswe extent, e.g. via plotmap).
      fci_filenames = list of FCI L1c BODY chunk files covering area_nswe.
      composite = name of the FCI composite to load (e.g. 'true_color').
      area_nswe = 4-element list of North South West East limits, in degrees.
      width, height = number of pixels of the resampled background grid.
    Returns:
      ax = input axis, with the FCI background image plotted on it.
    """

    from satpy.writers import get_enhanced_image

    if area_nswe is None:
        raise ValueError("area_nswe must be provided to resample the FCI background.")

    area_def = area_def_from_nswe(area_nswe, width=width, height=height)

    fci_scn = Scene(reader='fci_l1c_nc', filenames=fci_filenames)
    fci_scn.load([composite])
    resampled_scn = fci_scn.resample(area_def, resampler='nearest')

    img = get_enhanced_image(resampled_scn[composite]).data
    img = img.transpose('y', 'x', 'bands')

    north, south, west, east = area_nswe
    ax.imshow(img.values, extent=(west, east, south, north), origin='upper',
        transform=ccrs.PlateCarree())

    return ax


def plot_flash_geometry_on_fci(lgr_filenames, fci_filenames, area_nswe,
    fci_composite='true_color', title=None, plot_fov=False,
    fci_width=1500, fci_height=1500):
    """
    Plot the geometry of LI flashes (LI-2-LGR groups connected per flash, as
    in plot_flash_geometry) on top of an FCI background composite, mirroring
    the ESSL Weather Displayer 'Geometry and density' visualisation, which
    combines LI flash geometry with imagery of the underlying convective
    cells.
    Args:
      lgr_filenames = list of LI-2-LGR BODY files covering area_nswe.
      fci_filenames = list of FCI L1c BODY chunk files covering area_nswe.
      area_nswe = 4-element list of North South West East limits, in degrees.
      fci_composite = name of the FCI composite to use as background.
      title = plot title str.
      plot_fov = if True then plot the 4 LI camera field-of-views on the map.
      fci_width, fci_height = number of pixels of the resampled FCI background.
    Returns:
      fig, ax = the matplotlib figure and axis objects of the plot.
    """

    if not lgr_filenames:
        raise ValueError("No LI-2-LGR files found. Please check your file path.")
    check_lgr_filenames(lgr_filenames)
    if not fci_filenames:
        raise ValueError("No FCI files found. Please check your file path.")

    area = Area(north=area_nswe[0], south=area_nswe[1], west=area_nswe[2], east=area_nswe[3])

    # Create the figure and map first, so the FCI background can be plotted
    # on it before the flash geometry is drawn on top.
    fig, ax = plt.subplots(subplot_kw=({'projection': ccrs.PlateCarree()}))
    format_fig_size(fig, area)
    ax = plotmap(ax, gridlines=True, area=area)
    if title is not None:
        ax.set_title(title)

    plot_fci_background(ax, fci_filenames, composite=fci_composite,
        area_nswe=area_nswe, width=fci_width, height=fci_height)

    # Load the LI groups and overlay the flash geometry.
    for n, filename in enumerate(lgr_filenames):
        scn = Scene([filename], reader="li_l2_nc")
        scn.load(['latitude', 'longitude', 'flash_id'])
        lats_n = scn['latitude'].compute().values
        lons_n = scn['longitude'].compute().values
        flash_ids_n = scn['flash_id'].compute().values

        if n == 0:
            lats_acc = lats_n
            lons_acc = lons_n
            flash_ids_acc = flash_ids_n
        else:
            lats_acc = np.concatenate([lats_acc, lats_n])
            lons_acc = np.concatenate([lons_acc, lons_n])
            flash_ids_acc = np.concatenate([flash_ids_acc, flash_ids_n])

    lats_acc = np.asarray(lats_acc)
    lons_acc = np.asarray(lons_acc)
    flash_ids_acc = np.asarray(flash_ids_acc)
    colour_map = _flash_colours(flash_ids_acc)

    for fid in np.unique(flash_ids_acc):
        mask = flash_ids_acc == fid
        flash_lons = lons_acc[mask]
        flash_lats = lats_acc[mask]
        colour = colour_map[fid]
        points = np.column_stack([flash_lons, flash_lats])

        if len(points) >= 3:
            try:
                from scipy.spatial import ConvexHull
                hull = ConvexHull(points)
                hull_points = points[hull.vertices]
                polygon = mpl.patches.Polygon(hull_points, closed=True,
                    facecolor=colour, edgecolor=colour, alpha=0.45, lw=1.4,
                    transform=ccrs.PlateCarree())
                ax.add_patch(polygon)
            except Exception:
                ax.plot(flash_lons, flash_lats, '-', color=colour, lw=1.2,
                    transform=ccrs.PlateCarree())
        elif len(points) == 2:
            ax.plot(flash_lons, flash_lats, '-', color=colour, lw=1.8,
                transform=ccrs.PlateCarree())

        ax.scatter(flash_lons, flash_lats, color=colour, marker='.', s=12,
            transform=ccrs.PlateCarree())

    if plot_fov:
        plot_li_fov_polygons(ax, projection=ccrs.PlateCarree())

    return fig, ax


if __name__ == '__main__':

    plot_lmap_from_filenames(filenames, area_nswe, time_dataset_name, title, output_filename)
