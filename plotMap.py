import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import folium 
import datetime   
import os
import branca.colormap as cm


### -------------------------- preferences -----------------
data         = "countRate"
darkMode     = False  # light/dark mode map
input_folder = "csvFiles"

tileType = "Cartodb Positron"
if darkMode:
    tileType = "Cartodb dark_matter"
### --------------------------------------------------------


# import dataframes using pandasS
dfs = [pd.read_csv(input_folder + "/" + file, sep=',') for file in os.listdir(input_folder)]


# Find the mean of all plots to find center of map mean = [lat, lon]
mean = [np.mean(dfs[0].lat),np.mean(dfs[0].lon)]
#find max and min of long and lat across all tracks
latlim = [100, -100]
lonlim = [181, 0]
# fin max and min of countrate and doserate across all tracks
countlim = [1000, 0]
doselim  = [1000, 0] 

for df in dfs:
    mean[0] = (mean[0] + np.mean(df.lat))/2
    mean[1] = (mean[1] + np.mean(df.lon))/2
    
    if max(df.lat) > latlim[1]: latlim[1] = max(df.lat)
    if min(df.lat) < latlim[0]: latlim[0] = min(df.lat)
    
    if max(df.lon) > lonlim[1]: lonlim[1] = max(df.lon)
    if min(df.lon) < lonlim[0]: lonlim[0] = min(df.lon)
    
    if max(df.countRate) > countlim[1]: countlim[1] = max(df.countRate)
    if min(df.countRate) < countlim[0]: countlim[0] = min(df.countRate)
    
    if max(df.doseRate) > doselim[1]: doselim[1] = max(df.doseRate)
    if min(df.doseRate) < doselim[0]: doselim[0] = min(df.doseRate)
    

linear = cm.LinearColormap(['#00ff00', '#6fff00', '#cfff00', '#fff300', '#ffdb00', '#ffc600', '#ffb400', '#ffa300', '#ff8c00', '#ff7600', '#ff6500', '#ff5700', '#ff4a00', '#ff3e00', '#ff3600', '#ff2d00', '#ff2700', '#ff2100', '#ff1b00', '#ff1700'], vmin=countlim[0], vmax=countlim[1])
linear.caption = "Countrate"

# initiate map
map = folium.Map(location=[
    mean[0], mean[1]],
    tiles=tileType,
    zoom_start= 13
)

# plot all the paths
for df in dfs:
    toupleCoords = [(df.lat[i], df.lon[i]) for i in range(len(df.lat))]  # folium wants coords in a touple
    color_line = folium.ColorLine(
        positions=toupleCoords,
        colors=df.countRate,
        colormap=linear,
        weight=3,
    ).add_to(map)
    
map.add_child(linear)
map.save("map.html")