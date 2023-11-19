"""
========================================================================================
File Name:
    flash.py

File Description:
    Flashes the board with the inputted bitstream file path (safe / trojan)

Author:
    Quentin Ramos II
========================================================================================
"""

# --- Import statements ---
import subprocess
import os

# --- Global Paths ---

# RIT Paths:
#vivado_file     = 'C:\\Xilinx\\Vivado\\2019.1\\bin\\vivado.bat'
#tcl_file_path   = 'D:\\HWSec\\Projects\\Project1\\PycharmProject\\script.tcl'

# Quentin's PC Paths
vivado_file     = 'C:\\Custom\\Xilinx\\Vivado\\2023.2\\bin\\vivado.bat'
tcl_file_path   = 'F:\\HWSec\\Projects\\Project1\\PycharmProject\\script.tcl'

# Quentin's Laptop Paths:
#vivado_file    = 'D:\\Programming\\Vivado\\Vivado\\2023.2\\bin\\vivado.bat'
#tcl_file_path  = 'F:\\HWSec\\Projects\\Project1\\PycharmProject\\script.tcl'

# TODO if you're trying to run the code, comment out the paths and paste your own
#   the vivado file needs to point to the batch file and the tcl script in the
#   project needs to be pointed to as well with double back slashes!

def flash(bitstream_path):

    os.environ["BITSTREAM_PATH"] = bitstream_path

    # Execute the Tcl script with the specified bitstream file
    subprocess.run([
        vivado_file,
        '-mode',
        'tcl',
        '-source',
        tcl_file_path
    ], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, shell=True)
