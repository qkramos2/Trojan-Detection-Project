# Parse the command line argument (bitstream file path) provided by Python
set bitstream_path $env(BITSTREAM_PATH)

# Check if a valid bitstream file path is provided
if {![info exists bitstream_path] || [string length $bitstream_path] == 0} {
    puts "Error: No bitstream file path provided."
    exit 1
}

# Open Hardware Manager in batch mode
# open_hw_manager <- ONLY WORKS ON HOME PC
open_hw
connect_hw_server

# Open Hardware Target
open_hw_target

# Set the device (Basys 3)
current_hw_device [get_hw_devices xc7a35t_0]
refresh_hw_device -update_hw_probes false [lindex [current_hw_device] 0]

# Load the specified bitstream file onto the device
set_property PROBES.FILE {} [current_hw_device]
set_property FULL_PROBES.FILE {} [current_hw_device]
set_property PROGRAM.FILE $bitstream_path [current_hw_device]
program_hw_devices [current_hw_device]
refresh_hw_device [current_hw_device]

# Close Hardware Manager
# close_hw_manager <- ONLY WORKS ON HOME PC
close_hw
exit