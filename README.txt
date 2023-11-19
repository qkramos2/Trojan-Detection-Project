(v1.2) Updated Trojan Detection Methodology:


The first thing done to detect the trojan is to find a pattern of 1's and 0's
that detects the trojan. The purpose of figuring out at least one input that
causes the trigger is to then individually toggle bits in hopes to find the
individual bits that create the trigger.

To find this trigger input, the pattern_identifier sends a total of 500 inputs
consisting of "divide and conquer" pattern of inputs, pseudo-generation of
inputs, and the rest of the inputs are randomly and uniquely generated inputs.

In hopes to find multiple hits, these list of inputs can be compared to each
other to see what bits each input has in common and then individually analyze
the common bits by toggling a bit at a specific position. Running this to the
board should cause all misses if the specific bit is apart of the trigger
sequence.

The above functionality is completed by the find_trigger_bits function which
takes the hit inputs and returns the trigger string.

The other fpga_out function is responsible for flashing the trojan and safe
bitstreams and returning a list of booleans to indicate what inputs caused
hits and which caused misses.

The last function strings all the other functions together and serves as a main
function for the detection.py file.


Analysis:


Based on whether or not the trigger is successfully identified, the analysis is
a simple analysis on whether or not the trojan is a simple combinational trojan
or a weak sequential trojan. It then goes into depth on what the payload affects
given a list of golden outputs compared to their trojan outputs.


Flashing:


The board is flashed via a custom .tcl script which runs hardware manager and
programs the bitstream given the bitstream file path.


py_2_FPGA:


The main file that holds the main callable function that calls the analysis
and detection functions to run and detect and analyze the trojan and the
payload respectively.