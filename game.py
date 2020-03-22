# pylint: disable=no-member
# pylint: disable=no-name-in-module

import pygame, pickle
from engine import Engine, GameAdapter
from renderer import fromScreen, toScreen, SORT_Y_REVERSE, SORT_Y

from networking import *
from player import *

import random

def lerp(a, b, t):
	return (1 - t) * a + b * t

class Game(GameAdapter, Client):
	def __init__(self):
		super().__init__()

	def onCreate(self):
		self.player = Player(name="guest" + str(random.randint(0, 10)))
		print(self.player.name)

		self.entities = {}
		self.entities[self.player.name] = self.player

		self.tile = Engine.loadImage("tile", "assets/blocks.png")

		self.init()

		self.send((
			TYPE_CONNECT,
			pickle.dumps({
				"name": self.player.name,
				"x": self.player.x,
				"y": self.player.y,
				"z": self.player.z,
				"direction": self.player.direction
			})
		))

	def onError(self, data):
		if data["code"] == ERR_NAME_TAKEN:
			self.exitGame()

	def onChange(self, data):
		if data["name"] == self.player.name: return
		user = self.entities[data["name"]]
		user.x = data["x"]
		user.y = data["y"]
		user.z = data["z"]
		user.direction = data["direction"]
		print(user.name)

	def onConnect(self, data):
		user = BasePlayer()
		user.x = data["x"]
		user.y = data["y"]
		user.z = data["z"]
		user.direction = data["direction"]
		user.name = data["name"]
		self.entities[user.name] = user

	def onDisconnect(self, data):
		del self.entities[data["name"]]

	def onDraw(self, renderer):
		renderer.clear(20, 120, 200)

		ply = self.player
		px, py = toScreen(ply.x, ply.y, ply.z)
		renderer.cameraX = lerp(renderer.cameraX, px, 0.25)
		renderer.cameraY = lerp(renderer.cameraY, py, 0.25)

		# ox, oy = renderer.camera()
		for y in range(10):
			for x in range(10):
				cx, cy = toScreen(x * 64, y * 64, 0)
				renderer.tile(self.tile, cx, cy, 8, config=(8, 16), origin=(0.5, 0.5))
				#pygame.draw.rect(renderer.target, (255, 0, 0), (cx-ox, cy-oy, 128, 64), 1)

		renderer.flush(sort=SORT_Y)

		for e in self.entities.values():
			e.onDraw(renderer)
		
		renderer.flush(sort=SORT_Y_REVERSE)

	def onUpdate(self, dt):
		if self.player.state == WALKING_TO_TARGET:
			self.send((
				TYPE_PLAYER_CHANGE,
				pickle.dumps({
					"name": self.player.name,
					"x": self.player.x,
					"y": self.player.y,
					"z": self.player.z,
					"direction": self.player.direction
				})
			))

		for e in self.entities.values():
			e.update(dt)

	def onEvent(self, e):
		for e in self.entities.values():
			e.onEvent(e)

	def onQuit(self):
		self.send((
			TYPE_DISCONNECT,
			self.player.name
		))

Engine.init(Game())