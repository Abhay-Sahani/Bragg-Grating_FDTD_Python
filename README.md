# Bragg-Grating_FDTD_Python
This repository contains a Python version of my Bragg grating simulation—translated from Lumerical `.lsf` to a script leveraging `lumapi.FDTD`, NumPy, and Matplotlib. It automates simulation setup, execution, data extraction, and plotting.
# Bragg Grating FDTD Simulation

This repository translates a Lumerical `.lsf` script for Bragg grating simulation into Python—fully automating geometry creation, simulation, and visualization using `lumapi.FDTD`.

## 🔧 Features

- Builds the full Bragg grating structure with substrate, waveguides, corrugations, sources, and monitors
- Runs a 3D FDTD simulation within Python
- Extracts transmission (T) and reflection (R) spectra
- Plots spectral responses and saves raw data in CSV format
