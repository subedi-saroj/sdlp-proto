#
# Base code for handling .seq files. 
# Short scripts removed from classes to improve readability and clarity.# 
#

def split_sequence_into_packets(self, file_path, chunk_size=1440):
        
        with open(file_path, 'rb') as file:
            
            for chunk in self._read_chunk(file, chunk_size):
                    yield chunk

