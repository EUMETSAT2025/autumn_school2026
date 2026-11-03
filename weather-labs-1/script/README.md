# Script for Imagery

### Python environment

*Note: If the environment is installed already, it only needs to be activated.*

First we need to create the python environment.

To create the environment, run:

`mamba env create -f environment.yml`

This will create a Python environment called **MTG**. The environment won't be activated by default. To activate it, run:

`conda activate MTG`

### Running the Script

*Note: /data/Weather/ is no longer accessible on TrainHub. In the examples below, replace /data/Weather/script/ with the folder where your unzipped data is.*

1. change directory to script/ by doing ->  cd script
2. Run the script by following the example below
Example: 
            
            ./create_imagery.sh "/data/Weather/script/" IR_105,airmass 2025-03-28T12:40:00Z 2025-03-28T13:40:00Z 10 germ 2000

Arguments specification (arguments are separated by space character):
   a) "/data/Weather/script/" - location of the unzipped data (absolute path)
   b) IR_105,airmass - list of channels and composites separated by comma as per file composites/fci.yaml 
   c) 2025-03-28T12:40:00Z - start timestamp
   d) 2025-03-28T13:40:00Z - end timestamp
   e) 10 - interval between consecutive images
   f) germ - spatial designation
   g) 2000 - spatial resolution of the imagery in metres

**Options for channel/composite selection - argument b):**

    a) single channel/composite - "IR_105"

            ./create_imagery.sh "/data/Weather/script/" IR_105,airmass 2025-03-28T12:40:00Z 2025-03-28T13:40:00Z 10 germ 2000

            will produce six IR 10.5 images (6 timesteps)
            
    b) multi channel/composite - "IR_105,airmass"

            ./create_imagery.sh "/data/Weather/script/" IR_105,airmass 2025-03-28T12:40:00Z 2025-03-28T13:40:00Z 10 germ 2000

            will produce six IR 10.5 and six airmass RGB images

**Options for spatial designation - argument f):**

   a) "0" - Full disk mode

   ./create_imagery.sh "/data/Weather/script/" IR_105,airmass 2025-03-28T12:40:00Z 2025-03-28T13:40:00Z 10 "0" 2000
   
   b) "10,30,40,60" - bounding box mode (min_lon,max_lon,min_lat,max_lat) *Note: Resolution argument g) works only in bounding box mode*

   ./create_imagery.sh "/data/Weather/script/" IR_105,airmass 2025-03-28T12:40:00Z 2025-03-28T13:40:00Z 10 "10,30,40,60" 2000

   c) "germ" - area of Germany and surroundings - using satpy preset areas (for more info check: https://github.com/pytroll/satpy/blob/main/satpy/etc/areas.yaml)

   ./create_imagery.sh "/data/Weather/script/" IR_105,airmass 2025-03-28T12:40:00Z 2025-03-28T13:40:00Z 10 germ 2000

**Options for temporal designation - arguments c), d) and e):**

    Temporal scheme or cadence of the produced imagery can be controlled with following 3 arguments: c), d) and e). These represent start
    time, end time and step between images in minutes, respectively. End time is not included.

    Examples:

    a) ./create_imagery.sh "/data/Weather/script/" IR_105,airmass 2025-03-28T12:40:00Z 2025-03-28T13:40:00Z 10 germ 2000

    will create images for timesteps:

    2025-03-28T12:40:00Z
    2025-03-28T12:50:00Z
    2025-03-28T13:00:00Z
    2025-03-28T13:10:00Z
    2025-03-28T13:20:00Z
    2025-03-28T13:30:00Z

    b) ./create_imagery.sh "/data/Weather/script/" fire_temperature 2025-03-28T12:40:00Z 2025-03-28T13:40:00Z 30 "0" 10000

    will create images for timesteps:

    2025-03-28T12:40:00Z
    2025-03-28T13:10:00Z
    
3. Find the imagery in the directory plots/.

**For fine tuning of the RGBs and single channle images it is necessary to edit enhancements/fci.yaml by changing the recipe for the particular
composite/single channel. Make sure to save file once you edit it for changes to be accepted.**