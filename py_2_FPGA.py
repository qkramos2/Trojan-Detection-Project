"""
========================================================================================
File Name:
    py_2_FPGA.py

File Description:
    Given a programmable bitstream with an injected logical hardware trojan, the given
    code finds the specific bit sequence to which the trojan is triggered and analyzes
    the payload that the trojan utilizes.

    TODO: BEFORE RUNNING CHECK EACH TODO STATEMENT IN EACH FILE

Author:
    Quentin Ramos II & Robbie Riviere
========================================================================================
"""


# --- Import statements ---
import serial
import combinational_detection as cd
import analysis


# --- Global Variables ---
com_port = 'COM9'    # TODO change the com port of the FPGA device
output_bytesize = 4  # TODO change accordingly (C432  = 1 | C5315 = 15 | C6288 = 4 | DES3 = 9)
baud_rate = 115200
test = 1


"""
Given code to test FPGA and bitstream:
"""
def test_fpga():
    # Open the COM port
    ser = serial.Serial(com_port, baud_rate, timeout=1)
    if ser.is_open:
        try:
            while True:
                # Send data to the device
                data_to_send = input("Enter data to send: ")
                data_to_send = data_to_send[2:] if data_to_send[0:2] == "0x" else data_to_send
                data_bytes = bytes.fromhex(data_to_send)
                ser.write(data_bytes)

                # Read data from the FPGA
                received_data = ser.read(output_bytesize)

                # Convert the received bytes to a hexadecimal string
                hex_string = ''.join(f'{byte:02X}' for byte in received_data)

                # Compare the output to the reference file:
                print(f"Received data: 0x{hex_string}")

        except KeyboardInterrupt:
            pass
        finally:
            ser.close()
            print("Connection closed.")
    else:
        print(f"Failed to connect to {com_port}")


def main():

    # Trojan detection:
    trigger, input_size, circuit, hits = cd.trojan_detection(output_bytesize, com_port, baud_rate,test)
    trigger = "".join(trigger)

    # Trojan detection print statements:
    print("\n\n" + ("=" * 84)), print((" " * 34) + "Trojan Detection"), print("=" * 84)
    print("\nSpecified bitstream: " + circuit)
    print("\nDetected trojan trigger: " + trigger)
    print("\nTrigger bits and their associated value:")
    [print(f"\tin[{(input_size - 1) - i}] = {list(trigger)[i]}") for i in range(len(list(trigger))) if list(trigger)[i] != "X"],print()

    # Payload Analysis:
    trojan_desc, payload = analysis.analysis(trigger, hits)

    # Payload analysis print statements:
    print("=" * 84), print((" " * 34) + "Payload Analysis"), print("=" * 84)
    print("\nSpecified bitstream: " + circuit)
    print("\nTrojan Description: ")
    print("\t"+ trojan_desc)
    print("\nPayload Analysis: ")
    print("\t" + payload)


if __name__ == "__main__":
    main()