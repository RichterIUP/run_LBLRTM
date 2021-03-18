# run\_LBLRTM.py

Python script for creating TAPE5 input of LBLRTM and calling LBLRTM. run\_LBLRTM.py is tested with LBLRTM v12.8 and part of TCWret.

## Software requirements

run\_LBLDIS.py is written in Python and tested with Python 3.8.5. Necessary libraries: 

- Numpy 
- Pandas

Python and several scientific libraries are assembled in [Anaconda](https://www.anaconda.com/).

LBLRTM must be already compiled on your system to use run\_LBLDIS.py

## Usage of run\_LBLDIS.py

```sh
python3 run_LBLRTM.py <OUTPUT_PATH>
```

run\_LBLRTM.py searches for input.dat and atm\_grid.csv in your run directory. 

## input.dat

input.dat is an ASCII file containing the parameters and paths which are necessary to use run\_LBLRTM.py. It is explained using the example input.dat.example

- Line 1: Lower limit of spectral interval
- Line 2: Upper limit of spectral interval
- Line 3: Name of LBLRTM input file
- Line 4: Path to LBLRTM directory (containing bin/BINARY\_OF\_LBLRTM)
- Line 5: Path to LBLRTM output directory

## atm\_grid.csv

This file is read using Pandas, therefore the order of columns does not matter. The file must contain following columns (case sensitive):

- altitude(km)
- ch4(ppmv)
- co(ppmv)
- co2(ppmv)
- humidity(%)
- n2o(ppmv)
- o2(ppmv)
- o3(ppmv)
- pressure(hPa)
- temperature(K)

## Output

Optical depths of trace gases
