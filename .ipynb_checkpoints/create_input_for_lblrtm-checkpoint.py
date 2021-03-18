#!/usr/bin/python3
# Original: 
# $Id: rundecker.pro,v 1.37 2012/08/15 11:43:52 dturner Exp $
#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
#;+
#; Abstract:
#;	  This script builds rundecks which can be used for both the LBLRTM
#;	and the RRTM. Clear sky runs only. Can use standard atmospheres
#;	for the PTU data (one or all variables).  Able to compute either 
#;	radiance/transmittance or optical depths.  Layer structure used in the
#;	models can be specified.  Lots of features here.
#;
#;	  Profiles for other gasses can be specified to be one of the default
#;       atmospheres.  In fact, its a good idea to always specify the background
#;	atmosphere when z/p/t/w are entered, so the correct atmosphere is added
#;	above the highest level in the z/p/t/w profile...
#;
#; Author:	Dave Turner, PNNL
#; Date:		February, 1998
#;
# Python translation:
#  Author: Philipp Richter, IUP-HB
#  Date: July, 2020

import numpy as np


#MODEL   selects atmospheric profile
#= 0  user supplied atmospheric profile
#= 1  tropical model
#= 2  midlatitude summer model
#= 3  midlatitude winter model
#= 4  subarctic summer model
#= 5  subarctic winter model
#= 6  U.S. standard 1976
def create_TAPE5(z, p, t, w, tape5, atm, hmd_unit, wnum1, wnum2, \
              co2=None, o3=None, co=None, ch4=None, n2o=None, o2=None, \
              XSELF=1, XFRGN=1, XCO2C=1, XO3CN=1, XO2CN=1, XN2CN=1, XRAYL=1):
   
    view_angle=0.0 # Downwelling
    resolution = 1.0
    
    ###############################
    # Reshape atmospheric profile #
    ###############################
    JCHAR = '{}'.format(hmd_unit)
    zz = z
    tt = t
    pp = p
    ww = w
    if np.where((pp != np.sort(pp)[::-1]) == True)[0].size != 0:
        raise IndexError("Pressure array is not monotonically increasing - quitting")

    #Only unique pressure levels
    pp = np.union1d(np.sort(pp)[::-1], np.sort(pp)[::-1])
    index = []
    for ii in pp:
        index.append(np.where(p == ii)[0][0])
    index = np.array(index)[::-1]
    pp = p[index]
    zz = z[index]
    tt = t[index]
    ww = w[index]
    #o3 = np.zeros(len(ww))
    #co2 = np.zeros(len(ww))
    #co = np.zeros(len(ww))
    #ch4 = np.zeros(len(ww))
    #n2o = np.zeros(len(ww))
    trace_gas = [co2, o3, co, ch4, n2o, o2]
    for tg in range(len(trace_gas)):
        if not (trace_gas[tg] is None):
            trace_gas[tg] = trace_gas[tg][index]
            JCHAR += 'A'
        else:
            trace_gas[tg] = np.zeros(len(index))
            JCHAR += '{:1d}'.format(atm) 
    inlayers = len(zz)
   
    
    #############
    # Paramters #
    #############
    ihirac = 1#Voigt profile
    ilblf4 = 1#line by line bound is 25cm-1 for all layer pressures (altitudes)
    #icntnm = 0#no continuum calculated
    icntnm = 6#all continua calculated, including Rayleigh extinction where applicable
    iaersl = 0#no aerosols used
    iemit  = 0#optical depth only
    iscan  = 0
    ifiltr = 0#flag for FILTR
    iplot  = 0#flag for PLTLBL
    itest  = 0#flag for TEST
    iatm   = 1#flag for LBLATM
    imrg   = 1#optical depths only; results for each layer on different file
    ilas   = 0#not available in LBLRTM
    ixsect = 1#cross-sections included in calculation
    mpts   = 0#number of optical depth values printed for the beginning and 
              #ending of each panel as a result of convolution for current layer
    npts   = 0#number of values printed for the beginning and ending of each panel
              #as result of merge of current layer with previous layers 
    model_atm = 0#User defined profile
    itype = 2 #slant path from H1 to H2, use RECORD 3.2
    noprint = 1#selects short printout
    nmol = 7#number of molecular species
    ipunch = 1# layer data written to unit ITAPE7)PU (TAPE7)
    h2o_sf = 1.0#Scaling factor for H2O
    co2_sf = 1.0#Scaling factor for CO2
    o3_sf = 1.0#Scaling factor for O3
    co_sf = 1.0#Scaling factor for CO
    ch4_sf = 1.0#Scaling factor for CH4
    n2o_sf = 1.0#Scaling factor for N2O
    o2_sf = 1.0#Scaling factor for O2
    ccl4_sf = 0.1105#Scaling factor for CCL4
    f11_sf = 0.2783#Scaling factor for F11
    f12_sf = 0.5027#Scaling factor for F12
    dptmin = 0.0002#minimum molecular optical depth below which lines will be rejected
    dptfac = 0.001#factor multiplying molecular continuum optical depth to determine optical depth below which lines will be rejected
    nmol_scal= 0#NMOL_SCAL is the highest molecule number for which scaling will be applied
    JCHARP = 'A'#Unit for pressure (A: mb, B: atm, C: torr)
    JCHART = 'A'#Unit for temperature (A: K, B: °C)
    JCHAR  = JCHAR#'{}444444'.format(hmd_unit)#Units for trace gases 
    #(A: volume mixing ratio (ppmv), B: number density (cm-3), C: mass mixing ratio (g/kg), 
    # D: mass density (gm-3), E: partial pressure (mb), F: dew point temperature (K) [only H2O], 
    # G: dew point temperature (°C) [only H2O], H: relative humidity (%) [only H2O]))
    ixmols = 3#number of cross-section molecules to be inputed (maximum of 35)
    iprfl = 0#user input profile
    ixsbin = 0#corss-sections convolved with pressure
    
    ####################
    # Write Record 1.2 #
    ####################    
    rec_1_1  = '$ LBLRTM run for TCWret'
    
    ####################
    # Write Record 1.2 #
    ####################
    rec_1_2  = ' HI={:1d}'.format(ihirac)
    rec_1_2 += ' F4={:1d}'.format(ilblf4)
    rec_1_2 += ' CN={:1d}'.format(icntnm)
    rec_1_2 += ' AE={:1d}'.format(iaersl)
    rec_1_2 += ' EM={:1d}'.format(iemit)
    rec_1_2 += ' SC={:1d}'.format(iscan)
    rec_1_2 += ' FI={:1d}'.format(ifiltr)
    rec_1_2 += ' PL={:1d}'.format(iplot)
    rec_1_2 += ' TS={:1d}'.format(itest)
    rec_1_2 += ' AM={:1d}'.format(iatm)
    rec_1_2 += ' MG={:1d}'.format(imrg)
    rec_1_2 += ' LA={:1d}'.format(ilas)
    rec_1_2 += ' MS=0'
    rec_1_2 += ' XS={:1d}'.format(ixsect)
    rec_1_2 += ' {:4d}'.format(mpts)
    rec_1_2 += ' {:4d}'.format(npts)
    rec_1_2 += '   00   00'
    if icntnm == 6:
        rec_1_2 += "\n {:1d} {:1d} {:1d} {:1d} {:1d} {:1d} {:1d}".format(XSELF, XFRGN, XCO2C, XO3CN, XO2CN, XN2CN, XRAYL)

    ####################
    # Write Record 1.3 #
    ####################
    rec_1_3  = '{:10.3f}'.format(wnum1)
    rec_1_3 += '{:10.3f}'.format(wnum2)
    rec_1_3 += '{:10.3f}'.format(resolution)
    rec_1_3 += 25*' '
    rec_1_3 += '{:10.4f}'.format(dptmin)
    rec_1_3 += '{:10.3f}'.format(dptfac)
    rec_1_3 += 29*' '
    rec_1_3 += '{:1d}'.format(nmol_scal)
    if nmol_scal > 0:
        rec_1_3 += '\n'
        for ii in range(nmol_scal):
            rec_1_3 += '1'
        rec_1_3 += '\n'
        rec_1_3 += '{:15.7E}'.format(h2o_sf)
        rec_1_3 += '{:15.7E}'.format(co2_sf)
        rec_1_3 += '{:15.7E}'.format(o3_sf)
        rec_1_3 += '{:15.7E}'.format(n2o_sf)
        rec_1_3 += '{:15.7E}'.format(co_sf)
        rec_1_3 += '{:15.7E}'.format(ch4_sf)
        rec_1_3 += '{:15.7E}'.format(o2_sf)

    ####################
    # Write Record 3.1 #
    ####################  
    rec_3_1  = '{:>5d}'.format(model_atm)
    rec_3_1 += '{:>5d}'.format(itype)
    rec_3_1 += '{:>5d}'.format(inlayers)
    rec_3_1 += '{:>5d}'.format(1)
    rec_3_1 += '{:>5d}'.format(noprint)
    rec_3_1 += '{:>5d}'.format(nmol)
    rec_3_1 += '{:>5d}'.format(ipunch)
    
    ####################
    # Write Record 3.2 #
    ####################  
    rec_3_2  = '{:10.3f}'.format(zz[0])
    rec_3_2 += '{:10.3f}'.format(zz[-1])
    rec_3_2 += '{:10.3f}'.format(view_angle)    
    
    ####################
    # Write Record 3.3 #
    ####################  
    rec_3_3 = ''    
    for i in range(len(zz)):
        rec_3_3 += '{:10.3f}'.format(zz[i])
        if((i+1) %8 == 0 and i+1 != len(zz)):
            rec_3_3 += '\n'
            
    ####################
    # Write Record 3.4 #
    ####################    
    rec_3_4  = '{:5d}'.format(inlayers)
    rec_3_4 += ' Atmospheric layers'
    
    ############################
    # Write Record 3.5 and 3.6 #
    ############################       
    rec_3_5_3_6 = ''
    for ii in range(inlayers):
        rec_3_5_3_6 += '{:10.3f}'.format(zz[ii])
        rec_3_5_3_6 += '{:10.3f}'.format(pp[ii])
        rec_3_5_3_6 += '{:10.3E}'.format(tt[ii])
        rec_3_5_3_6 += '     {}'.format(JCHARP)
        rec_3_5_3_6 += '{}'.format(JCHART)
        rec_3_5_3_6 += '   {}\n'.format(JCHAR)
        rec_3_5_3_6 += '{:10.3E}'.format(ww[ii])
        for tg in trace_gas:
            rec_3_5_3_6 += '{:10.3E}'.format(tg[ii])
        #rec_3_5_3_6 += '{:10.3f}'.format(o3[ii])
        #rec_3_5_3_6 += '{:10.3f}'.format(n2o[ii])
        #rec_3_5_3_6 += '{:10.3f}'.format(co[ii])
        #rec_3_5_3_6 += '{:10.3f}'.format(ch4[ii])
        #rec_3_5_3_6 += '{:10.3f}'.format(o2[ii])
        rec_3_5_3_6 += '\n'
        
    ####################
    # Write Record 3.7 #
    ####################   
    rec_3_7  = '{:5d}'.format(ixmols)
    rec_3_7 += '{:5d}'.format(iprfl)
    rec_3_7 += '{:5d}  The following cross-sections were selected:\n'.format(ixsbin)
    rec_3_7 += 'CCL4      F11       F12\n' #Names of molecules
    rec_3_7 += '{:5d}    0 XS 1995 UNEP values\n'.format(2)
    for ii in [0, len(zz)-1]:
        rec_3_7 += '{:10.3f}     AAA\n'.format(zz[ii])
        rec_3_7 += '{:10.3E}'.format(ccl4_sf/1e3)
        rec_3_7 += '{:10.3E}'.format(f11_sf/1e3)
        rec_3_7 += '{:10.3E}\n'.format(f12_sf/1e3)

    ##############################
    # Write TAPE5 (LBLRTM-Input) #
    ##############################
    with open(tape5, 'w') as tape5_f:
        tape5_f.write(rec_1_1 + '\n')
        tape5_f.write(rec_1_2 + '\n')
        tape5_f.write(rec_1_3 + '\n')
        tape5_f.write(rec_3_1 + '\n')
        tape5_f.write(rec_3_2 + '\n')
        tape5_f.write(rec_3_3 + '\n')
        tape5_f.write(rec_3_4 + '\n')
        tape5_f.write(rec_3_5_3_6)
        if ixsect == 1:
            tape5_f.write(rec_3_7)
        tape5_f.write('-1\n')
        tape5_f.write('%%%\n')

    return True

if __name__ == "__main__":
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
         0.739904402865, 0.660337703568,  0.58818380923])
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
    create_TAPE5(z, p, t, q, tape5='tp5_mod', atm=4, hmd_unit="C", wnum1=500.0, wnum2=1500.0, co2=523*np.ones(len(z)))