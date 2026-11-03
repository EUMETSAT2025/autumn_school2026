# weather-labs-1

Here are some Jupyter notebooks and python scripts to work with weather data to build cases, labs and have people explore the data.

## License
  
This code is licensed under [GPL-3](https://spdx.org/licenses/GPL-3.0-only.html) license. See file LICENSE.txt for details on the usage and distribution terms.

All product names, logos, and brands are property of their respective owners. All company, product and service names used in this website are for identification
purposes only.

## Authors
* [**Dr. Alen Berta**](mailto://alen.berta@cgi.com) - *Initial work* - [CGI](http://www.cgi.com)
* [**Ivan Smiljanic**](mailto://Ivan.Smiljanic@external.eumetsat.int) - *Initial work* - [Exostaff](http://www.exostaff.de)
* [**Carla Barroso**](mailto://Carla.Barroso@eumetsat.int) - *Contributor* - [EUMETSAT](http://www.eumetsat.int)
* [**Djordje Gencic**](mailto://djordje.gencic@exostaff.de) - *Contributor* - [Exostaff](http://www.exostaff.de)
* [**Natasa Strelec Mahovic**](mailto://Natasa.StrelecMahovic@eumetsat.int) - *Contributor* - [EUMETSAT](http://www.eumetsat.int)
* [**Bartolomeo Viticchie**] - *Contributor* - [EUMETSAT](http://www.eumetsat.int)
* [**Sven-Erik Enno**] - *Contributor* - [EUMETSAT](http://www.eumetsat.int)

* [**Pablo Benedicto**](mailto://pablo.benedicto@solenix.ch) - *Contributor* - [Solenix](http://www.solenix.ch)
* [**Vesa Nietosvaara**](mailto://Vesa.Nietosvaara@eumetsat.int) - *SW Responsible* - [EUMETSAT](http://www.eumetsat.int)

## Getting Started

### Prerequisites

You will require `Jupyter Notebook` to run this code. We recommend that you install the latest [Anaconda Python distribution](https://www.anaconda.com/) for your operating system. Anaconda Python distributions include Jupyter Notebook.

#### Included components
The following components are included in this SW package:
* component name, version, SPDX license id, copyright, home_url, location, comments
* DejaVuSans, 2.37, Bitstream-Vera, Copyright (c) 2004-2016 DejaVu fonts team, https://github.com/dejavu-fonts/dejavu-fonts, "./Lab7_GOES-16_GLM_data_as_proxy_for_MTG_LI_data/DejaVuSans.ttf" and "./Lab8_European_small_fires_observed_with_proxy_FCI_data/DejaVuSans.ttf"
* coord2area_def.py, 0.39.0, GPL-3-or-later, Copyright (c) 2012-2019 Satpy developers, https://github.com/pytroll/satpy/blob/v0.39.0/utils/coord2area_def.py, Location: ./Lab10_FCI_data_display/coord2area_def.py

#### Dependencies
The following dependencies are not included in the package but are required and they will be downloaded at build or compilation time:

* component name, version, SPDX license id, copyright, home_url, location, comments
* cartopy, 0.21.1, LGPL-3.0; GPL-3.0, (C) British Crown Copyright 2011 - 2016 Met Office, https://github.com/SciTools/cartopy
* matplotlib, 3.6.3, PSF-2.0, Copyright 2002 - 2012 John Hunter / Darren Dale / Eric Firing / Michael Droettboom / the Matplotlib development team; 2012 - 2023 The Matplotlib development team, https://github.com/matplotlib/matplotlib
* pycoast, 1.6.1, GPL-3.0, Copyright (C) 2007 Free Software Foundation Inc., https://github.com/pytroll/pycoast
* notebook, 6.5.2, BSD-3, Copyright (c) 2001-2015, IPython Development Team;Copyright (c) 2015-, Jupyter Development Team, https://github.com/jupyter/notebook
* satpy, 0.39.0, GPL-3.0-or-later, Copyright (C) 2007 Free Software Foundation Inc., https://github.com/pytroll/satpy
* python, 3.9, PSF-2.0, ,https://github.com/python/
* imageio-ffmpeg, 0.4.8, BSD 2-Clause License, Copyright (c) 2019, imageio, https://github.com/imageio/imageio-ffmpeg/
* pydecorate, 0.3.4 , GPL-3.0,  Copyright (C) 2007 Free Software Foundation Inc.,https://github.com/pytroll/pydecorate/
* ipympl, 0.9.3, BSD 3-Clause "New" or "Revised" License, Copyright (c) 2016, Matplotlib Contributors, https://github.com/matplotlib/
* pyhdf, 0.10.5, MIT License (MIT), Copyright (c) 2019 The pyhdf Authors, https://github.com/fhs/pyhdf

## Installation

The simplest and best way to install these packages is via Git. Users can clone this repository by running the following commands from either their [terminal](https://tinyurl.com/2s44595a) (on Linux/OSx), or from the [Anaconda prompt](https://docs.anaconda.com/anaconda/user-guide/getting-started/). 

You can usually find your terminal in the start menu of most Linux distributions and in the Applications/Utilities folder  on OSx. Alternatively, you should be able to find/open your Anaconda prompt from your start menu (or dock, or via running the Anaconda Navigator). Once you have opened a terminal/prompt, you should navigate to the directory where you want to put the code. Once you are in the correct directory, you should run the following command;

`git clone --recurse-submodules --remote-submodules https://gitlab.eumetsat.int/eo-lab-usc-open/weather/weather-labs/weather-labs-1.git`

This will make a local copy of all the relevant files.

*Note: If you find that you are missing packages, you should check that you ran `git clone` with both the `--recurse-submodules` and `--remote-submodules` options.*

*Note: if you are using an older version of git, you may find that your submodules are empty. In this case, you need to remove the folder and re-run the line above with `--recursive` added to the end*


## Usage

This collection supports Python 3.9. Although many options are possible, the authors highly recommend that users install the appropriate Anaconda package for their operating system. In order to ensure that you have all the required dependencies, we recommend that you build a suitable Python environment, as discussed below.

### Python environments

Python allows users to create specific environments that suit their applications. This tutorials included in this collection require a number of non-standard packages - e.g. those that are not included by default in Anaconda. In this directory, users will find a *environment.yml* file which can be used to construct an environment that will install all the required packages.

To construct the environment, you should open either **terminal** (Linux/OSx) or an **Anaconda prompt** window and navigate to repository folder you downloaded in the **Installation** section above. In this folder there is a file called **environment.yml**. This contains all the information we need to install the relevant packages.

To create the environment, run:

`mamba env create -f environment.yml`

*Note: use `mamba` rather than `conda env create`: the classic conda solver can run out of memory and be killed while solving this environment. `conda activate` works as usual afterwards.*

This will create a Python environment called **MTG**. The environment won't be activated by default. To activate it, run:

`conda activate MTG`

In order to add new kernel to the list in the jupyter notebook, run:

`python -m ipykernel install --user --name=MTG`

Now you are ready to go!

*Note: remember that you may need to reactivate the environment in every  new window instance*

### Running Jupyter Notebook

This module is based around a series of [Jupyter Notebooks](https://jupyter.org/). These support high-level interactive learning by allowing us to combine code, text description and data visualisations. If you have not worked with `Jupyter Notebooks` before, please look at the [Introduction to Python and Project Jupyter](./working-with-python/Intro_to_Python_and_Jupyter.ipynb) module to get a short introduction to their usage and benefits.

To to run Jupyter Notebook, open a terminal or Anaconda prompt and make sure you have activated the correct environment. Again, navigate to the repository folder.

TODO: Check if this is applicable here!
If you are running this code for the first time in this environment, you need to enable two `extensions` to Jupyter by running the following commands.

`jupyter nbextension enable --py widgetsnbextension` \
`jupyter nbextension enable exercise2/main`

*Note: you can also enable these in the **Nbextensions** tab of the Jupyter browser window* 

Now you can run Jupyter using:

`jupyter notebook`

This should open Jupyter Notebooks in a browser window. On occasion, Jupyter may not be able to open a window and will give you a URL to past in your browser. Please do so, if required.

*Note: Jupyter Notebook is not able to find modules that are 'above' it in a directory tree, and you will unable to navigate to these. So make sure you run the line above from the correct directory!*

Now you can run the notebooks!
