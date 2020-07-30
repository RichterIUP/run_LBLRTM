#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 15:08:18 2020

@author: philipp
"""

import sys
import os
import datetime as dt 
import numpy as np
import shutil
from create_input_for_lblrtm import create_TAPE5

def run_LBLRTM(z, p, t, q, atm, hmd_unit, wnum1, wnum2, lbltp5, lbl_home, path, 
               co2=None, o3=None, co=None, ch4=None, n2o=None, o2=None):
    create_TAPE5(z, p, t, q, lbltp5, atm, hmd_unit, wnum1, wnum2)
        
    LBL_HOME = lbl_home
    T3_FILE = "tape3.data"
    
    now = dt.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    second = now.second
    millisecond = now.second

    LBLRUN_DATE="{:04d}{:02d}{:02d}".format(year, month, day)
    LBLRUN_TIME="{:02d}{:02d}{:02d}{}CEST".format(hour, minute, second, millisecond)
    
    ROOT_LBLRUN_TAG="_{}_{}_{}".format(os.uname()[1], LBLRUN_DATE, LBLRUN_TIME)
    LBLRUN_TAG=ROOT_LBLRUN_TAG
    LBL_WORK="{}/.lblrtm{}".format(path, LBLRUN_TAG)

    # -- Make sure the directory doesn't already exist. If it does, suffix
    # -- the name with an _ and an integer identifier.
    LBLRUN_SUFFIX=0
    while(os.path.exists(LBL_WORK)):
        LBLRUN_SUFFIX=LBLRUN_SUFFIX+1
        LBLRUN_TAG="{}_{}".format(ROOT_LBLRUN_TAG, LBLRUN_SUFFIX)
        LBL_WORK="{}/.lblrtm{}".format(path, LBLRUN_TAG)
        
    os.mkdir(LBL_WORK)
    
    HITRAN_DIR="{}/hitran".format(LBL_HOME)
    if(not os.path.isfile("{}/FSCDXS".format(LBL_WORK))):
       os.symlink("{}/FSCDXS".format(HITRAN_DIR), "{}/FSCDXS".format(LBL_WORK))

    # -- Link /x (cross-section data) directory to LBL_WORK if required
    if(not os.path.isdir("{}/x".format(LBL_WORK))):
       os.symlink("{}/x".format(HITRAN_DIR), "{}/x".format(LBL_WORK))

    # -- Link /xs (cross-section data) directory to LBL_WORK if required
    if(not os.path.isdir("{}/xs".format(LBL_WORK))):
       os.symlink("{}/xs".format(HITRAN_DIR), "{}/xs".format(LBL_WORK))

    # -- Link TAPE3 spectroscopic database to work directory

    T3_DIR="{}".format(HITRAN_DIR)
    if(not os.path.exists("{}/{}".format(T3_DIR, T3_FILE))):   
       sys.exit(3)

    os.symlink("{}/{}".format(T3_DIR, T3_FILE), "{}/TAPE3".format(LBL_WORK))
    shutil.copy2("{}".format(lbltp5), "{}/TAPE5".format(LBL_WORK))
    
    # ----------------------------
    # Run LBLRTM in work directory
    # ----------------------------
    os.system("cd {}; nice -1 {}/bin/lblrtm".format(LBL_WORK, LBL_HOME))

    return LBL_WORK

if __name__ == '__main__':
    z = np.array([0.0, 0.008, 0.032, 0.072, 0.128, 0.2, 0.288, 0.392, 0.512, 0.648, 0.8,  0.968, \
         1.152, 1.352, 1.568, 1.8, 2.048, 2.312, 2.592, 2.888, 3.2, 3.528, 3.872, 4.232, \
         4.608, 5.0, 5.408, 5.832, 6.272, 6.728, 7.2, 7.688, 8.192, 8.712, 9.248, 9.8, 10.368, \
         10.952, 11.552, 12.168, 12.8, 13.448, 14.112, 14.792, 15.488, 16.2, 16.928, 17.672, 18.432, \
         19.208, 20.0])
    p = np.array([10.0691935484, 10.0691935484, 10.0418018489, 9.9920290033, 9.92204733044, 9.83305739721, \
         9.72480404796, 9.59846587394, 9.4546008537, 9.29330963153, 9.11648353638, 8.9250451243, \
         8.72012823129, 8.50210360138, 8.27116639365, 8.02974567835, 7.77918072235, 7.52126212776, \
         7.25811133593, 6.98847365753, 6.71383820697, 6.43499834147, 6.15212990636, 5.86672343454, \
         5.58081220485, 5.29395691368, 5.00805348591, 4.72491117985, 4.44361520906, 4.16715015576, \
         3.89510853649, 3.62866902235, 3.36849977893, 3.11611259592, 2.87506561076, 2.64479865907, \
         2.42621790995, 2.2232320913, 2.03318596144, 1.8564116623, 1.69143583689, 1.5370713746, \
         1.39388516378, 1.26158875805, 1.13884079964, 1.02527254473, 0.921760818389, 0.826728634711, \
         0.739904402865, 0.660337703568,  0.58818380923])*100
    t = np.array([273.612903226,273.612903226, 273.057738124, 272.673875423, 272.517054109, 271.970046742, \
         271.716935484,271.222147793, 270.460365738, 269.839595627, 270.086802977, 269.377582495, \
         269.694718016, 268.379542882, 266.914175907, 266.257289705, 265.737061689, 266.693548387, \
         266.445403663, 265.647577306, 263.561136482, 261.756436584, 259.352196396, 257.189278937, \
         254.699722764, 252.1727774, 249.40082503, 246.196034026, 243.204912023, 239.861473171, \
         236.216083507, 232.418024226, 228.347281141, 225.787503104, 225.012782593, 223.918548387, \
         225.243329973, 227.262907582, 228.317952383, 228.861412332, 228.843405442, 228.573161, \
         228.953055371, 229.14674716, 229.541472058, 229.232789713, 229.625510244, 229.774010109, \
         229.77615013, 229.971814334, 230.00521917])
    q = np.array([4.43525008771, 4.43525008771, 3.91163212244, 4.11013212532, 4.09430589408, 4.20118246395, \
         3.96302160684, 3.79492112852, 3.72098837478, 3.46258558754, 3.40618549525, 3.08298591678, \
         2.59367328686, 2.44014813401, 2.05108776133, 2.26184155599, 1.86362280966, 1.47139101628, \
         1.21534239674, 1.14851623259, 1.21928331259, 1.01076543751, 0.823743251872, 0.614694927612, \
         0.54732936928, 0.409350331268, 0.263205149464, 0.188926862496, 0.149236855357, 0.126514591073, \
         0.101879556598, 0.0612401049152, 0.0545139393063, 0.0340927948804, 0.0221047169385, 0.0235166588019, \
         0.00356754891666, 0.00197738522031, 0.00107859019429, 0.00114148083765, 0.00113934522762, \
         0.00110772385208, 0.00115240565472, 0.00117580628454, 0.00122482417583, 0.00118633803273, \
         0.00123549487023, 0.0012545554029, 0.00125483200763, 0.00128035552547, 0.00128475944956])
    lbldir = run_LBLRTM(z, p, t, q, lbltp5='tp5', lbllog='lbllog.txt', lbl_home="/home/philipp/RADIATIVE_TRANSFER/lblrtm", path=".")