# coding: utf-8

####################################################
# Importation of external modules
import os
import numpy as np
import matplotlib.pyplot as plt
import yaml
from laspy.file import File
from scipy import interpolate
from matplotlib import cm
#import argparse

try:
    import common_function as cf # local module
except ModuleNotFoundError:
    import sys
    sys.path.append("..")
    import common_function as cf
    
#######################################################
### Parser for command-line options, arguments and sub-commands
#parser = argparse.ArgumentParser()
#parser.add_argument('config_file') # positional argument  

#if parser.prog in ['', 'ipython']: # script run on python shell or ipython
    #args = parser.parse_args(['ConfigurationFile_Figures_WetBottom.yaml'])
#else: 
    #args = parser.parse_args()
    
######################################################
# Local definition of functions

######################################################
# Loading of configuration file: User's parameters
#with open(args.config_file) as f:    
    #user_parameter = yaml.load(f)

user_parameter = yaml.load("""
path_las: '/home/fbellafo/Documents/Stage SIAME/Data/Post-doc/SOCOA- zone Fort.las'    
    """)

######################################################   
# source: https://pythonhosted.org/laspy/
las_file = File(user_parameter['path_las'], mode='r')

# Grab all of the points from the file.
point_records = las_file.points

# Find out what the point format looks like.
pointformat = las_file.point_format
for spec in pointformat:
    print(spec.name)
    
def plot_rectangle(p1, p2, color='k'):
    x1, y1 = las_file.X[p1]/1000, las_file.Y[p1]/1000
    x2, y2 = las_file.X[p2]/1000, las_file.Y[p2]/1000
    plt.plot([x1, x2, x2, x1, x1], [y1, y1, y2, y2, y1], color)
    
def kept_data_in_countour(las_file, p1, p2):
    "Renvoit les données BATHY situées dans le cadre rectangulaire horizonal défini par cadre_bathy"  
    x1, y1 = las_file.X[p1], las_file.Y[p1]
    x2, y2 = las_file.X[p2], las_file.Y[p2]
    countour = [[x1, x2], [y1, y2]]    
    X, Y, Z = las_file.X, las_file.Y, las_file.Z
    X_kept = X[(X <= np.max(countour[0])) & (X >= np.min(countour[0])) & (Y <= np.max(countour[1] )) & (Y >= np.min(countour[1]))]
    Y_kept = Y[(X <= np.max(countour[0])) & (X >= np.min(countour[0])) & (Y <= np.max(countour[1] )) & (Y >= np.min(countour[1]))]
    Z_kept = Z[(X <= np.max(countour[0])) & (X >= np.min(countour[0])) & (Y <= np.max(countour[1] )) & (Y >= np.min(countour[1]))]    
    return X_kept, Y_kept, Z_kept  

    
p1, p2 = 1498046, 2563016
r1, r2 = 8699287, 1310101

fig, ax = plt.subplots()
plt.plot(las_file.X/1000, las_file.Y/1000, '+')
plt.plot([las_file.X[p1]/1000, las_file.X[p2]/1000], [las_file.Y[p1]/1000, las_file.Y[p2]/1000], 'r')
plot_rectangle(r1, r2, 'm')
plt.axis('equal')
plt.show()

x, y, z = kept_data_in_countour(las_file, r1, r2)
x = x/1000
y = y/1000
z = z/1000

L, W = np.max(x) - np.min(x), np.max(y) - np.min(y)

DX, DY = 0.1, 0.1
Y, X = np.mgrid[np.min(y):np.max(y)+DY:DY, np.min(x):np.max(x)+DX:DX] # mesh
Z = interpolate.griddata((x, y), z, (X, Y), method='linear')

fig, ax = plt.subplots()
plt.contourf(X, Y, Z, 10, alpha=.75, cmap=cm.hot) 
plt.plot([las_file.X[p1]/1000, las_file.X[p2]/1000], [las_file.Y[p1]/1000, las_file.Y[p2]/1000], 'r')
plt.colorbar()
C = plt.contour(X, Y, Z, 10, colors='black', linewidth=.5)
plt.plot(x, y, '+')
plt.clabel(C, fontsize=10)
plt.axis('equal')
plt.xlabel('X [m]')
plt.ylabel('Y [m]')
plt.show()

def get_transect(las_file, p1, p2, delta=0.1):
    x, y, z = las_file.X/1000, las_file.Y/1000, las_file.Z/1000
    x1, y1 = las_file.X[p1]/1000, las_file.Y[p1]/1000
    x2, y2 = las_file.X[p2]/1000, las_file.Y[p2]/1000
    
    L = np.sqrt((x2-x1)**2 + (y2-y1)**2)
    d = np.arange(0, L, delta)
    
    if not d[-1] == L:
        d = np.append(d, L)
        
    x_transect, y_transect = x1 + d/L*(x2-x1), y1 + d/L*(y2-y1)
    z_transect = interpolate.griddata((x, y), z, (x_transect, y_transect), method='linear')
    
    return x_transect, y_transect, z_transect, d

#x_transect, y_transect, z_transect, d_transect = get_transect(las_file, r1, r2, delta=0.1)
cf.save_pickle('transect', get_transect(las_file, r1, r2, delta=0.1))


