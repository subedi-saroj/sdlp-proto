from typing import BinaryIO, Iterator
#
# Base code for handling .seq files. 
# Short scripts removed from classes to improve readability and clarity.# 
#
class Sequencer:
	'''A class for handling .seq files.'''

	def __init__(self, file_path:str, chunk_size:int=1440):
		'''Initialize a Sequencer object with a file path.

		Args:
		    file_path (str): The path to the sequence file to open.
		'''
		self.file_path = file_path
		self.chunk_size = chunk_size

		self.file = self.open().read()

		self.packets = self.to_packets(self.file)

	def open(self) -> BinaryIO:
		'''Open a sequence file and return the file object.'''

		return open(self.file_path, 'rb')
	
	def read(self) -> bytes:
		'''Read a chunk from the sequence file and return it as bytes.'''

		return self.file.read(self.chunk_size)

	def to_packets(self, data:bytes, chunk_size=1440) -> bytes:
		"""Splits a sequence file into packets for transmission."""
		
		SequencerValueError.check_chunk_size(chunk_size)
		
		packets = []
		
		while len(data) > chunk_size:
			packets.append(data[:chunk_size])
			data = data[chunk_size:]
		packets.append(data)
		
		for i in range(len(packets)):
			len_chunk = len(packets[i]).to_bytes(2, byteorder='big')
			i_of_total = (i+1).to_bytes(2, byteorder='big') + len(packets).to_bytes(2, byteorder='big')
			packets[i] = b'\x00\x69' + i_of_total + len_chunk + packets[i]
			packets[i] = (len(packets[i]) + 2).to_bytes(2, byteorder='big') + packets[i]
		
		return packets


class SequencerValueError(ValueError):
	'''Custom exception for Sequencer class.'''

	@staticmethod
	def check_chunk_size(chunk_size:int):
		'''Check if a chunk size is valid.

		Args:
		    chunk_size (int): The chunk size to check.

		Raises:
		    ValueError: If the chunk size is invalid (exceeds 1500 or is not a multiple of 8).'''
		
		if chunk_size > 1500:
			raise ValueError("Chunk size exceeds 1500.")
		
		if chunk_size % 8 != 0:
			raise ValueError("Chunk size must be a multiple of 8.")
