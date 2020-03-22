import socket, sys, pickle

def alert(msg):
	print >>sys.stderr, msg
	sys.exit(1)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#s.setblocking(False)
s.sendto(
	pickle.dumps((6, "TESTING!")),
	("191.252.103.220", 1360)
)

while True:
	dat, addr = s.recvfrom(4096)
	if dat:
		print(pickle.loads(dat))
		break
s.close()