class Entity:

	def __init__(self):
		self.x = 0
		self.y = 0
		self.z = 0
		self.tag = ""

		self.__life = -1
		self.__justCreated = True
		self.__dead = False

	def onCreate(self):
		pass

	def onUpdate(self, dt):
		pass

	def onDraw(self, ren):
		pass

	def onDestroy(self):
		pass

	def onEvent(self, e):
		pass

	def update(self, dt):
		if self.__dead:
			return

		if self.__justCreated:
			self.onCreate()
			self.__justCreated = False
		self.onUpdate(dt)

		if self.__life > 0.0:
			self.__life -= dt
			if self.__life <= 0.0:
				self.__life = 0.0
				self.__dead = True
				self.onDestroy()
