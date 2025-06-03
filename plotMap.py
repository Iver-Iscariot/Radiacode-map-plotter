import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import folium 
import datetime   
import os
import branca.colormap as cm
from scipy.interpolate import griddata


### -------------------------- preferences -----------------
data         = "countRate"
darkMode     = False  # light/dark mode map
input_folders = ["TrondheimCSV", "GdanskCSV", "SverigeCSV", "otherCSV"] 

gridResolution = 0.0001

tileType = "Cartodb Positron"
if darkMode:
    tileType = "Cartodb dark_matter"
### --------------------------------------------------------

def findLimits(folders):
    # import dataframes using pandas
    # a list of lists of dataframes
    # [folders]         (Trondheim, gdansk...)
    #    |->  [dfs]     (trip1, trip2 ...)
    folderDfs = [[pd.read_csv(input_folder + "/" + file, sep=',') for file in os.listdir(input_folder)] for input_folder in folders]
   
    # Find the mean of all plots in the first folder (We only use this for the startpoint of the map plot)
    mean = [np.mean(folderDfs[0][0].lat),np.mean(folderDfs[0][0].lon)]

    
    # fin max and min of countrate and doserate across all tracks across all folders
    countlim = [1000, 0]
    doselim  = [1000, 0] 

    for folder in folderDfs:
        for df in folder:
            
            if max(df.countRate) > countlim[1]: countlim[1] = max(df.countRate)
            if min(df.countRate) < countlim[0]: countlim[0] = min(df.countRate)
            
            if max(df.doseRate) > doselim[1]: doselim[1] = max(df.doseRate)
            if min(df.doseRate) < doselim[0]: doselim[0] = min(df.doseRate)

    linear = cm.LinearColormap(['#00ff00', '#6fff00', '#cfff00', '#fff300', '#ffdb00', '#ffc600', '#ffb400', '#ffa300', '#ff8c00', '#ff7600', '#ff6500', '#ff5700', '#ff4a00', '#ff3e00', '#ff3600', '#ff2d00', '#ff2700', '#ff2100', '#ff1b00', '#ff1700'], vmin=countlim[0], vmax=countlim[1])
    linear.caption = "Countrate"

    return mean, countlim, doselim, linear




def plotArea(input_folder, Globalmap, GlobalColorMap, mean):
    print("Plotting area: " + input_folder)
    # This function plots all tracs from one folder.

    # It inherits a map with centerpoint and colormap found using findLimits()  

    linear = GlobalColorMap
    mean   = mean
    
    # import dataframes using pandas
    dfs = [pd.read_csv(input_folder + "/" + file, sep=',') for file in os.listdir(input_folder)]


    #find max and min of long and lat across all tracks for use in the array (needed to do interpolation)
    latlim = [100, -100]
    lonlim = [181, 0]

    for df in dfs:
        mean[0] = (mean[0] + np.mean(df.lat))/2
        mean[1] = (mean[1] + np.mean(df.lon))/2
        
        if max(df.lat) > latlim[1]: latlim[1] = max(df.lat)
        if min(df.lat) < latlim[0]: latlim[0] = min(df.lat)
        
        if max(df.lon) > lonlim[1]: lonlim[1] = max(df.lon)
        if min(df.lon) < lonlim[0]: lonlim[0] = min(df.lon)





    """
  #------------------------   creating interpolation grid   ------------------------
    # make a 2d array representing the araea within lonlim and latlim, with the step size of gridResolution
    lats = np.arange(latlim[0], latlim[1], gridResolution)
    lons = np.arange(lonlim[0], lonlim[1], gridResolution)
    # make a 2d array of the same size as the lats and lons, filled with zeros
    countRateGrid = np.zeros((len(lats), len(lons)))
    numberOfPoints = np.zeros((len(lats), len(lons)))  # count number of points added to each grid cell for later mean calculation
        
   
    def getIndex(lat, lon):
        latIndex = 0
        lonIndex = 0
        # find the index of the lat and lon in the lats and lons arrays
        for i in range(len(lats)):
            if lat < lats[i]:
                latIndex = i - 1
                break
        for i in range(len(lons)):
            if abs(lon) < abs(lons[i]):
                lonIndex = i - 1
                break
        # if latIndex or lonIndex is out of bounds, set it to the last index    
        if latIndex >= len(lats): latIndex = len(lats) - 1        
        if lonIndex >= len(lons): lonIndex = len(lons) - 1
        return latIndex, lonIndex

    # loop through all the dataframes and add the countRate to the countRateGrid (we just sum the countRate in each grid cell, and later divide by the amount of datapoints in that grid cell to get a mean at that coordinate)
    for df in dfs:
        for i in range(len(df.lat)):
            latIndex, lonIndex = getIndex(df.lat[i], df.lon[i])
            countRateGrid[latIndex][lonIndex] += df.countRate[i]
            numberOfPoints[latIndex][lonIndex] += 1

    # divide countRateGrid by numberOfPoints to get the mean countRate in each grid cell, taking care to avoid zero division
    for i in range(len(countRateGrid)):
        for j in range(len(countRateGrid[i])):
            if numberOfPoints[i][j] != 0:
                countRateGrid[i][j] /= numberOfPoints[i][j]
            else:
                countRateGrid[i][j] = 0
    """
    
    #------------------------   creating interpolation grid   ------------------------
    """
    # Coordinates grid
    x, y = np.indices(countRateGrid.shape)
    # Mask of known (nonzero) values
    known_mask = countRateGrid != 0
    # Known positions and values
    known_coords = np.column_stack((x[known_mask], y[known_mask]))
    known_values = countRateGrid[known_mask]
    # All positions
    all_coords = np.column_stack((x.ravel(), y.ravel()))
    # Interpolate
    interpolated = griddata(
        known_coords, known_values, all_coords,
        method='linear', fill_value=0
    ).reshape(countRateGrid.shape)
    # Preserve original nonzero values
    interpolated[known_mask] = countRateGrid[known_mask]
"""

    # optional: plot the grids in matpllotlib
    """
    plt.subplot(2,1,1)
    # plot the countRateGrid as a scatterplot in matplotlib using the "linear" colormap
    plt.imshow(countRateGrid, cmap= "Oranges_r", extent=[lonlim[0], lonlim[1], latlim[0], latlim[1]], origin='lower')
    plt.colorbar(label="Count Rate")
    plt.subplot(2,1,2)
    plt.imshow(interpolated, cmap= "Oranges_r", extent=[lonlim[0], lonlim[1], latlim[0], latlim[1]], origin='lower')
    plt.colorbar(label="Count Rate")
    plt.show()
    """

    #------------------------   plotting using folium   ------------------------
    """
    # add the grid to the map using folium
    # create a grid of folium polygons at the coordinates of the grid, with a color based on the interpolated value at that coordinate
    for i in range(len(countRateGrid)):
        for j in range(len(countRateGrid[i])):
            coords = [
                    [lats[i] - gridResolution, lons[j] - gridResolution],
                    [lats[i] - gridResolution, lons[j] + gridResolution],
                    [lats[i] + gridResolution, lons[j] + gridResolution],
                    [lats[i] + gridResolution, lons[j] - gridResolution]
                ]


            # The interpolated plot lags out the HTML page. make it lower resolution before adding back in
            if interpolated[i][j] != 0:                
                folium.Polygon(
                    locations=coords,
                    color=linear(interpolated[i][j]),
                    weight=0,             # border thickness
                    fill=True,
                    fill_opacity=0.1
                ).add_to(map)
            
            
            if countRateGrid[i][j] != 0:
                folium.CircleMarker(
                        location=[lats[i], lons[j]],
                        radius=1,
                        color=linear(countRateGrid[i][j]),
                        fill=True,
                        fill_opacity=0.99,
                    ).add_to(map)
            
    """
    # plot without use of grid (straight coordinates) for when were not using interpolation
    counter = 0
    for df in dfs:
        counter += 1
        print("Plotting track nr: " + str(counter) + " of " + str(len(dfs)) + " in folder: " + input_folder)
        for i in range(len(df.lat)):
            folium.CircleMarker(
                    location=[df.lat[i], df.lon[i]],
                    radius=1,
                    color=linear(df.countRate[i]),
                    fill=True,
                    fill_opacity=0.99,
                ).add_to(map)

    

    map.add_child(linear)
    map.save("map.html")

mean, countlim, doselim, linear = findLimits(input_folders)

map = folium.Map(location=[
        mean[0], mean[1]],
        tiles=tileType,
        zoom_start= 13
    )

for folder in input_folders:
    plotArea(folder, map, linear, mean)
