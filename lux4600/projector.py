import socket
import records
from img import Strip
from seq import Sequencer


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
            try:
                msg = self.send(check.bytes())
            except socket.error:
                print(socket.error)
                print("Connection unsuccessful.")
                return False
            
            if msg is None:
                return False
            else:
                print(msg)
                print(check.reply(msg[0]))

        print("Connection successful!")
        return True
    
    def send_strip(self, strip:Strip):
        """Sends an image to the projector to be stored at position inum.

        Args:
            img: A PIL Image object to be sent to the projector.
            inum: The inum of the image to be sent.

        Returns:
            None
        """


        # Set into reset mode and prime for image receiving
        init_messages = [
            records.SetImageType(4), # 4 = 1-bit grayscale
            records.SetInumSize(strip.height), # Set the inum size to the height of the image, i.e. the number of rows in the image
            records.ResetSeqNo(), # Reset the sequencer number
            records.SetSequencerState(1, False), # Halt the sequencer
            records.SetSequencerState(2, True) # Set the sequencer to reset mode
        ]

        for msg in init_messages:
            reply = self.send(msg.bytes())
            print(msg.reply(reply[0]))

        # Send image
        packets = strip.to_packets(lines_per_packet=6) # TODO
        
        count = 0 # TODO: get rid of this BS variable. Need something cleaner

        for _, packet in enumerate(packets):
            
            self.client_socket.sendto(packet, (self.SERVER_IP, self.IMAGE_DATA_PORT))
            count += 1

        print(f"Sent {count} packets, data length: {len(packet) - 14} per packet")

        # Request out-of-sequence packets
        reply = self.send(records.RequestSeqNoError().bytes())
        
        out_of_seq_packet = int.from_bytes(reply[0][5:], byteorder='big') + 1

        if out_of_seq_packet == count:
            print("No out of sequence packets")
        else:
            print(records.RequestSeqNoError().reply(reply[0]))
            raise RuntimeError(f"Out of sequence packet: {out_of_seq_packet}")
        
        self.send(records.SetSequencerState(2, False).bytes()) # Take sequencer out of reset mode
        
        return

    
    def send_sequencer(self, sequencer:Sequencer):
        """
        Sends sequence packets to the client socket.

        Args:
            sequencer: The sequence packets to be sent.
        """
        packets = sequencer.packets

        init_messages = [
            records.ResetSeqNo(), # 4 = 1-bit grayscale
            records.SetSequencerState(1, False), # Set the inum size to the height of the image, i.e. the number of rows in the image
            records.SetSequencerState(2, True), # Reset the sequencer number
        ]

        for msg in init_messages:
            reply = self.send(msg.bytes())
            print(msg.reply(reply[0]))

        for packet in packets:
            reply = self.send(packet)
            print(msg.reply(reply[0]))
            
        self.send(records.SetSequencerState(2, False).bytes())

    def check_sequencer_error(self):

        """Check for sequencer errors and print the error message if any."""

        reply = self.send(records.RequestSeqFileErrorLog().bytes())
        
        for _ in reply: print(_)
        
            
    
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
    

    



        
    

    

