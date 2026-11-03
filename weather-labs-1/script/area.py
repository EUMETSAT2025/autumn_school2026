import argparse
import sys
from pyproj import Proj
from PIL import Image
from pycoast import ContourWriterAGG

def get_parameters(name, proj, left, right, up, down, res):
    """Calculate projection parameters and area extent."""
    lat_0 = (up + down) / 2
    lon_0 = (right + left) / 2

    p = Proj(proj=proj, lat_0=lat_0, lon_0=lon_0, ellps="WGS84")

    left_ex1, up_ex1 = p(left, up)
    right_ex1, up_ex2 = p(right, up)
    left_ex2, down_ex1 = p(left, down)
    right_ex2, down_ex2 = p(right, down)
    left_ex3, _ = p(left, lat_0)
    right_ex3, _ = p(right, lat_0)

    area_extent = (
        min(left_ex1, left_ex2, left_ex3),
        min(up_ex1, up_ex2),
        max(right_ex1, right_ex2, right_ex3),
        max(down_ex1, down_ex2),
    )

    #print(area_extent[2],area_extent[0])
    #print(res)
    xsize = int(round((area_extent[2] - area_extent[0]) / float(res)))
    ysize = int(round((area_extent[3] - area_extent[1]) / float(res)))

    return proj, lat_0, lon_0, xsize, ysize, area_extent

def print_parameters(name, proj, lat_0, lon_0, xsize, ysize, area_extent):
    """Print calculated projection parameters in a structured format."""
    proj4_string = f"+proj={proj} +lat_0={lat_0} +lon_0={lon_0} +ellps=WGS84"

    print(f'### {proj4_string}\n')
    print(f"{name}:")
    print(f"  description: {name}")
    print("  projection:")
    print(f"    proj: {proj}")
    print("    ellps: WGS84")
    print(f"    lat_0: {lat_0}")
    print(f"    lon_0: {lon_0}")
    print("  shape:")
    print(f"    height: {ysize}")
    print(f"    width: {xsize}")
    print("  area_extent:")
    print(f"    lower_left_xy: [{area_extent[0]:.6f}, {area_extent[1]:.6f}]")
    print(f"    upper_right_xy: [{area_extent[2]:.6f}, {area_extent[3]:.6f}]")

def visualize_area(args, proj4_string, area_extent, xsize, ysize):
    """Visualize area using coastlines if the --shapes argument is provided."""
    if args.shapes is None:
        return

    img = Image.new('RGB', (xsize, ysize))
    area_def = (proj4_string, area_extent)
    cw = ContourWriterAGG(args.shapes)

    # Add coastlines
    cw.add_coastlines(img, area_def, resolution='l', width=8.5)

    # Add grid
    cw.add_grid(
        img, area_def, (10.0, 10.0), (2.0, 2.0),
        write_text=False, outline='white', outline_opacity=175,
        width=1.0, minor_outline='white', minor_outline_opacity=175,
        minor_width=0.2, minor_is_tick=False
    )

    img.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="The name of the area.")
    parser.add_argument("proj", help="The projection to use. Use proj.4 names, like 'stere', 'merc'...")
    parser.add_argument("min_lat", type=float, help="The latitude of the bottom of the area")
    parser.add_argument("max_lat", type=float, help="The latitude of the top of the area")
    parser.add_argument("min_lon", type=float, help="The longitude of the left of the area")
    parser.add_argument("max_lon", type=float, help="The longitude of the right of the area")
    parser.add_argument("resolution", type=float, help="The resolution of the area (in km)")
    parser.add_argument("-s", "--shapes", help="Show a preview of the area using the coastlines in this directory")

    args = parser.parse_args()

    # Convert resolution to meters
    res = args.resolution * 1000

    # Compute projection parameters
    proj, lat_0, lon_0, xsize, ysize, area_extent = get_parameters(
        args.name, args.proj, args.min_lon, args.max_lon, args.min_lat, args.max_lat, res
    )

    # Print results
    print_parameters(args.name, proj, lat_0, lon_0, xsize, ysize, area_extent)

    # Visualize if shapes are provided
    proj4_string = f"+proj={proj} +lat_0={lat_0} +lon_0={lon_0} +ellps=WGS84"
    visualize_area(args, proj4_string, area_extent, xsize, ysize)
