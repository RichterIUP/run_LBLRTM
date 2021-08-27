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
import pandas as pd
from create_input_for_lblrtm import create_TAPE5

def run_LBLRTM(z, p, t, q, hmd_unit, wnum1, wnum2, lbltp5, lbl_home, path, 
               co2=None, o3=None, co=None, ch4=None, n2o=None, o2=None,  XSELF=1, XFRGN=1, XCO2C=1, XO3CN=1, XO2CN=1, XN2CN=1, XRAYL=1):
    create_TAPE5(z, p, t, q, lbltp5, 0, hmd_unit, wnum1, wnum2, co2, o3, co, ch4, n2o, o2, XSELF, XFRGN, XCO2C, XO3CN, XO2CN, XN2CN, XRAYL)
        
    LBL_HOME = lbl_home
    T3_FILE = "tape3.data"
    print(LBL_HOME)
    
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

    with open("input.dat", "r") as file_:
        wn_low = float(file_.readline())
        wn_high = float(file_.readline())
        lbltp5 = file_.readline().rstrip()
        lbl_home = file_.readline().rstrip()
        path = file_.readline().rstrip()
    
    atm_grid = pd.read_csv("atm_grid.csv")
    z = np.array(atm_grid["altitude(km)"])
    p = np.array(atm_grid["pressure(hPa)"])
    t = np.array(atm_grid['temperature(K)'])
    q = np.array(atm_grid['humidity(%)'])
    ch4 = np.array(atm_grid['ch4(ppmv)'])
    co = np.array(atm_grid['co(ppmv)'])
    co2 = np.array(atm_grid['co2(ppmv)'])
    n2o = np.array(atm_grid['n2o(ppmv)'])
    o2 = np.array(atm_grid['o2(ppmv)'])
    o3 = np.array(atm_grid['o3(ppmv)'])
    
    lbldir = run_LBLRTM(z, p, t, q, "H", wn_low, wn_high, lbltp5=lbltp5, \
                        lbl_home=lbl_home, path=path, \
                       co=co, co2=co2, n2o=n2o, o2=o2, o3=o3, ch4=ch4)
