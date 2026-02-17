import numpy as np
import os
from PIL import Image

#Steps: list of elevations in ascending order

sea_steps = [
    -8100,
    -6400,
    -4900,
    -3600,
    -2500,
    -1600,
    -900,
    -400,
    -100,
    #0,     #extra step for use with gradient coloring
    ]

#Colors: list of rgb colors corresponding to elevation steps
# for regular use with solid colors, there should be 1 more color than steps
#   1 color for each interval between steps
#   and 2 extra for everything below the first step and above the last
# for gradient color, there should be an equal number of colors and steps
#   each color corresponds to one of the elevation steps
#   and then all other elevations are interpolated between colors
#   with areas outside the range of the steps just filled with the first or last color

sea_colors = [
     [113, 171, 216],
     [121, 178, 222],
     [132, 185, 227],
     [141, 193, 234],
     [150, 201, 240],
     [161, 210, 247],
     [172, 219, 251],
     [185, 227, 255],
     [198, 236, 255],
     [216, 242, 254],
    ]



#Steps and colors for land

land_steps = [
    #0,     #extra step for use with gradient coloring
    25,
    100,
    225,
    400,
    625,
    900,
    1225,
    1600,
    2025,
    2500,
    3025,
    3600,
    4225,
    4900,
    5625,
    6400,
    7225,
    8100,
    ]

land_colors = [
     [172, 208, 165],
     [148, 191, 139],
     [168, 198, 143],
     [189, 204, 150],
     [209, 215, 171],
     [225, 228, 181],
     [239, 235, 192],
     [232, 225, 182],
     [222, 214, 163],
     [211, 202, 157],
     [202, 185, 130],
     [195, 167, 107],
     [185, 152,  90],
     [170, 135,  83],
     [172, 154, 124],
     [186, 174, 154],
     [202, 195, 184],
     [224, 222, 216],
     [245, 244, 242],
     ]



ice_steps = [
    #0,
    100,
    400,
    900,
    1600,
    2500,
    3600,
    4900,
    6400,
    8100,
    ]

ice_colors = [
     [210, 210, 210],
     [215, 215, 215],
     [220, 220, 220],
     [225, 225, 225],
     [230, 230, 230],
     [235, 235, 235],
     [240, 240, 240],
     [245, 245, 245],
     [250, 250, 250],
     [255, 255, 255],
     ]



#Each layer gets its dict with its parameters

## Parameters:
# For elevation map, either:
#   map: greyscale map to be used for this layer only
#   basemap: used like map, but also saved as basemap for other sets
#   use neither to use previously saved basemap
# for scaling, choose either:
#   max: maximum elevation on greyscale map
#   min: minimum elevation on greyscale map
# or:
#   white: elevation of full white
#   black: elevation of full black
# Then either:
#   steps: list of elevation steps
#   colors: list of rgb colors corresponding to steps
# or:
#   onecolor: single color to fill whole map
# masking options (can be combined):
#   mask: greyscale image mask, will mark everywhere > half white
#   above: only mark > this elevation
#   below: only mark < this elevation
#   compare: set 'max' to mark where map > basemap, 'min' to mark where map < basemap
# additional options:
#   gradient: True to draw gradient between steps
#    by default gradients interpolates color linearly by elevation between elevation steps,
#    alternatively:
#       gradexp: exponent to scale elevation by before applying gradient (e.g. 0.5 works well with the example scales)


#examples:

#sea colors first, with base elevation map
sea = {
    'basemap': 'elev_map.png',
    'max': 10000,
    'min': -10000,
    'steps': sea_steps,
    'colors': sea_colors,
    }

#land colors next; includes no map so reuses base map
land = {
    'steps': land_steps,
    'colors': land_colors,
    'above': 0.0,   #masked to only apply above sea level
    }

#ice map uses separate ice elevation map and extra masks
ice = {
    'map': 'ice_map.png',   #extra map used only for this layer
    'max': 10000,
    'min': 0,
    'steps': ice_steps,
    'colors': ice_colors,
    'compare': 'max',   #apply only where ice elevation is above land elevation
    'above': 0.0,   #can combine multiple mask types
    }


#list layers in order they should be applied
layers = [
    sea,
    land,
    ice,
    ]

#can include as many layers as you want, including even just one;
# I use separate sea and land layers here only to ensure no blending at the coast if using gradient colors


#name of output file
outname = 'color_map.png'






#Get elevation data from greyscale map
def get_map(grey, mmax, mmin, fullscale=False):
    gmap = Image.open(grey)
    gdat = np.asarray(gmap)
    if fullscale:
        testar = [[255]]    #slightly funky procedure to determine max value for image mode
        testim = Image.fromarray(outmap.astype(np.uint8))
        testim.convert(gmap.mode)
        testar = np.asarray(testim)
        modemax = testar[0,0]
        gdat = gdat / modemax * (mmax - mmin) + mmin
    else:
        gdat = gdat / (np.max(gdat) - np.min(gdat)) * (mmax - mmin) + mmin
    return gdat

#Produce colors from elevation data, steps list, and colors list
def get_col(dat, steps, colors, layer={}):
    colmap = np.ones((dat.shape[0],dat.shape[1],3), dtype=np.uint8)
    colmap[:] = colors[0]   #set whole map to lowest color by default
    if ('gradient' in layer) and (layer['gradient']):
        colal = np.asarray(colors)
        if 'gradexp' in layer:
            dat2 = np.absolute(dat)
            dat2 = dat2**layer['gradexp']
            dat2 = dat2*np.sign(dat)
            steps2 = [np.absolute(s) for s in steps]
            steps2 = [s**layer['gradexp'] for s in steps2]   #scale data and steps
            steps2 = [s * np.sign(z) for s,z in zip(steps2,steps)]
        else:
            dat2 = dat
            steps2 = steps
        for n in range(len(steps2)):
            if n == len(steps2) - 1:
                colmap[dat2 > steps2[n]] = colors[n]  #color in everything above highest step with last color
            else:
                srange = (dat2 > steps2[n]) & (dat2 <= steps2[n+1])     #select everywhere within step interval
                hstep = (dat2 - steps2[n]) / (steps2[n+1] - steps2[n])      #find position relative to bounding steps
                colstep = colal[n] + (np.expand_dims(hstep,-1) * (colal[n+1] - colal[n]))   #interpolate color values
                colmap[srange] = colstep[srange]
    else:
        for n in range(len(steps)):
            colmap[dat > steps[n]] = colors[n+1]    #without gradient, just color in step intervals one by one
    return colmap


def Color_map(layers, outname):
    basedat = None
    outmap = None
    for l in layers:
        ldat = None
        lmap = None
        mask = True
        #get map
        if 'basemap' in l:
            if 'max' in l:
                ldat = get_map(l['basemap'], l['max'], l['min'])
            else:
                ldat = get_map(l['basemap'], l['white'], l['black'],fullscale=True)
            basedat = ldat
        if 'map' in l:
            if 'max' in l:
                ldat = get_map(l['map'], l['max'], l['min'])
            else:
                ldat = get_map(l['map'], l['white'], l['black'],fullscale=True)
        if ldat is None:
            ldat = basedat

        #build color map
        if 'onecolor' in l:
            lmap = np.ones((ldat.shape[0],ldat.shape[1],3), dtype=np.uint8)
            lmap[:] = l['onecolor']
        elif 'colors' in l:
            lmap = get_col(ldat, l['steps'], l['colors'], l)

        #masking
        if 'mask' in l:
            maskdat = get_map(l['mask'], 100.0, 0.0)
            mask = np.where(maskdat > 50)
        if 'above' in l:
            mask = np.where(ldat > l['above'], mask, False)
        if 'below' in l:
            mask = np.where(ldat < l['below'], mask, False)
        if 'compare' in l:
            if l['compare'] == 'max':
                mask = np.where(ldat > basedat, mask, False)
            if l['compare'] == 'min':
                mask = np.where(ldat < basedat, mask, False)

        #apply to map
        outmap = np.where(np.expand_dims(mask,-1), lmap, outmap)
            
    outim = Image.fromarray(outmap.astype(np.uint8))
    outim.save(outname)
    return

Color_map(layers,outname)
    
