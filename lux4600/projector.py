import records
import socket

class Projector:
    def __init__(self, server_ip, server_port, image_data_port, timeout=10):

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.SERVER_IP = server_ip
        self.SERVER_PORT = server_port
        self.IMAGE_DATA_PORT = image_data_port
        self.client_socket.settimeout(timeout)
    
    def send(self, bytes):
        '''Send a message to the projector and return the response.'''
        try:

            self.client_socket.sendto(bytes, (self.SERVER_IP, self.SERVER_PORT))
            reply = self.client_socket.recvfrom(1024)

        except socket.timeout:
            print("Timeout :(")
            return None
        
        except socket.error as e:
            print("Socket error: ", e)
            return None
        
        return reply

    def check_connection(self):

        checks = [
            records.RequestInumSize(),
            records.RequestImageType()
        ]
        
        for check in checks:
            msg = self.send(check.bytes())
            if msg is None:
                return False
            else:
                print(msg)
                print(check.reply(msg[0]))

        print("Connection successful!")
        return True

    def split_sequence_into_packets(self, file_path, chunk_size=1440):
        
        packets = []
        with open(file_path, 'rb') as file:
            
            for chunk in self._read_chunk(file, chunk_size):
                    packets.append(chunk)
        
        return packets

    def _read_chunk(self, file, chunk_size):
        
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk
    
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
    
    def start_sequencer(self):
        self.send(records.SetSequencerState(2, False).bytes())
        self.send(records.SetSequencerState(1, True).bytes())
        return

    def stop_sequencer(self):
        r = self.send(records.SetSequencerState(1, False).bytes())
    
    def reset_projector(self):
        r = self.send(records.SetSequencerState(2, True).bytes())

    def enable_sequencer(self):
        r = self.send(records.SetSequencerState(2, False).bytes())
    

    



        
    

    

