import socket
import struct
import records
from img import Strip
from seq import Sequencer
from rle import encode_rle_image_type5
import time


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
    
    def send_strip(self, strip:Strip, lines_per_packet:int=6):
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
        
        time_elapsed = time.time() # timing the upload time

        for msg in init_messages:
            reply = self.send(msg.bytes())
            print(msg.reply(reply[0]))

        # Send image
        packets = strip.to_packets(lines_per_packet) # TODO
        
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
        
        # Display timing information
        time_elapsed = time.time() - time_elapsed
        print(f"Time elapsed to send strip: {time_elapsed:.2f} seconds")

        return

    def send_image_rle(self, image, width: int, height: int, inum: int = 0, image_type: int = 5):
        """
        Send RLE-compressed binary image to the projector.

        Uses Visitech RLE Type 5 format (lb4k6) for Lux4600 hardware.
        Significantly reduces bandwidth compared to uncompressed transmission.

        Args:
            image: PIL Image (mode '1') or numpy array (binary 1-bit)
            width: Image width in pixels (typically 1920)
            height: Image height in pixels (typically 3240 for scrolling)
            inum: Image number slot (0-65535, default 0)
            image_type: Format type (default 5 = RLE with bit-swapping for Lux4600)

        Returns:
            None

        Raises:
            RuntimeError: If out-of-sequence packets detected during transmission
            ValueError: If image dimensions don't match specified width/height
        """
        # Initialize projector and set RLE mode
        init_messages = [
            records.SetImageType(image_type),  # 5 = RLE Type 5 (Lux4600 specific)
            records.SetInumSize(height),
            records.ResetSeqNo(),
            records.SetSequencerState(1, False),  # Halt sequencer
            records.SetSequencerState(2, True)    # Reset sequencer
        ]

        time_elapsed = time.time()

        for msg in init_messages:
            reply = self.send(msg.bytes())
            print(f"Init: {msg.reply(reply[0])}")

        # Encode image with RLE Type 5 compression
        print(f"Encoding image ({width}x{height}) with RLE Type 5...")
        encoded_rows = encode_rle_image_type5(image, width, height)

        # Calculate compression statistics
        uncompressed_size = (width // 8) * height
        compressed_size = sum(len(row) for row in encoded_rows)
        compression_ratio = compressed_size / uncompressed_size
        savings_percent = (1 - compression_ratio) * 100

        print(f"Compression: {uncompressed_size:,} → {compressed_size:,} bytes ({compression_ratio:.1%})")
        print(f"Bandwidth savings: {savings_percent:.1f}%")

        # Fragment RLE data into packets and send
        seq_no = 1
        packets_sent = 0
        max_data_per_packet = 8956  # Maximum UDP payload per spec

        for row_offset, row_data in enumerate(encoded_rows):
            # Build LoadImageData packet
            # Format: [tot_size: 2] [rec_id: 2] [seq_no: 2] [inum: 2] [offset: 4] [data: var]
            
            # Calculate offset (in lines from start of inum)
            offset = row_offset
            
            # Create payload: seq_no (2) + inum (2) + offset (4) + row_data
            payload = (
                seq_no.to_bytes(2, byteorder='big') +
                inum.to_bytes(2, byteorder='big') +
                offset.to_bytes(4, byteorder='big') +
                row_data
            )

            # Calculate total size: 2 (tot_size) + 2 (rec_id) + payload
            tot_size = 4 + len(payload)

            # Build complete packet
            packet = (
                tot_size.to_bytes(2, byteorder='big') +
                (0x0068).to_bytes(2, byteorder='big') +  # LoadImageData rec_id
                payload
            )

            # Send to image data port
            try:
                self.client_socket.sendto(packet, (self.SERVER_IP, self.IMAGE_DATA_PORT))
                packets_sent += 1
                seq_no += 1

                # Progress indicator every 100 packets
                if packets_sent % 100 == 0:
                    print(f"  Sent {packets_sent} packets ({packets_sent * 100 // len(encoded_rows)}%)")

            except socket.error as e:
                print(f"Socket error sending packet {seq_no}: {e}")
                raise RuntimeError(f"Failed to send RLE packet {seq_no}") from e

        print(f"Sent {packets_sent} RLE packets")

        # Check for out-of-sequence packets
        reply = self.send(records.RequestSeqNoError().bytes())
        
        if reply is not None:
            # Parse reply: [tot_size: 2] [rec_id: 2] [is_error: 1] [last_seq_no: 2]
            is_error = reply[0][4]
            
            if is_error:
                last_seq = int.from_bytes(reply[0][5:7], byteorder='big')
                print(f"Out-of-sequence error detected at packet {last_seq + 1}")
                raise RuntimeError(f"Out-of-sequence packet detected after seq_no {last_seq}")
            else:
                print("All packets received successfully")
        else:
            print("Warning: Could not verify packet transmission")

        # Take sequencer out of reset
        self.send(records.SetSequencerState(2, False).bytes())

        # Display timing information
        time_elapsed = time.time() - time_elapsed
        print(f"Time elapsed to send RLE image: {time_elapsed:.2f} seconds")
        print(f"Effective throughput: {compressed_size / time_elapsed / 1e6:.2f} MB/s")

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

        for packet in packets:
            reply = self.send(packet)

            
        self.send(records.SetSequencerState(2, False).bytes())

        self.check_sequencer_error() # Check for errors

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
    

    



        
    

    

