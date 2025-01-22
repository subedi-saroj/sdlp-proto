import socket
import time

# Define the server IP address and port
SERVER_IP = '192.168.0.10'
SERVER_PORT = 52985
IMAGE_DATA_PORT = 52986

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# various responses from the server
OK = b'\x00\x06\x01\xf5\x00\x00'

# command dictionary
command_dict = {
    'reset_sequence_number': b'\x00\x04\x00\x70',
    'set_image_type_to_1': b'\x00\x06\x00\x67\x00\x01',
    'set_image_type_to_4': b'\x00\x06\x00\x67\x00\x04',
    'request_image_type': b'\x00\x04\x01\x2F',
    'set_inum_size_1080': b'\x00\x06\x00\x66\x04\x38',
    'set_inum_size_20000': b'\x00\x06\x00\x66\x4E\x20',
    'start_sequencer': b'\x00\x06\x00\6A\x01\x01',
    'stop_sequencer': b'\x00\x06\x00\x6A\x01\x00',
    'set_sequencer_in_reset_state': b'\x00\x06\x00\x6A\x02\x01',
    'take_sequencer_out_of_reset': b'\x00\x06\x00\x6A\x02\x00',
    'run_sequencer': b'\x00\x06\x00\x6A\x01\x01', #00 06 00 6A 01 01
    'set_image_type_to_1': b'\x00\x06\x00\x67\x00\x01',
    'set_image_type_to_4': b'\x00\x06\x00\x67\x00\x04',
    'request_image_type': b'\x00\x04\x01\x2F',
    'request_software_sync': b'\x00\x04\x01\x40'
}

# print bytes in hex format
def print_bytes(data):
    hex_string = " ".join([f"{byte:02X}" for byte in data])
    print(hex_string)

# read the bytes from a .txt file and splits it into 1440 byte chunks
def split_file_into_chunks(file_path, chunk_size=1440):
    with open(file_path, 'rb') as file:
        chunk_number = 1
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk_number, chunk
            chunk_number += 1

# submit bytes to the server and return response
def send_bytes(data):
    # Send data to the server
    client_socket.sendto(data, (SERVER_IP, SERVER_PORT))

    # Receive response from the server
    response, server_address = client_socket.recvfrom(1024)

    if response == OK:
        print("Received OK")
    elif response[:4] == b'\x00\x06\x01\xf5':
        print("ERROR: Received error response from server: ", response.hex())
    else:
        print("Received response from server:", end=' ')
        print_bytes(response)

    return response

file_path = r"C:\Users\dmale\OneDrive\Desktop\Personal\Active Research\DMPM Lab\Visitech Scrolling DLP Projector\libluxbeam-master\examples\rle_demo\1920x20000-1bit.bmp"

def read_bmp_file(file_path):
    with open(file_path, 'rb') as file:
        # Skip bitmap header (54 bytes for typical BMP)
        file.seek(130)
        bmp_data = file.read()
        print(len(bmp_data))
    return bmp_data

def split_into_packages(data, lines_per_package, line_offset) -> list:
    packages = []
    lines = len(data) // 240  # Assuming each line is 1920 pixels wide and 1 bit per pixel = 240 bytes
    num_packages = lines // lines_per_package
    for i in range(num_packages):
        start = i * lines_per_package * 240
        end = (i + 1) * lines_per_package * 240
        offset = line_offset*i
        package = b'\x05\xAE\x00\x68' + i.to_bytes(2, byteorder='big') + offset.to_bytes(8, byteorder='big') + data[start:end]
        packages.append(package)
    return packages

def send_image(packages):
    print("Number of packages: ", len(packages))
    print("Packet size: ", len(packages[0][14:]))
    for package in packages:
        client_socket.sendto(package, (SERVER_IP, IMAGE_DATA_PORT))

def start_sequencer():
    r = send_bytes(command_dict['take_sequencer_out_of_reset']) # take sequencer out of reset
    if r != OK: print(r)
    r = send_bytes(command_dict['run_sequencer']) # start sequencer
    if r != OK: print(r)

#-------------------------------------    
# Scroll a 1920x20000 image
#-------------------------------------
        
# prepare the projector
r = send_bytes(command_dict['set_image_type_to_4']) # set image type to bitmap
if r != OK: print(r)
r = send_bytes(command_dict['set_inum_size_20000']) # set inum size to 1920x20000
if r != OK: print(r)
r = send_bytes(command_dict['reset_sequence_number']) # reset sequence number
if r != OK: print(r)
r = send_bytes(command_dict['disable_sequencer']) # disable sequencer
if r != OK: print(r)
r = send_bytes(command_dict['set_sequencer_in_reset_state']) # set sequencer in reset state
if r != OK: print(r)


# send the image
line_offset = 5
packages = split_into_packages(read_bmp_file(file_path), line_offset, line_offset)
send_image(packages)

print("Done sending image")
r = send_bytes(b'\x00\x04\x01\x37') # Do a request for out-of-sequence packets
OOS_packet = int.from_bytes(r[5:], byteorder='big') + 1
print("Out of sequence packet: ", OOS_packet)

if (OOS_packet == len(packages)):
    print("No out of sequence packets")
    x = False
elif (OOS_packet == 1):
    x = False
else:
    x = True

while x:
    x = (input("continue y/n: ") == 'y')
    if x:
        send_image(packages[OOS_packet:])
        print("Sent out of sequence packets")
        r = send_bytes(b'\x00\x04\x01\x37') # Do a request for out-of-sequence packets
        print_bytes(r)
        OOS_packet = int.from_bytes(r[5:], byteorder='big') + 1
        print("Out of sequence packet: ", OOS_packet)


x = input("Press q to quit, stop to stop, start to start: ")

while x != 'q':
    if x == 'stop':
        r = send_bytes(command_dict['stop_sequencer']) # stop sequencer
        if r != OK: print(r)
    elif x == 'start':
        start_sequencer()
    x = input("Press q to quit, stop to stop, start to start: ")

# Close the socket
client_socket.close()