import socket, threading, pickle

TYPE_PLAYER_CHANGE = 1
TYPE_MESSAGE = 2
TYPE_CONNECT = 3
TYPE_DISCONNECT = 4
TYPE_ERROR = 5,
TYPE_TEST = 6

ERR_NAME_TAKEN = 1

class User:
	def __init__(self, name, addr):
		self.name = name
		self.addr = addr
		self.x = 0
		self.y = 0
		self.z = 0
		self.direction = 0

class Server:
	def __init__(self, host="localhost", port=1360):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setblocking(False)
		self.sock.bind((host, port))
		
		self.clients = {}

		self.__main()

	def broadcast(self, msg, exceptions=[]):
		for n, cli in self.clients.items():
			if n in exceptions:
				continue
			self.sock.send(pickle.dumps(msg), cli.addr)

	def __main(self):
		while True:
			try:
				raw, addr = self.sock.recvfrom(4096)
				mtype, data = pickle.loads(raw)

				if mtype == TYPE_CONNECT:
					userData = pickle.loads(data)
					if userData["name"] not in self.clients.keys():
						msg = f"[ SERVER ] :: {userData['name']} has entered the game!"
						userData["msg"] = msg
						self.broadcast((
							TYPE_CONNECT,
							pickle.dumps(userData)
						))

						user = User(userData["name"], addr)
						user.x = userData["x"]
						user.y = userData["y"]
						user.z = userData["z"]
						user.direction = userData["direction"]
						self.clients[userData["name"]] = user
						print(msg)
					else:
						msg = (
							TYPE_ERROR,
							pickle.dumps({
								"code": ERR_NAME_TAKEN,
								"msg": f"[ SERVER ] :: The name \"{userData['name']}\" is already taken."
							})
						)
						self.sock.send(pickle.dumps(msg), addr)
				elif mtype == TYPE_DISCONNECT:
					del self.clients[data]
					msg = f"[ SERVER ] :: {data} has left the game..."
					self.broadcast((
						TYPE_DISCONNECT,
						pickle.dumps({
							"msg": msg,
							"name": data
						})
					))
					print(msg)
				elif mtype == TYPE_PLAYER_CHANGE:
					posData = pickle.loads(data)
					who = posData["name"]
					self.clients[who].x = posData["x"]
					self.clients[who].y = posData["y"]
					self.clients[who].z = posData["z"]
					self.clients[who].direction = posData["direction"]
					self.broadcast((
						TYPE_PLAYER_CHANGE,
						data
					), exceptions=[who])
				elif mtype == TYPE_TEST:
					print("Testing Socket! Message: " + data)
					self.broadcast((TYPE_TEST, "MSG: " + data))
			except:
				pass

		self.sock.close()
	

def new_thread(proc, args=()):
	th = threading.Thread(target=proc, args=args)
	th.daemon = True
	th.start()

class Client:
	def init(self, host="191.252.103.220", port=1360):
		self.addr = (host, port)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setblocking(False)

		new_thread(self.__main)
	
	def onChange(self, data):
		pass

	def onConnect(self, data):
		pass

	def onDisconnect(self, data):
		pass

	def onError(self, data):
		pass

	def send(self, msg):
		self.sock.sendto(pickle.dumps(msg), self.addr)

	def __main(self):
		while True:
			try:
				raw, addr = self.sock.recvfrom(4096)
				if not raw: continue

				mtype, data = pickle.loads(raw)

				if mtype == TYPE_CONNECT:
					userData = pickle.loads(data)
					self.onConnect(userData)
					print(userData["msg"])
				elif  mtype == TYPE_DISCONNECT:
					userData = pickle.loads(data)
					self.onDisconnect(userData)
					print(userData["msg"])
				elif mtype == TYPE_PLAYER_CHANGE:
					posData = pickle.loads(data)
					self.onChange(posData)

				elif mtype == TYPE_ERROR:
					dat = pickle.loads(data)
					self.onError(dat)
					print(dat["msg"])

			except:
				pass
		
		self.sock.close()

if __name__ == "__main__":
	serv = Server()