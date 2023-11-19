"""
========================================================================================
File Name:
    analysis.py

File Description:
    Given the trigger to the trojan, analyze the payload and how it's affecting
    the functionality of the given FPGA.

Author:
    Quentin Ramos II & Robbie Riviere
========================================================================================
"""

# --- Global Variables ---



# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


def analysis(trigger, hits_array):

    # If the returned trigger is all X's then the trigger couldn't be obtained:
    if "0" in trigger or "1" in trigger:
        trojan_desc = ( "The detected trojan on the circuit is a combinational trojan.\n\t"
                        "The outputs of the trojan are directly altered by the triggered\n\t"
                        "inputs and soely based on the trigger inputs.")
    else:
        trojan_desc = ( "The analyzed trojan is not combinational and is sequential.\n\t"
                        "Due to this, the sequential trojan is much more complex and\n\t"
                        "side channel analysis would have to be carried out in order\n\t"
                        "to correctly identify the trojan.")

    # Look at the hits_array and determine how the trojan works:
    results = []
    for outputs in hits_array:
        golden_out = int(outputs[0],16)
        trojan_out = int(outputs[1],16)
        results.append(bin(golden_out ^ trojan_out)[2:])

    payload = ("The sequential trojan is complex and the output bits are constantly changing\n\t"
               "based on factors other than the trigger input")
    first_element = results[0]
    set_high_bits = [i for i, bit in enumerate(reversed(first_element)) if bit == '1']

    # If all the results are the same, they're toggling the same bit:
    if all(element == first_element for element in results):
        payload = f"Ex: Golden output: 0x{hits_array[0][0]} | Trojan output: 0x{hits_array[0][1]}\n\t"
        if set_high_bits:
            payload += f"The triggered trojan affects the following: out[{', '.join(map(str, set_high_bits))}]"

    return trojan_desc, payload


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------