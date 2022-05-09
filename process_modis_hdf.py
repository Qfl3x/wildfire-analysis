import os
import datetime
import re
import io

import geopandas as gpd
import pandas as pd

file_list = os.listdir('./')

hdf_list = list(filter(lambda x: x[-3:] == 'hdf', file_list))

firemask_gdf = gpd.GeoDataFrame({'DN':[],'geometry':[],'date':[]}, geometry='geometry')
maxfrp_gdf = gpd.GeoDataFrame({'DN':[],'geometry':[],'date':[]}, geometry='geometry')

countries_gdf = gpd.read_file('World_Countries.shp')
countries_gdf = countries_gdf.to_crs(3857)
algeria_poly = countries_gdf.loc[3, 'geometry']

cleanshpcom = f"rm polygon*"
for file in hdf_list:
    year = int(re.search(r"MOD14A1.A(\d\d\d\d)(\d\d\d)*", file).group(1))
    days = int(re.search(r"MOD14A1.A(\d\d\d\d)(\d\d\d)*", file).group(2))
    day1 = (datetime.datetime(year,1,1) + datetime.timedelta(days-1)).date()
    for band in range(1,9):
        date = (day1 + datetime.timedelta(band-1))
        days = days + band - 1
        
        polygonizecom = f"gdal_polygonize.py HDF5:"{file}"://HDFEOS/GRIDS/VNP14A1_Grid/Data_Fields/FireMask polygon.shp geometry"
        
        os.system(polygonizecom)
        
        gdf = gpd.read_file('polygon.shp', geometry = 'geometry')
        
        gdf['date'] = date
        gdf = gdf.loc[gdf.within(algeria_poly)]
        firemask_gdf = pd.concat([firemask_gdf, gdf], ignore_index=True)
        os.system(cleanshpcom)
        
for file in hdf_list:
    year = int(re.search(r"VNP14A1.A(\d\d\d\d)(\d\d\d)*", file).group(1))
    days = int(re.search(r"VNP14A1.A(\d\d\d\d)(\d\d\d)*", file).group(2))
    day1 = (datetime.datetime(year,1,1) + datetime.timedelta(days-1)).date()
    for band in range(1,9):
        date = (day1 + datetime.timedelta(band-1))
        days = days + band - 1
    
        polygonizecom = f"gdal_polygonize.py HDF5:"{file}"://HDFEOS/GRIDS/VNP14A1_Grid/Data_Fields/MaxFRP polygon.shp geometry"
        
        os.system(polygonizecom)
        
        gdf = gpd.read_file('polygon.shp', geometry = 'geometry')
        
        gdf['date'] = date
        gdf = gdf.loc[gdf.within(algeria_poly)]
        maxfrp_gdf = pd.concat([maxfrp_gdf, gdf], ignore_index=True)
        os.system(cleanshpcom)
      
firemask_gdf = firemask_gdf.loc[firemask_gdf.DN >= 8]

firemask_gdf.date = firemask_gdf.date.apply(str)
maxfrp_gdf.date = maxfrp_gdf.date.apply(str)

firemask_gdf.loc[firemask_gdf.DN >= 7].to_file('NE_2021.gpkg', layer='FireMask', driver="GPKG")
maxfrp_gdf.to_file('NE_2021.gpkg', layer='MaxFRP', driver="GPKG")
