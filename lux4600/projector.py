import records, bmp, seq
import socket
from PIL import Image


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
            print("Timeout error.")
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
    
    def send_image(self, img:Image, inum:int=0):
        """Sends an image to the projector to be stored at position inum.

        Args:
            img: A PIL Image object to be sent to the projector.
            inum: The inum of the image to be sent.

        Returns:
            None
        """
        bmp_img = bmp.to_bmp(img)

        packets = bmp.bmp_to_packets(inum, 6, bmp_img)
        
        for packet in packets:
            self.client_socket.sendto(packet, (self.SERVER_IP, self.IMAGE_DATA_PORT))
    
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
    

    



        
    

    

