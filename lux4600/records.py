
# class containing common code for all records
class Record:
    def __init__(self, tot_size: int, rec_id: int, payload: bytes=b''):
            """
            Initializes a Record object with the given total size, record ID, and payload.

            Parameters:
            - tot_size (int): The total size of the record.
            - rec_id (int): The ID of the record.
            - payload (bytes, optional): The payload data of the record. Default is an empty byte string.
            """
            self.ReplyAck = {
                    b'\x00\x06\x01\xF5\x00\x00': "OK",
                    b'\x00\x06\x01\xF5\x27\x10': "Invalid inum size",
                    b'\x00\x06\x01\xF5\x27\x11': "Invalid image type",
                    b'\x00\x06\x01\xF5\x27\x12': "Sequence file package out of order",
                    b'\x00\x06\x01\xF5\x27\x13': "Error when parsing loaded sequence file. Log can be fetched with5.3.4 Sequencer File Error Log",
                    b'\x00\x06\x01\xF5\x27\x14': "Too many sequence file packages (must be <= 20)",
                    b'\x00\x06\x01\xF5\x27\x15': "Unknown record id (rec_id) received",
                    b'\x00\x06\x01\xF5\x27\x16': "Invalid sequence command",
                    b'\x00\x06\x01\xF5\x27\x17': "Mask file package out of order",
                    b'\x00\x06\x01\xF5\x27\x18': "Too many mask file packages (must be <= 30)",
                    b'\x00\x06\x01\xF5\x27\x19': "Accessing invalid FPGA register. [Internal]",
                    b'\x00\x06\x01\xF5\x27\x1A': "Translated sequence file is too large",
                    b'\x00\x06\x01\xF5\x27\x1B': "No contact with LED driver or accessing invalid LED driver register. [Internal]",
                    b'\x00\x06\x01\xF5\x27\x1C': "Trying to set an invalid sequence register. Ref 5.3.8 Sequencer Register.",
                    b'\x00\x06\x01\xF5\x27\x1D': "Focus motor number of steps out of range",
                    b'\x00\x06\x01\xF5\x27\x1E': "Focus motor is busy or in a mode where command cannot be performed.",
                    b'\x00\x06\x01\xF5\x27\x1F': "Focus motor measured distance out of range",
                    b'\x00\x06\x01\xF5\x27\x20': "Focus motor CCD thickness out of range",
                    b'\x00\x06\x01\xF5\x27\x21': "Focus motor absolute position out of range.",
                    b'\x00\x06\x01\xF5\x27\x22': "Focus motor has not been set to mid position",
                    b'\x00\x06\x01\xF5\x27\x23': "Focus motor measured distance never entered",
                    b'\x00\x06\x01\xF5\x27\x24': "Mask file with invalifd format (not bmp, not 8-bit, etc)",
                    b'\x00\x06\x01\xF5\x27\x25': "LED driver amplitude value out of range.",
                    b'\x00\x06\x01\xF5\x27\x26': "Temperature regulation setvalue out of range.",
                    b'\x00\x06\x01\xF5\x27\x27': "Focus motor step size conversion unit out of range",
                    b'\x00\x06\x01\xF5\x27\x28': "Internal sync pulse period outside valid range",
                    b'\x00\x06\x01\xF5\x27\x29': "AF trim value is outside valid range",
                    b'\x00\x06\x01\xF5\x27\x2A': "AF work range is outside valid range.",
                    b'\x00\x06\x01\xF5\x27\x2B': "AF time delay value is outside valid range.",
                    b'\x00\x06\x01\xF5\x27\x2C': "AF calibration set-position is outside valid range.",
                    b'\x00\x06\x01\xF5\x27\x2D': "AF pull-in range acceleration limit is outside valid range.",
                    b'\x00\x06\x01\xF5\x27\x2E': "AF speed high threshold is outside valid range",
                    b'\x00\x06\x01\xF5\x27\x2F': "Laser intensity level is outside valid range.",
                    b'\x00\x06\x01\xF5\x27\x30': "Trig delay outside valid range",
                    b'\x00\x06\x01\xF5\x27\x31': "Active Area Qualifier Keepout parameters are outside valid range.",
                    b'\x00\x06\x01\xF5\x27\x32': "Active Area Qualifier Keepout parameters adds up to a larger number than the active number of pulses",
                    b'\x00\x06\x01\xF5\x27\x33': "Trig divide factor outside valid range.",
                    b'\x00\x06\x01\xF5\x27\x34': "<Currently unused>",
                    b'\x00\x06\x01\xF5\x27\x35': "OCP limit is out of range",
                    b'\x00\x06\x01\xF5\x27\x36': "Strip number out of range.",
                    b'\x00\x06\x01\xF5\x27\x37': "Internal image number out of range or perrmanent storage error",
                    b'\x00\x06\x01\xF5\x27\x38': "Not possible to load sequence file. No file has has been loaded previously.",
                    b'\x00\x06\x01\xF5\x27\x39': "Invalid fan number",
                    b'\x00\x06\x01\xF5\x27\x3A': "Absolute Z position for AF is outside valid range",
                    b'\x00\x06\x01\xF5\x27\x3B': "Invalid morph record",
                    b'\x00\x06\x01\xF5\x27\x3C': "Led driver firmware package out of order",
                    b'\x00\x06\x01\xF5\x27\x3D': "Led driver firmware crc error",
                    b'\x00\x06\x01\xF5\x27\x3E': "Led driver firmware verification failed",
                    b'\x00\x06\x01\xF5\x27\x3F': "Led driver firmware upgrade ok",
                    b'\x00\x06\x01\xF5\x27\x40': "Invalid address",
                    b'\x00\x06\x01\xF5\x27\x41': "Invalid data",
                    b'\x00\x06\x01\xF5\x27\x42': "Command not supported by old led driver fw",
                    b'\x00\x06\x01\xF5\x27\x43': "<Reserved>",
                    b'\x00\x06\x01\xF5\x27\x44': "Overlay text parameter out of range",
                    b'\x00\x06\x01\xF5\x27\x45': "SSD Error: Ublaze can not start",
                    b'\x00\x06\x01\xF5\x27\x46': "SSD Error: Physical state error",
                    b'\x00\x06\x01\xF5\x27\x47': "SSD Error: Align count off",
                    b'\x00\x06\x01\xF5\x27\x48': "SSD Error: Bad link",
                    b'\x00\x06\x01\xF5\x27\x49': "SSD Error: Bad transport layer",
                    b'\x00\x06\x01\xF5\x27\x4A': "SSD Error: Loop counter stopped"
                }
            self.payload = payload
            self.tot_size = tot_size
            self.rec_id = rec_id
            pass

    def bytes(self) -> bytes:
        '''Returns the full record as bytes.'''
        return self.tot_size.to_bytes(2, byteorder='big') + self.rec_id.to_bytes(2, byteorder='big') + self.payload

    def reply(self, response: bytes) -> tuple[str, int]:
        try:
            return self.ReplyAck[response], -1
        except KeyError:
            return "Unknown ReplyAck or invalid Reply: " + response.hex(), -1 

#
# VISITECH RECORD LIBRARY
# last updated 05/01/2024
#
# status: incomplete
#
class SetInumSize(Record):
    def __init__(self, rows: int):
        super().__init__(6, 102, rows.to_bytes(2, byteorder='big'))

class RequestInumSize(Record):
    def __init__(self):
        super().__init__(4, 302)

    def reply(self, response: bytes) -> tuple[str, int]:
        try:
            return self.ReplyAck[response], -1
        except KeyError:
            inum_size = int.from_bytes(response[4:], byteorder='big')
            return "Inum size: " + str(inum_size), inum_size

class SetImageType(Record):
    def __init__(self, image_type: int):
        super().__init__(6, 103, image_type.to_bytes(2, byteorder='big'))

class RequestImageType(Record):
    def __init__(self):
        super().__init__(4, 303)

    def reply(self, response: bytes) -> str:
        try:
            return self.ReplyAck[response]
        except KeyError:
            image_type = int.from_bytes(response[4:], byteorder='big')
            return "Image type: " + str(image_type), image_type

class LoadImageData(Record):
    def __init__(self, seq_no:int, inum:int, offset:int, data:bytes):

        if len(data) > 8956 or len(data) < 4:
            raise ValueError("Data length must be between 4 and 8956 bytes.")

        payload = seq_no.to_bytes(2, byteorder='big') + inum.to_bytes(2, byteorder='big') + offset.to_bytes(2, byteorder='big') + data
        super().__init__(len(payload) + 4, 104, payload)

class RequestSeqNoError(Record):
    def __init__(self):
        super().__init__(4, 311)
    
    def reply(self, response: bytes) -> str:
        if len(response) != 7 or response[:4] != b'\x00\x07\x01\xFF':
            return "Invalid Reply: " + response.hex()
        elif response[4] == 0:
            return "No sequence number error since last request"
        elif response[4] == 1:
            return "Sequence number error since last request. Sequence number: " + str(int.from_bytes(response[5:], byteorder='big'))
        else:
            return "Unknown SeqNoError Reply: " + response.hex()

class ResetSeqNo(Record):
    def __init__(self):
        super().__init__(4, 112)

class LoadFlatnessCorrectionMask(Record):
    def __init__(self, pkg_no: int, tot_pkg: int, data_size: int, data: bytes):
        if len(data) > 8956 or len(data) < 1:
            raise ValueError("Data length must be between 1 and 8956 bytes.")
        
        payload = pkg_no.to_bytes(2, byteorder='big') + tot_pkg.to_bytes(2, byteorder='big') + data_size.to_bytes(2, byteorder='big') + data
        super().__init__(len(payload) + 4, 116, payload)

class SetFlatnessMaskOn(Record):
    def __init__(self, enable: bool):
        super().__init__(5, 148, int(enable).to_bytes(1, byteorder='big'))

class RequestFlatnessMaskOn(Record):
    def __init__(self):
        super().__init__(4, 348)
    
    def reply(self, response: bytes) -> str:
        if response[:4] != b'\x00\x04\x01\x5C':
            return "Invalid Reply: " + response.hex(), -1
        elif response[4] == 0:
            return "Flatness mask is off", False
        elif response[4] == 1:
            return "Flatness mask is on", True
        else:
            return "Unknown FlatnessMaskOn Reply: " + response.hex(), -1

class SetLoadInternalImage(Record):
    def __init__(self, img_no: int):
        super().__init__(5, 169, img_no.to_bytes(1, byteorder='big'))

class RequestLoadInternalImage(Record):
    def __init__(self):
        super().__init__(4, 369)
    
    def reply(self, response: bytes) -> str:
        try:
            return self.ReplyAck[response]
        except KeyError:
            if response[:4] != b'\x00\x05\x02\x39':
                return "Invalid Reply: " + response.hex(), -1
            else:
                img_no = response[-1]
                return "Internal image number: " + str(img_no), img_no
            
class SetSequencerState(Record):
    """
    Represents a record for setting the sequencer state.
    
    Args:
        seq_cmd (int): 1 = Run, 2 = Reset
        enable (bool): True = enable, False = disable
        Example:
            Disable/stop the sequencer: SetSequencerState(1, False)
            Enable/start the sequencer: SetSequencerState(1, True)
            Set the sequencer in reset: SetSequencerState(2, True)
            Take the sequencer out of reset: SetSequencerState(2, False)
    """

    def __init__(self, seq_cmd: int, enable: bool):
        super().__init__(6, 106, seq_cmd.to_bytes(1, byteorder='big') + int(enable).to_bytes(1, byteorder='big'))

class RequestSequencerState(Record):
    def __init__(self, seq_cmd: int):
        super().__init__(5, 306, seq_cmd.to_bytes(1, byteorder='big'))
    
    def reply(self, response: bytes) -> str:
        try:
            return self.ReplyAck[response]
        except KeyError:
            if response[:4] != b'\x00\x07\x01\xFA':
                return "Invalid Reply: " + response.hex(), -1
            else:
                seq_cmd = response[4]; enable = response[5]; valid_cmd = response[6] 
                return "Sequencer command: " + str(seq_cmd) + ", enable: " + str(enable) + ", valid command: " + str(valid_cmd), (seq_cmd, enable, valid_cmd)

class SetSoftwareSync(Record):
    def __init__(self, level: int):
        ''' level: 0 = low, 1 = high '''
        super().__init__(5, 120, level.to_bytes(1, byteorder='big'))
        
class SetLedDriverAmplitude(Record):
    def __init__(self, led_no: int, amplitude: int):
        if amplitude < 0 or amplitude > 4095:
            raise ValueError("Amplitude must be between 0 and 4095.")
        super().__init__(8, 133, led_no.to_bytes(2, byteorder='big') + amplitude.to_bytes(2, byteorder='big'))

class RequestLedAmplitude(Record):
    def __init__(self, led_no: int):
        super().__init__(6, 333, led_no.to_bytes(2, byteorder='big'))
    
    def reply(self, response: bytes) -> str:
        try:
            return self.ReplyAck[response]
        except KeyError:
            led_no = int.from_bytes(response[4:6], byteorder='big')
            amplitude = int.from_bytes(response[6:8], byteorder='big')
            read_ok = str(response[8])
            return "LED number: " + str(led_no) + ", amplitude: " + str(amplitude) + ", read ok: " + read_ok, (led_no, amplitude, read_ok)

class RequestLedStatus(Record):
    def __init__(self, led_no: int):
        super().__init__(6, 334, led_no.to_bytes(2, byteorder='big'))
    
    def reply(self, response: bytes) -> str:
        try:
            return self.ReplyAck[response]
        except KeyError:
            led_no = int.from_bytes(response[4:6], byteorder='big')
            led_status_word = ''.join(format(b, '08b') for b in response[6:8])
            led_status_word = led_status_word[:8]
            read_ok = str(response[8])
        
            #TODO: Add message for each bit in the status word

            return "LED number: " + str(led_no) + ", status word: " + str(led_status_word) + ", read ok: " + read_ok, (led_no, led_status_word, read_ok)
        
class RequestLedTemperature(Record):
    def __init__(self, led_no: int):
        super().__init__(6, 335, led_no.to_bytes(2, byteorder='big'))
    
    def reply(self, response: bytes) -> str:
        try:
            return self.ReplyAck[response]
        except KeyError:
            led_no = int.from_bytes(response[4:6], byteorder='big')
            led_temp = int.from_bytes(response[6:8], byteorder='big')/10 # degrees celsius
            board_temp = int.from_bytes(response[8:10], byteorder='big')/2 # degrees celsius
            read_ok = str(response[8])
            message = "LED number: " + str(led_no) + ", led_temp: " + str(led_temp) + ", board_temp: " + str(board_temp) + ", read ok: " + read_ok
            data = {"led_no": led_no, "led_temp": led_temp, "board_temp": board_temp, "read_ok": read_ok}
            return message, data
        
class RequestSeqFileErrorLog(Record):
    def __init__(self):
        super().__init__(4, 307)

    def reply(self, response: bytes) -> str:
        data_size = response[:2]
        error = response[2:].decode()
        return data_size, error

        
