import socket, sys, pickle

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setblocking(False)
s.sendto(
	pickle.dumps((6, "TESTING!")),
	("191.252.103.220", 11360)
)

while True:
	try:
		dat, addr = s.recvfrom(4096)
		if dat:
			print(pickle.loads(dat))
			break
	except: pass
s.close()