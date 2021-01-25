import socket
import time
import binascii


#from threading import Timer

gremlinCount = 1


def CRC(payload,pad ='0000000000000000'):

	#values to be used in CRC calculation
	#the divider
	#r = 16bits
	gen = '10001000000100001'

	#convert payload into a sting of its binary representation
	holder = bin(int(binascii.hexlify(payload),16))
	#drops '0b'
	payload = holder[2:]
 

	#adds paddding to the end of the payload
	payload = payload + pad
	#find lengths of strings
	payload = list(payload)
	gen = list(gen)
	
	#loops through payload, not including pad
	for i in range(len(payload) - len(pad)):
		if payload[i] == '1': 
			for j in range(len(gen)):
				#peforms modulo 2 multiplication on each index of the divisor
				payload[i+j] = str((int(payload[i+j]) + int(gen[j]))%2)

	#return the error checking part 
	return ''.join(payload[-len(pad):])

def parseData(data):

	global gremlinCount

	##GREMLIN corrupts package
	if gremlinCount == 6:
			data = data[:9] + '11111111' + data[19:]
			
	
	startFlag = data[0]
	if startFlag != '~':
		print 'Data received does not follow format'

	frameNumberSR = data[1]
	seq_Number = data[2:5]
	# print ' SEQUENCE NUMBER:'
	# print seq_Number
	print 'Frame:'
	print frameNumberSR

	payload_Length = data[6:9]
	payload = data[10:18]



	print data

	ACK = data[19]
	NAK = data[20]
	Checksum = data[-17:-1]	#checksum should be the last 16 bits of the data

	gremlinCount += 1
	

	errorMessage = CRC(payload, Checksum)
	if errorMessage != '0000000000000000':
		print 'Payload contains Errors!'
		return -1

	return frameNumberSR
	#dataList = [startFlag, seq_Number, pay]


def main():
#timer = Timer(30, "Server Timeout")
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	IP = socket.gethostbyname(socket.gethostname())
	port = 1274
	address = (IP,port)

	server.bind(address)
	server.listen(2)  #Argument specifies how many clients can connect at a time
	print "[*] Started listening on ", IP, ': ', port
	client,addr = server.accept()

	#IP address stored in the first memory location, the port is stored in the second
	print "[*] Got a connection from: ", addr[0], ": ", addr[1]
	client.settimeout(2)

	with open('ASCIItextReceived.txt', 'w+') as f:

		windowSize = 4
		totalFrames= 1024/8		#Num of chars in text file / size ofpayload
		framesSent = 0
		correctFramesSent = 0 #number of correct frames sent
		i = 0
		##start = 0
	


		while True:			

				window = ['ABSENT', 'ABSENT','ABSENT', 'ABSENT']
				expired = 0
				i = 0

				start = time.time()


				##TAKE IN Frame
				for i in range (0,windowSize):	
			
					try:
						## TAKE IN FRAME ##
						data = client.recv(1024)

						
					except socket.timeout:
						##IF SOCKET TIMES OUT, FRAME IS MISSING
						# SET FLAG 
						#print 'socket timeout'
						expired = 1
						print 'Socket timed out'
						continue

						
				
					else:

						##PLACE IT IN CORRECT POSITION IN WINDOW FRAME
						index = data[1] #frame number
						window[int(index)] = data[10:18] #STORE FRAME INFO
	

						#Check for errors in data
						frameNumberSR = parseData(data)

						##If there is a error in the data of the frame
						if frameNumberSR == -1:

							#NOTE ITS POSITION
							#SET VALUE IN WINDOW '-1'
							ErrorFrameIndex = data[1]
							window[int(ErrorFrameIndex)] = '-1'
			
						
					


				##CHECK ALL ELEMENTS TO SEE IF THERE WAS AN ERROR
				##UNRECEIVED PACKETS WILL HAVE STING 'ABSENT'
				if expired == 1:
					##timer expires if packet is missing
					print 'ERROR!: A packet has been dropped!'

					#find which packet is missing
					for m in range(0,windowSize):

						if window[m] == 'ABSENT':
							droppedPacketIdx = m

					##Send NAK

					NAKList = [str(droppedPacketIdx), '0']
					NAK = ''.join(NAKList)
					print 'Packet Dropped, Send NAK:'
					print NAK
					client.send(NAK)


					##waits for replacemet Frame
					data = client.recv(1024)
					frameNumberSR = parseData
					print 'NEW frame received:'
					print data

					##UPDATE WINDOW with accurate payload data
					window[droppedPacketIdx] = data[10:18]

			

				#CHECK IF CRC RETURNED -1 
				for k in range (0,windowSize):

				## IF YES
				##NOTE: this can only deal with one error per frame
				#could be expanded using array
					if window[k] == '-1':
						if window[k] == '-1':
							print "Error in Payload! Packet corrupt!"

						##SEND NAK
						NAKList = [ErrorFrameIndex, '0']
						NAK = ''.join(NAKList)
						client.send(NAK)

						##WAIT FOR NEW FRAME 
						data = client.recv(1024)
						#frameNumberSR = parseData
						print 'NEW frame received:'
						print data
						frameNumberSR = data[2:6]

						##UPDATE WINDOW with accurate payload data
						window[k] = data[10:18]


				##ERROR CHECKS COMPLETE

				##send ack
				index = '0'
				ackList = [index, '1']
				ACK = ''.join(ackList)
				print '[*] Sending ACK:'
				client.send(ACK)



				for d in range(0, windowSize):
					if window[d] != 'ABSENT':
						f.write(window[d])

				print ''

				if data == 'COMPLETED PROCESS - TERMINATE!':
					break


		server.close()	

	
if __name__ == "__main__":
	main()


		
