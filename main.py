import bluetooth
import time
import sys
import pyaudio
import math
from collections import deque

#Bluetooth address
mod1_addr = "98:D3:31:90:51:AB"
port = 1


def main():

	sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
	sock.connect((mod1_addr, port))

	qsize = 8
	qX = deque(maxlen=qsize)
	qY = deque(maxlen=qsize)
	qZ = deque(maxlen=qsize)

	X = 0
	Y = 0
	Z = 0

	#Wait until the data comes through correctly
	calibrate(sock)

	while(True):
		try:
			message = sock.recv(64)
			#Check if the data came through correctly
			data = checkData(message)
			if data:
				#The data contains 3 elements
				data = message.split()
				print data

				X = float(data[0])
				Y = float(data[1])
				Z = float(data[2])

				#Put the data in a Queue so we always get the 4 most recent elements
				qX.append(X)
				qY.append(Y)
				qZ.append(Z)

			#If the Queue is full, we can get the mean
			if len(list(qX)) == qsize & len(list(qY)) == qsize & len(list(qZ)) == qsize:
				print "queue is full"
				#Copy queue
				tqX = qX
				tqY = qY
				tqZ = qZ

				meanX = calcMean(tqX, qsize)
				meanY = calcMean(tqY, qsize)
				meanZ = calcMean(tqZ, qsize)

				print "Averages are: ", meanX, meanY, meanZ

				threshold = 4
				#if new data deviates to much from the mean, movement has been detected!
				#DISABLED due to BUG
				# if X > meanX + threshold or X < meanX - threshold:
				# 	alarm()

				if Y > meanY + threshold or Y < meanY - threshold:
					alarm()

				if Z > meanZ + threshold or Z < meanZ - threshold:
					alarm()
		except:
			import traceback
			print traceback.print_exc()
			sys.exit(1)
			continue

		time.sleep(1)

def calcMean(q, qsize):
	meanQ = mean(list(q))
	q.popleft()
	return meanQ


def mean(l):
	return float(sum(l))/len(l) if len(l) > 0 else float('nan')


def checkData(data):
	if len(data.split()) is 3:
		return True
	return False

def calibrate(sock):
	print "Calibrating"
	while(True):
		message = sock.recv(64)
		data =  message

		if checkData(data):
			print "Calibrated"

			return True
		time.sleep(1)


def alarm():
	PyAudio = pyaudio.PyAudio

	#See http://en.wikipedia.org/wiki/Bit_rate#Audio
	BITRATE = 16000 #number of frames per second/frameset.

	#See http://www.phy.mtu.edu/~suits/notefreqs.html
	FREQUENCY = 261.63 #Hz, waves per second, 261.63=C4-note.
	LENGTH = 1.2232 #seconds to play sound

	NUMBEROFFRAMES = int(BITRATE * LENGTH)
	RESTFRAMES = NUMBEROFFRAMES % BITRATE
	WAVEDATA = ''

	for x in xrange(NUMBEROFFRAMES):
	 WAVEDATA = WAVEDATA+chr(int(math.sin(x/((BITRATE/FREQUENCY)/math.pi))*127+128))

	#fill remainder of frameset with silence
	for x in xrange(RESTFRAMES):
	 WAVEDATA = WAVEDATA+chr(128)

	p = PyAudio()
	stream = p.open(format = p.get_format_from_width(1),
					channels = 1,
					rate = BITRATE,
					output = True)
	stream.write(WAVEDATA)
	stream.stop_stream()
	stream.close()
	p.terminate()

if __name__ == "__main__":
	main()