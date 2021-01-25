import socket
#file objects
import random
import string
import time
import binascii

contents = ''
pos_in_text = 0
seq_Number = '0000'
payload_Length = '0000'
gremlinDropPacket = 0


def CRC(payload, pad ='0000000000000000'):

	#pad is an optional parameter that can be used to pass a code from a previous
	#test to see if there are errors
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
	payload= list(payload)
	gen = list(gen)
	
	#loops through payload, not including pad
	for i in range(len(payload) - len(pad)):
		if payload[i] == '1': 
			for j in range(len(gen)):
				#peforms modulo 2 multiplication on each index of the divisor
				payload[i+j] = str((int(payload[i+j])+int(gen[j]))%2)

	#return the error code 

	#print ''.join(payload[-len(pad):])
	return ''.join(payload[-len(pad):])



def createFrame():
	global seq_Number
	global payload_Length
	global gremlinDropPacket 

	gremlinDropPacket += 1
	#header

	start_Flag = '~'
	
	frameNumberSR = '0' #For selective repeat
	seq_Number_holder = str(int(seq_Number)+1)
	#print seq_Number_holder
	length = len(seq_Number_holder)
	obj = (seq_Number[:4-length], seq_Number_holder)
	seq_Number = ''.join(obj)
	seq_Number_holder = '0'


	payload = get_data_input()



	payload_Length_holder = str(len(payload))
	length_pl_string = len(payload_Length_holder)
	obj = (payload_Length[:4-length_pl_string], payload_Length_holder)

	payload_Length = ''.join(obj)

	if payload == '':
		return 'COMPLETED PROCESS - TERMINATE!'

	#trailer
	ACK = '0'
	NAK = '0'
	#gets error code to be sent to client
	check_Sum = CRC(payload)
	end_Flag = '~'

	frame = ''
	sequence = (start_Flag, frameNumberSR, seq_Number, payload_Length, payload, ACK, NAK, check_Sum, end_Flag)
	print frame.join( sequence )
	return frame.join( sequence )
	
def gremlin(string, param):
	if param == 1:
		string = 111111111
		return string


def createTextFile():
	
	with open('ASCIItext.txt', 'w+') as f:
		print "File created!"
		chars = string.letters + string.digits + '         '

		ran_AN_char = random.choice(chars)

		for i in range(1024):
			f.write(ran_AN_char)
			ran_AN_char = random.choice(chars)

		#f.write('the end!') #signals end of the text file
		#contents of text file stored in string


def get_data_input():
	global pos_in_text

	with open('ASCIItext.txt', 'r') as f:
		contents = f.read()

	data_input = contents[pos_in_text:pos_in_text+8]
	pos_in_text +=8
	print data_input
	return data_input


def main():

	global gremlinDropPacket

	frame = 1
	name = socket.gethostname()
	socket.gethostbyname(name)
	client = socket.socket()
	client.connect((socket.gethostbyname(name), 1274))
	print "Connection made!"

	createTextFile()



	#values for Selective Repeat Process
	##WINDOW SIZE CAN'T BE GREATER THAN 9!
	windowSize = 4
	totalFrames = 128 #1024/8		#Num of chars in text file / payload
	framesSent = 0
	window = list()
	i = 0
	j = 0
	k =0                        #flag for to see if negative ack ever received
	



	print 'Beginning Communications'


	while framesSent<totalFrames:

		##build window
		window = ['empty', 'empty', 'empty', 'empty'] 

		while (j < windowSize) and (i < totalFrames):
			##SEND ALL FRAMES WITHIN WINDOW

			##build frame
			frame = createFrame()

			#attach window INDEX to front of frame data
			list1 = list(frame)
			list1[1] = str(i) 	
			frame = ''.join(list1)
			window[i] = frame
			i += 1
			j +=1
			
			print 'Gremlin Number:'
			print gremlinDropPacket

			### Sending Frames #####
			if gremlinDropPacket != 15:	
				##if packet is not to be dropped
				client.send(frame)	
				print 'Frame left client as:'
				print frame
				print "data sent!\n"
				time.sleep(.2)

			if(gremlinDropPacket == 15):
				gremlinDropPacket = 16





		### Wait for Acknowledgement ###
		print 'waiting for acknowledgement for'
		print frame
		acknowledgement = client.recv(10240)
		print 'ack received:'
		print acknowledgement

		#### Checking Acknowledgment #####
		# can only deal with one error per window at the moment
		# this can be improved 
		
		
		if acknowledgement[1] == '0' :
			print 'Negative Acknowledgment received'
			print 'Resending frame'
			print acknowledgement
			k = 1
			corruptFrameIndx = int(acknowledgement[0])

			### resend corrupted frame ###
			corruptFrame = window[corruptFrameIndx]
			print ' Sent CorruptFrame'
			client.send(corruptFrame)

			
		framesSent += 1
		i = 0
		j = 0
		
		print ' '
		time.sleep(.01)

	client.send('COMPLETED PROCESS - TERMINATE!')	

	if k ==0:
			print 'Positive Acknowledgments received for all Frames!'

	print 'All Frames sent successfully!'
	client.close()


if __name__ == "__main__":
    main()


   #NOTES:
   #frames sent as strings
   #integers represented as strings
   #may have been possible to represent them as binary numbers
   #and print their ascii values