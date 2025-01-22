from ..Records import Records
import socket

class Projector:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.SERVER_IP = '192.168.0.10'
        self.SERVER_PORT = 52985
        self.IMAGE_DATA_PORT = 52986
        self.Records = Records

    def split_sequence_into_packets(self, file_path, chunk_size=1440):
        with open(file_path, 'rb') as file:
            packets = []
            while True:
                chunk = file.read(chunk_size)
                if not chunk: # if the chunk is empty, break the loop
                    break
                packets.append(chunk)
            return packets
    
    def read_bmp_file(self, file_path, size:int=1080):
        with open(file_path, 'rb') as file:
            s = len(file.read())
            size = size*240
            # Skip bitmap header (54 bytes for typical BMP)
            if s != size: file.seek(s-size)
            bmp_data = file.read()
            print("Total number of bytes loaded from image: ", len(bmp_data))
        return bmp_data


    #
    # The code below to be refined for clarity and efficiency
    #
    #
    def split_img_into_packets(self, inum: int, lines_per_packet: int, data: bytes) -> list:
        packets = []
        lines = len(data) // 240  # Assuming each line is 1920 pixels wide and 1 bit per pixel = 240 bytes
        num_packets = lines // lines_per_packet
        for i in range(num_packets):
            start = i * lines_per_packet * 240
            end = (i + 1) * lines_per_packet * 240
            offset = lines_per_packet*i
            packet = b'\x05\xAE\x00\x68' + i.to_bytes(2, byteorder='big') + inum.to_bytes(2, byteorder='big') + offset.to_bytes(6, byteorder='big') + data[start:end]
            packets.append(packet)
        return packets
    
    def send_image(self, packets):
        print("Number of packets: ", len(packets))
        print("Packet size: ", len(packets[0][14:]))
        print("Sending image to inum ", int.from_bytes(packets[0][6:8], byteorder='big'))
        for packet in packets:
            self.client_socket.sendto(packet, (self.SERVER_IP, self.IMAGE_DATA_PORT))
    #
    #
    #
    #
    #
    #        
    def send(self, bytes):
        self.client_socket.sendto(bytes, (self.SERVER_IP, self.SERVER_PORT))
        return self.client_socket.recvfrom(1024)
    
    def start_sequencer(self):
        self.send(Records.SetSequencerState(2, False).bytes())
        self.send(Records.SetSequencerState(1, True).bytes())
        return

    def stop_sequencer(self):
        r = self.send(Records.SetSequencerState(1, False).bytes())
    
    def reset_projector(self):
        r = self.send(Records.SetSequencerState(2, True).bytes())

    def enable_sequencer(self):
        r = self.send(Records.SetSequencerState(2, False).bytes())
    

    



        
    

    

