#! c:/users/mark/developer/python/hdfm/.venv/scripts/pythonw.exe
import matplotlib.pyplot as plt
import numpy as np

import math
import requests
from io import BytesIO
from PIL import Image, ImageDraw

# from https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 1 << zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile
  
def num2deg(xtile, ytile, zoom):
    n = 1 << zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg

# -----  

def getImageCluster(lat1_deg, lon1_deg, lat2_deg, lon2_deg, zoom):
    smurl = r"https://tile.openstreetmap.org/{0}/{1}/{2}.png"
    left_tile, top_tile = deg2num(lat1_deg, lon1_deg, zoom)
    right_tile, bottom_tile = deg2num(lat2_deg, lon2_deg, zoom)
    top_lat, left_lon = num2deg(left_tile, top_tile, zoom)
    bot_lat, right_lon = num2deg(right_tile+1, bottom_tile+1, zoom)
    img_width = (right_tile - left_tile + 1) * 256
    img_height = (bottom_tile - top_tile + 1) * 256
    deg_width = right_lon - left_lon
    deg_height = top_lat - bot_lat
    deg_xpix = deg_width / img_width
    deg_ypix = deg_height / img_height
    left_offset = (lon1_deg - left_lon) / deg_xpix
    right_offset = (lon2_deg - left_lon) / deg_xpix
    top_offset = (top_lat - lat1_deg) / deg_ypix
    bot_offset = (top_lat - lat2_deg) / deg_ypix

    Cluster = Image.new('RGBA',(img_width, img_height)) 
    headers = {
      'user-agent':"Mozilla/5.0 ...",
    }
    try:
        for xtile in range(left_tile, right_tile + 1):
            for ytile in range(top_tile,  bottom_tile + 1):
                imgurl=smurl.format(zoom, xtile, ytile)
                imgstr = requests.get(imgurl, headers=headers)
                tile = Image.open(BytesIO(imgstr.content))
                Cluster.paste(tile, box=((xtile - left_tile) * 256,  (ytile - top_tile) * 256))
        delta = min(right_offset - left_offset, bot_offset - top_offset)
        return Cluster.crop((left_offset, top_offset, left_offset + delta, top_offset + delta))
    except Exception as e:
        print (e)
        pass     
   
  
if __name__ == '__main__':
    a = getImageCluster(42.04157, -85.57844, 37.91347, -80.18855, 8)
    if a:
        b = Image.open('weather.png').convert(mode='RGBA')
        c = Image.alpha_composite(a,b.resize(a.size))
        c.save('map.png')
        fig = plt.figure()
        fig.patch.set_facecolor('white')
        plt.imshow(np.asarray(c))
        plt.show()
    
