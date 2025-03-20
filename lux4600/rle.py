

def encode_rle(data:bytes, width:int, height:int):

    for l in range(len(data) // height):

        line = data[l*width:l*width + width]
        
        yield rle_encode_line(line)

def rle_encode_line(line:bytes):
    encoded_packet = b''
    count = 1
    prev = line[0]

    for byte in line:

        if byte == prev:
            count += 1
        else:
            encoded_packet += bytes([prev, count])
            count = 1
            prev = byte

    encoded_packet += bytes([prev, count - 1])

    return encoded_packet
 
