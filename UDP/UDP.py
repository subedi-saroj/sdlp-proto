import socket

class UDPProjector:
    def __init__(self):
        self.SERVER_IP = '192.168.0.10'
        self.SERVER_PORT = 52985
        self.IMAGE_DATA_PORT = 52986
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # initialise
        self.init_commands()


    def send_command(self, command):
        try:
            self.socket.sendto(command, (self.server_ip, self.server_port))
            response, _ = self.socket.recvfrom(1024)
            return response
        except socket.error as e:
            print(f"Error sending command: {e}")
            return None

    def close(self):
        self.socket.close()

# class that 
class Record:
    def __init__(self) -> None:
        
        self.set()

        self.ReplyAck = {
            # This record is returned from the Luxbeam as an acknowledgement that a «Set»-record has been received and processed. 
            "set": None,
            "request": None,
            "reply": {
                b'\x00\x00': "OK",
                b'\x27\x10': "Invalid inum size",
                b'\x27\x11': "Invalid image type",
                b'\x27\x12': "Sequence file package out of order",
                b'\x27\x13': "Error when parsing loaded sequence file. Log can be fetched with5.3.4 Sequencer File Error Log",
                b'\x27\x14': "Too many sequence file packages (must be <= 20)",
                b'\x27\x15': "Unknown record id (rec_id) received",
                b'\x27\x16': "Invalid sequence command",
                b'\x27\x17': "Mask file package out of order",
                b'\x27\x18': "Too many mask file packages (must be <= 30)",
                b'\x27\x19': "Accessing invalid FPGA register. [Internal]",
                b'\x27\x1A': "Translated sequence file is too large",
                b'\x27\x1B': "No contact with LED driver or accessing invalid LED driver register. [Internal]",
                b'\x27\x1C': "Trying to set an invalid sequence register. Ref 5.3.8 Sequencer Register.",
                b'\x27\x1D': "Focus motor number of steps out of range",
                b'\x27\x1E': "Focus motor is busy or in a mode where command cannot be performed.",
                b'\x27\x1F': "Focus motor measured distance out of range",
                b'\x27\x20': "Focus motor CCD thickness out of range",
                b'\x27\x21': "Focus motor absolute position out of range.",
                b'\x27\x22': "Focus motor has not been set to mid position",
                b'\x27\x23': "Focus motor measured distance never entered",
                b'\x27\x24': "Mask file with invalifd format (not bmp, not 8-bit, etc)",
                b'\x27\x25': "LED driver amplitude value out of range.",
                b'\x27\x26': "Temperature regulation setvalue out of range.",
                b'\x27\x27': "Focus motor step size conversion unit out of range",
                b'\x27\x28': "Internal sync pulse period outside valid range",
                b'\x27\x29': "AF trim value is outside valid range",
                b'\x27\x2A': "AF work range is outside valid range.",
                b'\x27\x2B': "AF time delay value is outside valid range.",
                b'\x27\x2C': "AF calibration set-position is outside valid range.",
                b'\x27\x2D': "AF pull-in range acceleration limit is outside valid range.",
                b'\x27\x2E': "AF speed high threshold is outside valid range",
                b'\x27\x2F': "Laser intensity level is outside valid range.",
                b'\x27\x30': "Trig delay outside valid range",
                b'\x27\x31': "Active Area Qualifier Keepout parameters are outside valid range.",
                b'\x27\x32': "Active Area Qualifier Keepout parameters adds up to a larger number than the active number of pulses",
                b'\x27\x33': "Trig divide factor outside valid range.",
                b'\x27\x34': "<Currently unused>",
                b'\x27\x35': "OCP limit is out of range",
                b'\x27\x36': "Strip number out of range.",
                b'\x27\x37': "Internal image number out of range or perrmanent storage error",
                b'\x27\x38': "Not possible to load sequence file. No file has has been loaded previously.",
                b'\x27\x39': "Invalid fan number",
                b'\x27\x3A': "Absolute Z position for AF is outside valid range",
                b'\x27\x3B': "Invalid morph record",
                b'\x27\x3C': "Led driver firmware package out of order",
                b'\x27\x3D': "Led driver firmware crc error",
                b'\x27\x3E': "Led driver firmware verification failed",
                b'\x27\x3F': "Led driver firmware upgrade ok",
                b'\x27\x40': "Invalid address",
                b'\x27\x41': "Invalid data",
                b'\x27\x42': "Command not supported by old led driver fw",
                b'\x27\x43': "<Reserved>",
                b'\x27\x44': "Overlay text parameter out of range",
                b'\x27\x45': "SSD Error: Ublaze can not start",
                b'\x27\x46': "SSD Error: Physical state error",
                b'\x27\x47': "SSD Error: Align count off",
                b'\x27\x48': "SSD Error: Bad link",
                b'\x27\x49': "SSD Error: Bad transport layer",
                b'\x27\x4A': "SSD Error: Loop counter stopped"
            }
        }
        
        # 5.2.1 Inum Size Records
        self.InumSize = {
            # This record is used to set the size of the image number (inum) in the Luxbeam.             "set":,
            "set": None,
            "request": None,
            "reply": self.ReplyAck["reply"]
        }
        pass

    def _to_bytes(tot_size, rec_id, payload, payload_type="byte"):
        command =  tot_size.to_bytes(2, byteorder='big') + rec_id.to_bytes(2, byteorder='big')
        if payload_type == "byte":
            return command + payload
        elif payload_type == "string":
            return command + payload.encode()
        elif payload_type == "int":
            return command + payload.to_bytes(2, byteorder='big')
        else:
            print("Invalid payload type")
            return None