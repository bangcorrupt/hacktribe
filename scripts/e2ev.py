# INCOMPLETE

import ntpath
import math
import binascii
from bitstring import BitArray
import os
import argparse


def main():		
	parser = argparse.ArgumentParser()	
	parser.add_argument("inFile", metavar="INPUT_FILE", type=str, help="path/to/load/file.e2ev")
	parser.add_argument("-s", "--split", dest='split', help="Split event recording by pattern change", action='store_true')	
	parser.add_argument("-c", "--channels", dest='channels', nargs='+', help="Mute all channels except list of channel numbers to include in stem (0 - 15)")
	parser.add_argument("-n", "--name", dest='name', help="Name for stem.")
	parser.add_argument("-e", "--extract", dest='extract', help="Extract pattern files from event recording", action='store_true')
	parser.add_argument("-r", "--replace", dest='replace', help="Pattern number to replace.  Requires -p file.e2pat.  Overwrites original ev file.")
	parser.add_argument("-p", "--pattern", dest='pattern', help="path/to/pattern/file.e2pat")	
	parser.add_argument("-m", "--mute", dest='mute', help="Channel number to mute (0 - 15)")
	parser.add_argument("-i", "--info", dest='info', help="Print patterns found")
	args = parser.parse_args()

	ev = EventRec(args.inFile)
	
	if args.split:
		ev.split_by_pattern()
	
	if args.channels and args.name:
		ev.get_stem(args.channels, args.name)
		
	if args.extract:
		ev.extract_patterns()
	
	if args.replace and args.pattern:
		ev.replace_pattern(int(args.replace), args.pattern)
		ev.write_evData()
		
	if args.mute:
		ev.mute_channel(int(args.mute))
		ev.write_evData()

	if args.info:
		ev.get_info()

class EventRec:
	def __init__(self, path):
		print('This tool is unfinished.  Back up your files.')
		self.path = path
		self.name = self.get_filename(self.path)
		self.get_evData()

	
	def get_info(self):
		print(str(self.patCount) + ' patterns found.')
		for i in range(len(self.evPat)):		
			p = self.evPat[i].patData[0x10:0x1F]
			while p and p[-1] is 0:
				p.pop()	
			print(str(i) + ' ' + p.decode("utf-8") )


	def get_evData(self):	
		self.evData = []
		with open(self.path, 'rb') as f:
			self.evData =  bytearray(f.read())	
		ptCount = self.evData.count(bytearray('PTST', 'ascii'))
		self.patCount = ptCount
		ptPos = []
		x = 0
		for i in range(0, ptCount):
			x = self.evData.find(bytearray('PTST', 'ascii'), x+1)
			ptPos.append(x)
		self.evPat = []
		for i in range(0, ptCount):
			startByte = ptPos[i]
			try:
				endByte = ptPos[i+1]
			except:
				endByte = len(self.evData)-8
			self.evPat.append(EvPat(self, i, startByte, endByte))	# e2eventrec split by pattern change
			
		
	def write_evData(self, evPat=None, name=None):
		if not name:
			name = self.get_filename(self.path)[:-5]	
		if not evPat:
			evPat = self.evPat
		z = []
		evPatMod = []
		for i in range(len(evPat)):
			z.append(evPat[i].patData)
			for j in range(len(evPat[i].perfData)):
				z.append(evPat[i].perfData[j])
		for x in z:
			for y in x:
				evPatMod.append(y)	
		evPatMod = bytearray(evPatMod)	
		evDataMod = self.evData[:280] + evPatMod + self.evData[-8:]
		
		# insert file size
		leng = len(evDataMod)-288
		try:
			leng  = bytearray.fromhex('0' + hex(leng)[2:])[::-1]
		except:
			leng  = bytearray.fromhex(hex(leng)[2:])[::-1]
		pos = 260
		for byte in leng:			
			evDataMod[pos] = byte
			pos+=1
		evDataMod[pos] = 0x00

		with open(name + '.e2ev', 'wb') as f:
			f.write(bytearray(evDataMod))
			

	def mute_channel(self, channel):
		for j in range(0, len(self.evPat)):
			#	Add vol CC = 0 at start
			b  = b'\x00\x00\x00\x00\x01\x00' + bytes([channel]) + b'\x00\x26\x00\xFF\xFF\x00\x00\x00\x00'
			self.evPat[j].perfData.insert(self.evPat[j].goMsgPos+1,b)
			p = []	
			for msg in self.evPat[j].perfData:
				line = bytearray(msg)	# copy to mutable
				
				#	set volume changes to 0	
				if line[4] == 1 and line[6] == channel and line[8] == 38:
					line[12] = 0x00
					line[13] = 0x00 
				
				#	set all note velocities for channel to 0
				if len(line) == 16 and line[4] == 0 and line[11] == 1:		
					noteOn = int(str(hex(line[8])[2:3]), 16)
					chan = int(str(hex(line[8])[3:4]), 16)
					if noteOn == 9 and chan == channel:
						line[10] = 0x00
				p.append(line)			
			
			for i in range(0,len(p)):
				self.evPat[j].perfData[i] = p[i]	

	
	def extract_patterns(self):
		i = 0
		for pat in self.evPat:
			pattern = self.evData[:256] + pat.patData
			with open(self.name[:-5] + '_pat_' + str(i) + '.e2pat', 'wb') as f:
				f.write(pattern)
			i+=1


	def replace_pattern(self, position, pattern):
		with open(pattern, 'rb') as f:
			new_patData =  bytearray(f.read())		
		self.evPat[position].patData = new_patData[256:]
		
	
	def split_by_pattern(self):
		i = 0
		for evpat in self.evPat:
			ev = [evpat]
			self.write_evData(evPat=ev, name=self.name[:-5] + '_pat_' + str(i))
			i+=1
	
	
	def get_stem(self, channels, name):	# channels is list of channel numbers to include in stem
		mutes = [x for x in range(16) if x not in channels]
		for channel in mutes:
			self.mute_channel(channel)
		self.write_evData(name=self.name[:-5] + '_' + name + '_stem')
		self.get_evData()


	def get_filename(self, path):
		head, tail = ntpath.split(path)
		return tail or ntpath.basename(head)



class EvPat:
	def __init__(self, evRec, number, startByte, endByte):
		self.evRec = evRec
		self.evData = evRec.evData
		self.number = number
		self.patSt = startByte
		self.perfSt = startByte + 16384	
		self.endByte = endByte

		self.get_patData()
		self.get_perfData()


	def get_patData(self):
		self.patData = self.evData[self.patSt:self.patSt+16384]
		
			
	def get_perfData(self):	
		self.goMsgPos = 0
		j = 0	
		self.perfData = []
		for i in range(self.perfSt-8, self.endByte+8, 16):
			line = self.evData[i:i+16]
			self.perfData.append(line)
			if len(line) == 16:
				if line[8] != 0x00 and line[12] == 0x03 and line[11] == 0x00:
					self.goMsgPos = j
			j+=1
		self.perfData[0] = self.perfData[0][-8:]
		self.perfData[-1] = self.perfData[-1][:-8]


   
if __name__ == '__main__':
    main()

