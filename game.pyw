# pylint: disable=no-member
# pylint: disable=no-name-in-module

import pygame, pickle
from engine import Engine, GameAdapter
from renderer import fromScreen, toScreen, SORT_Y_REVERSE, SORT_Y

from networking import *
from player import *

import random

from tkinter.simpledialog import askstring
from tkinter import Tk

root = Tk()
root.withdraw()

def lerp(a, b, t):
	return (1 - t) * a + b * t

class Game(GameAdapter, Client):
	def __init__(self):
		super().__init__()

	def onCreate(self):
		name = askstring("Name", "Enter an User name")
		if name is None:
			self.running = False
			self.exitGame()
			return

		self.player = Player(self, name=name)
		print(self.player.name)

		self.entities = {}
		self.entities[self.player.name] = self.player

		self.tile = Engine.loadImage("tile", "assets/blocks.png")

		# self.init()
		self.init(host="localhost")

		self.send((
			TYPE_CONNECT,
			pickle.dumps({
				"name": self.player.name,
				"x": self.player.x,
				"y": self.player.y,
				"z": self.player.z
			})
		))

		self.send((
			TYPE_USERLIST,
			self.player.name
		))

		self.enteringMessage = False
		self.message = "Message Goes Here"
		self.messageList = []

	def onError(self, data):
		if data["code"] == ERR_NAME_TAKEN:
			self.running = False
			self.exitGame()

	def onGotoTarget(self, data):
		if data["name"] == self.player.name: return
		user = self.entities[data["name"]]
		x = data["x"]
		y = data["y"]
		z = data["z"]
		user.goto(x, y, z)

	def onUserList(self, users):
		for u in users:
			print((u.name, u.x, u.y, u.z))
			user = BasePlayer()
			user.name = u.name
			user.x = u.x
			user.y = u.y
			user.z = u.z
			self.entities[user.name] = user

	def onConnect(self, data):
		user = BasePlayer()
		user.name = data["name"]
		user.x = data["x"]
		user.y = data["y"]
		user.z = data["z"]
		self.entities[user.name] = user

	def onDisconnect(self, data):
		del self.entities[data["name"]]
	
	def onMessageReceived(self, _from, msg, color):
		self.messageList.insert(0, (_from, msg, color))
		if len(self.messageList) > 7:
			self.messageList.pop()

	def onDraw(self, renderer):
		renderer.clear(20, 120, 200)

		ply = self.player
		px, py = toScreen(ply.x, ply.y, ply.z)
		renderer.cameraX = lerp(renderer.cameraX, px, 0.25)
		renderer.cameraY = lerp(renderer.cameraY, py, 0.25)

		# ox, oy = renderer.camera()
		for y in range(10):
			for x in range(10):
				cx, cy = toScreen(x * 32, y * 32, 0)
				renderer.tile(self.tile, cx, cy, 8, config=(8, 16), origin=(0.5, 0.5))
				#pygame.draw.rect(renderer.target, (255, 0, 0), (cx-ox, cy-oy, 128, 64), 1)

		renderer.flush(sort=SORT_Y)

		for e in self.entities.values():
			e.onDraw(renderer)

		renderer.flush(sort=SORT_Y)

		for pl in self.entities.values():
			if pl.tag != "player": continue
			if pl.name == self.player.name: continue
			lx, ly = toScreen(pl.x, pl.y, pl.z)
			renderer.text(pl.name, lx - renderer.textWidth(pl.name) / 2, ly - 76, color=(200,200,200,255))

		renderer.text(self.player.name, px - renderer.textWidth(self.player.name) / 2, py - 76, color=(20,200,50,255))
		
		renderer.applyCamera = False
		boxheight = 16 + renderer.font.get_height() // 16
		inputOff = (boxheight if not self.enteringMessage else boxheight*2)
		my = renderer.target.get_height() - inputOff
		mx = 10
		for user, msg, color in self.messageList:
			renderer.text(f"{user}: {msg}", mx, my, color=(*color, 255))
			my -= renderer.font.get_height() // 16

		if self.enteringMessage:
			pygame.draw.rect(renderer.target, (0, 0, 0, 128), (0, renderer.target.get_height() - boxheight, renderer.target.get_width(), boxheight))
			renderer.text(f">> {self.message}_", 10, renderer.target.get_height() - boxheight + 6)
		
		renderer.applyCamera = True
		renderer.flush()

	def onUpdate(self, dt):
		for e in self.entities.values():
			e.update(dt)

	def onEvent(self, evt):
		for e in self.entities.values():
			e.onEvent(evt)
		
		if self.enteringMessage and evt.type == pygame.KEYDOWN:
			if evt.key == pygame.K_RETURN or evt.key == pygame.K_KP_ENTER:
				pass
			elif evt.key == pygame.K_BACKSPACE:
				self.message = self.message[:len(self.message)-1]
			else:
				self.message += evt.unicode

		if pygame.key.get_pressed()[pygame.K_RETURN]:
			if not self.enteringMessage:
				self.message = ""
				self.enteringMessage = True
			else:
				self.send((
					TYPE_SEND_MESSAGE,
					pickle.dumps({
						"user": self.player.name,
						"msg": self.message,
						"color": (245, 158, 66)
					})
				))
				self.enteringMessage = False
				self.messageList.insert(0, (self.player.name, self.message, (245, 158, 66)))
				if len(self.messageList) > 7:
					self.messageList.pop()

	def onQuit(self):
		self.send((
			TYPE_DISCONNECT,
			self.player.name
		))

Engine.init(Game())