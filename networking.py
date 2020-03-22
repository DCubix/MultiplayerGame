import socket, threading, pickle, time

TYPE_PLAYER_GOTO = 1
TYPE_SEND_MESSAGE = 2
TYPE_CONNECT = 3
TYPE_DISCONNECT = 4
TYPE_ERROR = 5
TYPE_TEST = 6
TYPE_USERLIST = 7

ERR_NAME_TAKEN = 1

class User:
	def __init__(self, name, addr):
		self.name = name
		self.addr = addr
		self.x = 0
		self.y = 0
		self.z = 0

class Server:
	def __init__(self, host="0.0.0.0", port=11360):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setblocking(False)
		self.sock.bind((host, port))
		
		self.clients = {}

		self.__main()

	def broadcast(self, msg, exceptions=[]):
		for n, cli in self.clients.items():
			if n in exceptions:
				continue
			self.sock.sendto(pickle.dumps(msg), cli.addr)

	def __main(self):
		while True:
			try:
				raw, addr = self.sock.recvfrom(4096)
				if not raw:
					continue
				mtype, data = pickle.loads(raw)

				if mtype == TYPE_CONNECT:
					userData = pickle.loads(data)
					if userData["name"] not in self.clients.keys():
						msg = f"{userData['name']} has entered the game!"
						userData["msg"] = msg
						userData["users"] = list(self.clients.values())
						
						user = User(userData["name"], addr)
						user.x = userData["x"]
						user.y = userData["y"]
						user.z = userData["z"]
						self.clients[userData["name"]] = user
						print(msg)

						self.broadcast((
							TYPE_CONNECT,
							pickle.dumps(userData)
						), exceptions=[userData["name"]])

						self.broadcast((
							TYPE_SEND_MESSAGE,
							pickle.dumps({
								"user": "[SERVER]",
								"msg": msg,
								"color": (245, 120, 66)
							})
						), exceptions=[userData["name"]])
					else:
						msg = (
							TYPE_ERROR,
							pickle.dumps({
								"code": ERR_NAME_TAKEN,
								"msg": f"[ SERVER ] :: The name \"{userData['name']}\" is already taken."
							})
						)
						self.sock.sendto(pickle.dumps(msg), addr)
				elif mtype == TYPE_DISCONNECT:
					del self.clients[data]
					msg = f"{data} has left the game..."
					self.broadcast((
						TYPE_DISCONNECT,
						pickle.dumps({
							"msg": msg,
							"name": data
						})
					))
					self.broadcast((
						TYPE_SEND_MESSAGE,
						pickle.dumps({
							"user": "[SERVER]",
							"msg": msg,
							"color": (245, 120, 66)
						})
					))
					print(msg)
				elif mtype == TYPE_PLAYER_GOTO:
					posData = pickle.loads(data)
					who = posData["name"]
					self.clients[who].x = posData["x"]
					self.clients[who].y = posData["y"]
					self.clients[who].z = posData["z"]
					self.broadcast((
						TYPE_PLAYER_GOTO,
						data
					))
				elif mtype == TYPE_TEST:
					print("Testing Socket! Message: " + data)
					self.sock.sendto(pickle.dumps((TYPE_TEST, "MSG: " + data)), addr)
				elif mtype == TYPE_USERLIST:
					name = data
					users = [x for x in self.clients.values() if x.name != name]
					self.sock.sendto(pickle.dumps((TYPE_USERLIST, users)), addr)
				elif mtype == TYPE_SEND_MESSAGE:
					msgData = pickle.loads(data)
					_from = msgData["user"]
					msg = msgData["msg"]
					print(f"[ {_from} ] :: {msg}")
					self.broadcast((
						TYPE_SEND_MESSAGE,
						data
					), exceptions=[_from])

			except socket.error as e:
				if e.args[0] == socket.errno.EWOULDBLOCK:
					time.sleep(1)
				else:
					print(e)
					break

		self.sock.close()
	

def new_thread(proc, args=()):
	th = threading.Thread(target=proc, args=args)
	th.daemon = True
	th.start()

class Client:
	def init(self, host="191.252.103.220", port=11360):
		self.addr = (host, port)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setblocking(False)

		self.running = True

		new_thread(self.__main)
	
	def onGotoTarget(self, data):
		pass

	def onUserList(self, users):
		pass

	def onConnect(self, data):
		pass

	def onDisconnect(self, data):
		pass

	def onError(self, data):
		pass

	def onMessageReceived(self, _from, msg, color):
		pass

	def send(self, msg):
		self.sock.sendto(pickle.dumps(msg), self.addr)

	def __main(self):
		while self.running:
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
				elif mtype == TYPE_PLAYER_GOTO:
					posData = pickle.loads(data)
					self.onGotoTarget(posData)
				elif mtype == TYPE_ERROR:
					dat = pickle.loads(data)
					self.onError(dat)
					print(dat["msg"])
				elif mtype == TYPE_USERLIST:
					self.onUserList(data)
				elif mtype == TYPE_SEND_MESSAGE:
					msgData = pickle.loads(data)
					self.onMessageReceived(msgData["user"], msgData["msg"], msgData["color"])

			except:
				pass
		
		self.sock.close()

if __name__ == "__main__":
	# serv = Server(host="localhost")
	serv = Server()