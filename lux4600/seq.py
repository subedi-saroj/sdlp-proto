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

		self.file = self.open()

		self.packets = self.sequence_to_packets(self.file)

	def open(self) -> BinaryIO:
		'''Open a sequence file and return the file object.'''

		return open(self.file_path, 'rb')
	
	def read(self) -> bytes:
		'''Read a chunk from the sequence file and return it as bytes.'''

		return self.file.read(self.chunk_size)

	def sequence_to_packets(self, chunk_size:int=1440) -> Iterator[bytes]:
		'''Splits a sequence into packets for transmission.'''

		SequencerValueError.check_chunk_size(chunk_size) # check chunk size

		while True:
			chunk = self.read(chunk_size)
			if not chunk:
				break
			yield chunk


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
