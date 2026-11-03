# In this file we deffine utility functions for reading healp with data in yupyter notebook

import h5py as h5
import pandas as pd
import numpy as np
import os
from scipy.ndimage import zoom
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from datetime import datetime


def readFRP_list(path, *arguments, group=False):
    """This function read FRP-list data from LSA-SAF into the dataframe
    https://nextcloud.lsasvcs.ipma.pt/s/pnDEepeq8zqRyrq
    path: directory path to hdf5 file
    arguments: FRP,FRP_UNCERTAINTY,LATITUDE,LONGITUDE ,FIRE_CONFIDENCE,PIXEL_SIZE,ABS_PIXEL,
    group: [true/false], if true it itterates over the hdf5 dataset and print all groups and arguments
    ABS_LINEnpr
    """
    if group:
        try:
            f = h5.File(path, "r")
            print("keys of a file", list(f.keys()))
            for key in list(f.keys()):
                try:
                    print("key in array", key)
                    print("attributes in subset", f[key].attrs.keys())
                except Exception as e:
                    print("something went wrong in this situations")
            for key in f.attrs.keys():
                try:
                    print("atribut: ", key)
                    print(f.attrs[key])
                except:
                    print("Can not print attribute")
        except Exception as e:
            print(e)
            print("Something wennt wrong")
    fire_df = {}
    # iterate over arguments and prepare dict for dataframe
    for i in arguments:
        if len(fire_df) == 0:
            try:
                # image acq time  is in byte clas b'202208221200' use method .decode() to convert and then str()
                f = h5.File(path, "r")
                time_string = str(f.attrs["IMAGE_ACQUISITION_TIME"].decode())
                time_stamp = datetime.strptime(time_string, "%Y%m%d%H%M%S")
                fire_df["TIME"] = time_stamp
            except Exception as e:
                print(e)
                print("failed to read ACQUISITION_TIME")
        try:
            f = h5.File(path, "r")
            fire_df[i] = f[i][:] / f[i].attrs["SCALING_FACTOR"]
            print("argument", i)
            print(
                "scaling factor: ",
                f[i].attrs["SCALING_FACTOR"],
                "Units:",
                f[i].attrs["UNITS"],
            )
        except Exception as e:
            print("failed to read: ", i)
            print("failed to read: ", e)
    dframe = pd.DataFrame(fire_df)
    return dframe


##


def check_for_dir(dir_path: str):
    dir_path_abs = os.path.abspath(dir_path)
    if not os.path.exists(dir_path_abs):
        os.makedirs(dir_path_abs)
    return dir_path_abs


def shift_grid(arr):
    dense_grid = zoom(arr, zoom=2, order=1)
    return dense_grid[1::2, 1::2]


def get_region(arr, start, stop):
    return arr[start:stop, start:stop]


def find_max_daily_frp(df, fire_conf_thr=0.90):
    df = df.copy()
    df["TIME"] = pd.to_datetime(df["TIME"])
    df = df.loc[df["FIRE_CONFIDENCE"] > fire_conf_thr]
    df.loc[:, "DATE"] = df["TIME"].dt.floor("D")
    # aggregate by location
    df = df.groupby(
        ["DATE", "LATITUDE", "LONGITUDE", "geometry"],
        as_index=False,
    ).agg({"FRP": "max"})
    df = df.sort_values(by=["DATE", "FRP"], ascending=[True, False]).reset_index(drop=True)
    return df


def define_legend(ax, generation: str, plot_burned_area: bool, plt_title=True):
    # Add legend

    handles = []

    if generation == "MSG":
        handles.append(Line2D([0], [0], color="blue", alpha=0.7, lw=0.4, label="MSG Grid"))
    if generation == "MTG":
        handles.append(Line2D([0], [0], color="red", alpha=0.7, lw=0.4, label="MTG Grid"))
    if plot_burned_area:
        handles.append(
            mpatches.Patch(facecolor="black", edgecolor="black", alpha=0.8, label="Burned Area")
        )

    # Title text
    parts = []
    if generation == "MSG":
        parts.append("MSG grid")
    if generation == "MTG":
        parts.append("MTG grid")
    if plot_burned_area:
        parts.append("Burned area from Copernicus")

    if plt_title:
        plt_text = "FRP values, " + ", ".join(parts) if parts else "No data to display"
        ax.set_title(plt_text, fontsize=18)

    # Add gridlines with labels
    gl = ax.gridlines(
        draw_labels=True,
        linewidth=0.4,
        color="gray",
        alpha=0.7,
        linestyle="--",
    )
    gl.top_labels = False  # remove labels on top
    gl.right_labels = False  # remove labels on right
    gl.xlabel_style = {"size": 11, "color": "black"}
    gl.ylabel_style = {"size": 11, "color": "black"}

    if handles:
        ax.legend(handles=handles, loc="upper center")

    return ax


def plot_lsasaf_grid(
    generation: str,
    CHOOSEN_PROJECTION,
    lon_array,
    lat_array,
    frp_df,
    area_of_interest,
    fig,
    ax,
    cmap,
    vmin=0,
    vmax=1000,
    plot_FRP=True,
    plot_specific_date=None,
    plot_max_all_days=False,
):
    color = "red" if generation == "MTG" else "blue"

    if not plot_FRP:
        ax.pcolormesh(
            lon_array,
            lat_array,
            np.full_like(lat_array, np.nan, dtype=float)[:-1, :-1],  # shape one less
            cmap=cmap,  # only plot the mesh
            transform=CHOOSEN_PROJECTION,
            alpha=0.7,  # transparency
            edgecolors=color,
            linewidth=1.7,
            shading="flat",
            zorder=1,
        )
        # save_path = check_for_dir(os.path.join(area_of_interest, "plots"))
        # plt.savefig(os.path.join(save_path, f"{area_of_interest}_fire_mesh_{generation}"), dpi=100)
        plt.show()

        return

    # Compute approximate cell centers
    cell_lon = 0.25 * (
        lon_array[:-1, :-1] + lon_array[:-1, 1:] + lon_array[1:, :-1] + lon_array[1:, 1:]
    )
    cell_lat = 0.25 * (
        lat_array[:-1, :-1] + lat_array[:-1, 1:] + lat_array[1:, :-1] + lat_array[1:, 1:]
    )

    if plot_max_all_days:
        min_date = str(frp_df["DATE"].min().date())
        max_date = str(frp_df["DATE"].max().date())
        frp_df = frp_df.groupby(["LATITUDE", "LONGITUDE", "geometry"], as_index=False).agg(
            {"FRP": "max"}
        )
        frp_df.loc[:, "DATE"] = f"{min_date} - {max_date}"
        frp_df = frp_df.sort_values(
            by=["FRP"],
            ascending=[False],
        ).reset_index(drop=True)

    frp_dates = frp_df["DATE"].unique()

    # before loop: persistent base figure/axes already created
    pcm = None
    cbar = None
    # Find in which cell each FRP pixel falls (for each day a seperate plot)
    frp_dates = [plot_specific_date] if plot_specific_date else frp_dates
    for d in frp_dates:
        mask = frp_df["DATE"] == d
        frp_msg_d = frp_df.loc[mask].copy()
        fire_grid = np.full(cell_lon.shape, np.nan, dtype=float)

        for i in range(0, len(frp_msg_d)):
            i_lat = frp_msg_d.iloc[i]["LATITUDE"]
            i_lon = frp_msg_d.iloc[i]["LONGITUDE"]
            i_frp = frp_msg_d.iloc[i]["FRP"]

            dist = np.sqrt(((cell_lon - i_lon) ** 2) + ((cell_lat - i_lat) ** 2))
            iy, ix = np.where(dist == dist.min())
            fire_grid[iy, ix] = i_frp

        # Plot the grid (and FRP pixels)
        new_pcm = ax.pcolormesh(
            lon_array,
            lat_array,
            fire_grid,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            alpha=0.8,
            linewidth=0.4,
            edgecolors=color,
            transform=CHOOSEN_PROJECTION,
            shading="flat",
            zorder=2,
        )

        if cbar is None:
            # TODO
            # create colorbar once
            label = "FRP max daily value [MW]" if not plot_max_all_days else "FRP max value [MW]"
            cbar = fig.colorbar(
                new_pcm, ax=ax, orientation="vertical", alpha=0.8, shrink=0.8, pad=0.05
            )
            cbar.set_label(label, fontsize=14)
            cbar.ax.tick_params(labelsize=12)
        else:
            # update existing colorbar to reference the new QuadMesh
            # assign the new mappable and refresh
            cbar.mappable = new_pcm
            cbar.update_normal(new_pcm)

        # remove previous QuadMesh so only new one remains
        if pcm is not None:
            pcm.remove()
        pcm = new_pcm

        # date_str = d if plot_max_all_days else str(d)[0:10]
        # save_path = check_for_dir(os.path.join(area_of_interest, "plots"))
        # plt.savefig(os.path.join(save_path, f"{area_of_interest}_fire_{generation}_{date_str}"), dpi=100)
        plt.show()
    return
