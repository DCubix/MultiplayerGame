# pylint: disable=no-member
# pylint: disable=no-name-in-module

import pygame
from pygame.constants import (QUIT)

from renderer import Renderer

class GameAdapter:
	def __init__(self):
		self.shouldQuit = False

	def onCreate(self): pass
	def onDraw(self, renderer): pass
	def onUpdate(self, dt): pass
	def onEvent(self, e): pass
	def onQuit(self): pass

	def exitGame(self): self.shouldQuit = True

class Timer:
	def __init__(self):
		self.frame = 0
		self.speed = 0.1
		self.time = 0.0
	
	def tick(self, dt):
		f = self.frame
		self.time += dt
		if self.time >= self.speed:
			self.time = 0
			self.frame += 1
		return f

class Engine:

	assets = {}

	@staticmethod
	def loadImage(name, path):
		if not name in Engine.assets.keys():
			Engine.assets[name] = pygame.image.load(path)
		return Engine.assets[name]

	@staticmethod
	def init(adapter, title="Game", size=(800, 600)):
		if adapter is None: return

		pygame.init()

		screen = pygame.display.set_mode(size, depth=32)
		pygame.display.set_caption(title)

		renderer = Renderer(screen)

		clock = pygame.time.Clock()
		running = True

		adapter.onCreate()

		while running:
			clock.tick(60)

			for event in pygame.event.get():
				if event.type == QUIT:
					running = False
				else:
					adapter.onEvent(event)
			
			delta = clock.get_time() / 1000.0

			adapter.onUpdate(delta)
			adapter.onDraw(renderer)

			pygame.display.flip()

			if adapter.shouldQuit:
				running = False

		adapter.onQuit()
		pygame.quit()