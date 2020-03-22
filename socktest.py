import socket, sys, pickle

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setblocking(False)
s.sendto(
	pickle.dumps((6, "TESTING!")),
	("localhost", 1360)
)

while True:
	try:
		dat, addr = s.recvfrom(1024)
		if dat:
			print(pickle.loads(dat))
			break
	except: pass
s.close()