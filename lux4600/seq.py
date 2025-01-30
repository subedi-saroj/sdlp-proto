from typing import BinaryIO, Iterator
#
# Base code for handling .seq files. 
# Short scripts removed from classes to improve readability and clarity.# 
#
class Sequence:
	'''A class for handling .seq files.'''

	def __init__(self, file_path:str):
		self.file_path = file_path

	def open(self) -> BinaryIO:
		'''Open a sequence file and return the file object.'''

		return open(self.file_path, 'rb')

def sequence_to_packets(file:BinaryIO, chunk_size=1440) -> Iterator[bytes]:
	'''Splits a sequence into packets for transmission.'''

	check_chunk_size(chunk_size) # check chunk size

	while True:
		chunk = file.read(chunk_size)
		if not chunk:
			break
		yield chunk

def check_chunk_size(chunk_size:int):
	'''Check if chunk size is valid.'''

	if chunk_size > 1500:
		raise ValueError("Chunk size exceeds 1500.")
	if chunk_size % 8 != 0:
		raise ValueError("Chunk size must be a multiple of 8.")
