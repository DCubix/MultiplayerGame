# pylint: disable=no-member
# pylint: disable=no-name-in-module

import pygame, math
from entity import Entity
from engine import Engine, Timer
from renderer import fromScreen, toScreen

STAND = 0
SIT = 16
WALK_BL = 32
WALK_L = 48
WALK_TL = 64
WALK_T = 80
WALK_TR = 96
WALK_R = 112
WALK_RB = 128
WALK_B = 144

IDLE = 0
WALKING_TO_TARGET = 1

class BasePlayer(Entity):
	def __init__(self):
		super().__init__()
		self.timer = Timer()
		self.timer.speed = 0.11
		self.direction = 0

		self.directions = [7, 0, 1, 2, 3, 4, 5, 6]
		self.walkDirections = [WALK_B, WALK_BL, WALK_L, WALK_TL, WALK_T, WALK_TR, WALK_R, WALK_RB]

		self.state = IDLE
		self.target = (0, 0)

		self.mouse = (0, 0)

		self.tag = "player"
		self.name = "Guest"

	def onCreate(self):
		self.spr = Engine.loadImage("char", "assets/character.png")

	def onDraw(self, ren):
		self.mouse = ren.mousePos()

		x, y = toScreen(self.x, self.y, self.z)
		frame = 0

		if self.state == IDLE:
			frame = self.directions[self.direction]
		elif self.state == WALKING_TO_TARGET:
			frame = self.walkDirections[self.direction] + (self.timer.frame % 7)

		ren.tile(self.spr, x, y, frame + 8, config=(8, 20), origin=(0.5, 0.86))
		ren.tile(self.spr, x, y - (64 * 0.85), frame, config=(8, 20), origin=(0.5, 1.0))


class Player(BasePlayer):
	def __init__(self, name="Guest"):
		super().__init__()
		self.name = name

	def onEvent(self, e):
		mx, my = self.mouse
		ix, iy = fromScreen(mx, my)

		if pygame.mouse.get_pressed()[0]:
			self.state = WALKING_TO_TARGET
			self.target = (ix, iy)

	def onUpdate(self, dt):
		self.timer.tick(dt)

		if self.state == WALKING_TO_TARGET:
			dx = self.target[0] - self.x
			dy = self.target[1] - self.y
			mag = math.sqrt(dx * dx + dy * dy)
			dx /= mag
			dy /= mag

			angle = math.atan2(dy, dx) + math.pi
			ratio = ((angle / math.pi) * 0.5 + 0.5)
			self.direction = math.floor(ratio * 7) % 7

			self.x += dx * dt * 140.0
			self.y += dy * dt * 140.0

			if mag <= 5.0:
				self.state = IDLE
