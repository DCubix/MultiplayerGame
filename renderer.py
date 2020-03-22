# pylint: disable=no-member
# pylint: disable=no-name-in-module

import pygame, math

SORT_NATURAL = 0
SORT_Y = 1
SORT_Y_REVERSE = 2

def fromScreen(x, y):
	return (2.0 * y + x) / 2.0, ((2.0 * y - x) / 2.0)

def toScreen(x, y, z):
	return x - y, (x + y) / 2.0 - z

class Renderer:
	def __init__(self, target):
		self.target = target
		self.sprites = []
		self.cameraX = 0
		self.cameraY = 0

		self.font = pygame.image.load("assets/font.png")
		#self.font.set_colorkey((255, 0, 255))

		self.applyCamera = True
		

	def camera(self):
		if not self.applyCamera:
			return 0, 0
		cx = self.cameraX - self.target.get_width() // 2
		cy = self.cameraY - self.target.get_height() // 2
		return cx, cy

	def mousePos(self):
		cx, cy = self.camera()
		mx, my = pygame.mouse.get_pos()
		return mx + cx, my + cy
	
	def raw(self, surf, x, y, sx=0, sy=0, sw=0, sh=0, color=(255, 255, 255, 255)):
		sw = sw if sw > 0 else surf.get_width()
		sh = sh if sh > 0 else surf.get_height()

		cx, cy = self.camera()

		self.sprites.append((surf, x - cx, y - cy, (sx, sy, sw, sh), color))

	def tile(self, surf, x, y, index, config=(1, 1), origin=(0, 0), color=(255, 255, 255, 255)):
		tw = surf.get_width() // config[0]
		th = surf.get_height() // config[1]

		sx = index % config[0] * tw
		sy = math.floor(index / config[0]) * th

		ox = int(origin[0] * tw)
		oy = int(origin[1] * th)
		self.raw(surf, x - ox, y - oy, sx=sx, sy=sy, sw=tw, sh=th, color=color)

		return (x - ox) + (tw)
	
	def char(self, c, x, y, color=(255, 255, 255, 255)):
		code = int.from_bytes(c.encode("cp437"), "big")
		return self.tile(self.font, x, y, code, config=(16, 16), color=color)

	def textWidth(self, txt):
		return (self.font.get_width() // 16) * len(txt)

	def text(self, txt, x, y, color=(255, 255, 255, 255)):
		tx = x
		ty = y
		for c in txt:
			if c == "\n":
				tx = x
				ty += self.font.get_width() // 16
			else:
				tx = self.char(c, tx, ty, color=color)

	def flush(self, sort=SORT_NATURAL):
		sprites = self.sprites
		if sort == SORT_Y:
			sprites = sorted(self.sprites, key=lambda x: x[2])
		elif sort == SORT_Y_REVERSE:
			sprites = sorted(self.sprites, key=lambda x: x[2], reverse=True)
		
		pysprites = []
		for x in sprites:
			spr = x[0]
			dest = (x[1], x[2], x[3][2], x[3][3])
			src = x[3]

			if x[4][0] != 255 or x[4][1] != 255 or x[4][2] != 255 or x[4][3] != 255:
				spr = spr.convert_alpha()
				spr.fill(x[4], None, pygame.BLEND_RGBA_MULT)

			pysprites.append((spr, dest, src))

		self.target.blits(pysprites)

		self.sprites = []
	
	def clear(self, r, g, b):
		self.target.fill((r, g, b))