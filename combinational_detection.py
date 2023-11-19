"""
========================================================================================
File Name:
    combinational_detection.py

File Description:
    Given a programmable bitstream with an injected combinational hardware trojan, the
    given code finds the specific bit sequence to which the trojan is triggered.

Author:
    Quentin Ramos II
========================================================================================
"""


# --- Import statements ---
import math
import random
import serial
import flash
import datetime


# --------------------------- Global Variables -----------------------------
com_port    = ''
hit_array   = []
out_list    = []
baud_rate, bytes_read, input_size = 0,0,0
safe_file   = 'F:\\HWSec\\Projects\\Project1\\' # TODO Change for specific application
troj_file   = 'F:\\HWSec\\Projects\\Project1\\' # TODO Change for specific application
circuit     = ""
hex_format  = f''
# --------------------------------------------------------------------------


"""
Tries to find a generic pattern in trigger sequence by toggling specific 
  bits in a variety of ways (Divide & Conquer, Pseudo-generation, random)

UPDATED: Runs through all three methods and tries to collect a variety of
  hits instead of coming across the first hit. This in turn will be able
  to run bit_checker and bit_identifier into a single function.
  
  Will run through divide & conquer, pseudo-generation, and randomly
  generate 100 unique samples that haven't been sampled.

inputs:
    input_size: size of the input to go into the FPGA
    round_num: basically how many sections we divide the input up into

output:
    the pattern identified input
"""
def pattern_identifier():

    # Sub function that standardizes the input array for the board
    # -------------------------------------------------------------

    def standardizer(bin_string, array):
        binary_int = int(bin_string, 2)
        flipped_int = ~binary_int & (pow(2, input_size) - 1)
        if format(binary_int, hex_format) not in array:
            array.append(format(binary_int, hex_format))
            array.append(format(flipped_int, hex_format))

    # -------------------------------------------------------------

    # ------------ Divide & Conquer ------------

    # Evenly divide 0's and 1's across input:
    input_array = [format(0, hex_format), format(pow(2, input_size) - 1, hex_format)]
    for i in range (1,int(math.log2(input_size))):

        # Divide up the input with 0's and 1's:
        divider = input_size // int(pow(2, i - 1))
        standardizer(("".join("0" * (divider // 2) + "1" * (divider // 2)
                    for _ in range(math.ceil(input_size / i))))[:input_size], input_array)

    # ------------ Pseudo-generation ------------

    # Generates groups of 1's and 0's the size of the loop incrementer
    for i in range(1,input_size):
        standardizer(("".join("0" * i + "1" * i
                    for _ in range(math.ceil(input_size / i))))[:input_size], input_array)

    # ------------ Random Generation ------------

    # Randomly generate 500 unique binary inputs of the given length:
    size = len(input_array)
    while len(input_array) < size + 2000:
        standardizer(''.join(random.choice('01')
                    for _ in range(input_size)), input_array)

    # Check all the inputs and return an array of hits:
    hit_inputs = []
    bools = fpga_out(input_array,False)
    for i in range(len(bools)):
        if bools[i]:
            hit_inputs.append(input_array[i])

    # Print out all the inputs that caused hits:
    print("Inputs that caused hits:")
    for i in range(0,len(hit_inputs),3): print("\t" + ', '.join(map(str, hit_inputs[i:i+3])))

    # Return the list of inputs that caused hits:
    return hit_inputs


"""
Given the specific bit pattern from the pattern_identifier function it
    hones in on the specific bit causing the trigger

inputs:
    trigger_inputs: all the hit inputs from the previous function

outputs:
    the index of the bit apart of the trigger
"""
def find_trigger_bits(trigger_inputs):

    # Keep track of the trigger string:
    trigger_string = ""

    # Go through each bit individually:
    for i in range(input_size):

        # Boolean breaker, breaks and moves to next index if true:
        breaker = False

        # First, check if the bit value at the index is the same in all the hits:
        bit_value_checker = list(bin(int(trigger_inputs[0], 16))[2:].zfill(input_size))[i]
        for trigger_input in trigger_inputs:
            bit_val = list(bin(int(trigger_input, 16))[2:].zfill(input_size))[i]
            if bit_val != bit_value_checker:
                breaker = True
                break

        # If this didn't pass the first test, move onto the next bit
        if not breaker:

            # Debug statements:
            print(f"------- Hit inputs have matching values @ bit {(input_size - 1) - i} -------")
            print(f"\nAnalyzing Bit {(input_size - 1) - i} further:\n")

            # Second, flip the bit at the specified index, if all are misses then
            #   it's a part of the trigger:
            altered_bit_array = []
            bit_to_flip = list(bin(int(trigger_inputs[0], 16))[2:].zfill(input_size))[i]
            for trigger_input in trigger_inputs:
                binary_string = list(bin(int(trigger_input, 16))[2:].zfill(input_size))

                # If the bit at the specified position is a 0, switch it to a 1 and append to list
                if binary_string[i] == '0':
                    binary_string[i] = '1'
                    altered_bit_array.append(format(int("".join(binary_string), 2), hex_format))
                    binary_string[i] = '0'

                # Else the bit at the specified position is a 1 and switch it to a 0 and append to list
                else:
                    binary_string[i] = '0'
                    altered_bit_array.append(format(int("".join(binary_string), 2), hex_format))
                    binary_string[i] = '1'

            # Run the inputs into the board and if they're all misses append
            #   the bit value as a part of the trigger to the trigger string:
            bool_list = fpga_out(altered_bit_array, True)
            character = "X" if any(bool_list) else bit_to_flip
            if character != "X":
                print(f"\n>>> Bit {(input_size - 1) - i} apart of trigger! <<<\n")
            else:
                print()
            trigger_string += character

        # Ensure to add an "X" to the trigger string:
        else:
            trigger_string += "X"

    # Return the trigger string:
    return trigger_string


"""
Compare function that compares the trojan bitstream output to the golden
chip output and returns true if matching and false if not

inputs:
    fpga_in: the hex input going into the fpga

output:
    true if a 'hit' occurs  / trojan trigger triggered
    false if both are equal / trojan trigger not triggered
"""
def fpga_out(data_to_send, isPrint):
    # Keep track of safe outputs & trojan outputs & if they're equal:
    golden_out, trojan_out, bool_list = [], [], []

    # Pad the input for c432 test case:
    fpga_input = ["0" + byte if circuit == "C432" or
                                circuit == "C5315" or
                                circuit == "Challenge (DES3)"
                    else byte for byte in data_to_send]

    # Run inputs through safe bitstream:
    flash.flash(safe_file)
    ser_golden = serial.Serial(com_port, baud_rate, timeout=1)
    if ser_golden.is_open:
        for fpga_in in fpga_input:
            ser_golden.write(bytes.fromhex(fpga_in[2:] if fpga_in[0:2] == "0x" else fpga_in))
            golden_out.append(ser_golden.read(bytes_read))
        ser_golden.close()

    # Runs input through trojan bitstream:
    flash.flash(troj_file)
    ser_trojan = serial.Serial(com_port, baud_rate, timeout=1)
    if ser_trojan.is_open:
        for fpga_in in fpga_input:
            ser_trojan.write(bytes.fromhex(fpga_in[2:] if fpga_in[0:2] == "0x" else fpga_in))
            trojan_out.append(ser_trojan.read(bytes_read))
        ser_trojan.close()

    # Fill in boolean list:
    bool_list = [golden != trojan for golden, trojan in zip(golden_out, trojan_out)]

    # Debug Print Statements:
    for i in range(len(data_to_send)):
        golden_string = ''.join(f'{byte:02X}' for byte in golden_out[i])
        trojan_string = ''.join(f'{byte:02X}' for byte in trojan_out[i])
        # 'Miss' print statement
        if golden_out[i] == trojan_out[i] and isPrint:
            print("\t"+f"{data_to_send[i]}: golden: 0x{golden_string} | trojan: 0x{trojan_string} <- (MISS)")
        # 'Hit' print statement
        elif golden_out[i] != trojan_out[i]:
            hit_array.append(data_to_send[i])
            out_list.append([golden_string, trojan_string])
            if isPrint:
                print("\t"+f"{data_to_send[i]}: golden: 0x{golden_string} | trojan: 0x{trojan_string} <- (HIT)")

    return bool_list


"""
Actual trojan detection function that detects the trigger of the trojan

inputs:
    number of bits in the input

outputs:
    string of the trigger bits
"""
def trojan_detection(output_bytesize, com, baud, test):

    # Set global variables:
    global input_size, circuit, safe_file, troj_file, hex_format, com_port, baud_rate, bytes_read

    # Set the COM port and baud rate:
    baud_rate = baud
    com_port  = com
    bytes_read = output_bytesize

    # Set input_size & other strings:
    if bytes_read == 1:
        input_size  = 36
        circuit     = "C432"
        safe_file   += 'c432_train\\c432_safe.bit'
        troj_file   += 'c432_train\\c432_trojan.bit'
    elif bytes_read == 4 and test == 0:
        input_size  = 32
        circuit     = "C6288"
        safe_file   += 'c6288_train\\c6288_safe.bit'
        troj_file   += 'c6288_train\\c6288_trojan.bit'

    # TEST TROJANS:
    elif bytes_read == 4 and test == 1:
        input_size  = 41
        circuit     = "C499"
        safe_file   += 'c499_test\\c499_1.bit'
        troj_file   += 'c499_test\\c499_2.bit'
    elif bytes_read == 4 and test == 2:
        input_size  = 33
        circuit     = "C1908"
        safe_file   += 'c1908_test\\c1908_1.bit'
        troj_file   += 'c1908_test\\c1908_2.bit'
    elif bytes_read == 4 and test == 3:
        input_size  = 32
        circuit     = "FIR"
        safe_file   += 'FIR_test\\FIR_safe.bit'
        troj_file   += 'FIR_test\\FIR_trojan.bit'

    elif bytes_read == 15:
        input_size  = 178
        circuit     = "C5315"
        safe_file   += 'c5315_train\\c5315_safe.bit'
        troj_file   += 'c5315_train\\c5315_trojan.bit'
    elif bytes_read == 9:
        input_size  = 236
        circuit     = "Challenge (DES3)"
        safe_file   += 'challenge_des3_train\\des3_safe.bit'
        troj_file   += 'challenge_des3_train\\des3_T1.bit'

    # Formater for board readability:
    hex_format = f'0{math.ceil(input_size / 4) + (1 if input_size % 8 == 1 else 0)}x'

    # Start Time:
    print(("|" * 84) + "\n" + (" " * 20) + ">>> Start Time: " + (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " <<<")

    # Go about finding the pattern:
    print("\n" + ("=" * 84) + "\nStep 1: " + circuit + " Pattern Identification:\n" + ("=" * 84) + "\n")
    trigger_inputs = pattern_identifier()

    # Split into groups and find the trigger:
    print("\n" + ("=" * 84) + "\nStep 2: " + circuit + " Individual Trigger Bit Identification:\n" + ("=" * 84) + "\n")
    trigger = find_trigger_bits(trigger_inputs)

    # End Time:
    print((" " * 20) + ">>> Elapsed Time: " + (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " <<<" + "\n" +("|" * 84))

    # Return Trigger:
    return trigger, input_size, circuit, out_list
