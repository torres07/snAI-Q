# -*- coding: utf-8 -*-
# @Author: pedrotorres
# @Date:   2019-08-07 14:04:45
# @Last Modified by:   pedrotorres
# @Last Modified time: 2019-08-07 23:37:41

import sys
from random import randrange
import pygame
from pygame.locals import *

RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

NONE = 0
DOWN = 2
LEFT = 4
RIGHT = 6
UP = 8

WIDTH = 400
HEIGHT = 400

snake = [(200, 200), (210, 200), (220, 200)]
snake_direction = LEFT

class app(object):
	"""docstring for app"""
	def __init__(self):
		self.display_width = WIDTH
		self.display_height = HEIGHT
		self.display = pygame.display.set_mode((self.display_width, self.display_height))
		self.window_color = BLACK
		self.display.fill(self.window_color)
		self.clock = pygame.time.Clock()
		
		pygame.display.set_caption('snAI-Q')

	def collision(self, snake_pos, apple_pos):
		if (snake_pos == apple_pos):
			return True
		else:
			return False

	def game_over(self, snake_pos):
		if self.collision(snake_pos[1], 0):
			return True

		elif self.collision(snake_pos[1], HEIGHT):
			return True

		elif self.collision(snake_pos[0], 0):
			return True

		elif self.collision(snake_pos[0], WIDTH):
			return True

		else:
			return False

class snake(object):
	def __init__(self):
		self.structure = [(200, 200), (210, 200), (220, 200)]
		self.direction = LEFT
		self.skin = pygame.Surface((10, 10))

		self.skin.fill(WHITE)

	def hit_itself(self):
		for i in range(1, len(self.structure)):
			if self.structure[0] == self.structure[i]:
				return True
		
		return False

class apple(object):
	def __init__(self):
		self.skin = pygame.Surface((10, 10))
		self.pos = self.generate_pos()
		
		self.skin.fill(RED)

	def generate_pos(self):
		# -1 to now spawn on horizontal and vertical bars
		return (randrange(1, (WIDTH // 10) - 1) * 10, randrange(1, (HEIGHT // 10) - 1) * 10)


if __name__ == "__main__":

	pygame.init()
	app_obj = app()
	snake_obj = snake()
	apple_obj = apple()


	while True:
		
		app_obj.clock.tick(15)
		
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

			if event.type == KEYDOWN:
				if event.key == K_UP:
					if snake_obj.direction == LEFT or snake_obj.direction == RIGHT:
						snake_obj.direction = UP
				
				if event.key == K_DOWN:
					if snake_obj.direction == LEFT or snake_obj.direction == RIGHT:
						snake_obj.direction = DOWN
				
				if event.key == K_LEFT:
					if snake_obj.direction == UP or snake_obj.direction == DOWN:
						snake_obj.direction = LEFT
				
				if event.key == K_RIGHT:
					if snake_obj.direction == UP or snake_obj.direction == DOWN:
						snake_obj.direction = RIGHT

		collision = app_obj.collision(snake_obj.structure[0], apple_obj.pos)

		if collision:
			apple_obj.pos = apple_obj.generate_pos()
			# can be any value because the values will be copied after this point
			snake_obj.structure.append((0, 0))

		# each cell i of snake receive cell i-1
		for i in range(len(snake_obj.structure) - 1, 0, -1):
			snake_obj.structure[i] = snake_obj.structure[i-1]
		
		# move head of snake according to direction
		if snake_obj.direction == UP:
			snake_obj.structure[0] = (snake_obj.structure[0][0], snake_obj.structure[0][1] - 10)
		if snake_obj.direction == DOWN:
			snake_obj.structure[0] = (snake_obj.structure[0][0], snake_obj.structure[0][1] + 10)
		if snake_obj.direction == LEFT:
			snake_obj.structure[0] = (snake_obj.structure[0][0] - 10, snake_obj.structure[0][1])
		if snake_obj.direction == RIGHT:
			snake_obj.structure[0] = (snake_obj.structure[0][0] + 10, snake_obj.structure[0][1])
		
		# game over
		if app_obj.game_over(snake_obj.structure[0]):
			print('game over')
			break

		if snake_obj.hit_itself():
			print('game over')
			break

		app_obj.display.fill(app_obj.window_color)

		# draw snake
		for pos in snake_obj.structure:
			app_obj.display.blit(snake_obj.skin, pos)

		# draw apple
		app_obj.display.blit(apple_obj.skin, apple_obj.pos)

		# draw boundaries
		for x in range(0, WIDTH, 10):
			pygame.draw.rect(app_obj.display, GREEN, (x, 0, 10, 10))
			pygame.draw.rect(app_obj.display, GREEN, (x, HEIGHT - 10, 10, 10))

		for y in range(0, HEIGHT, 10):
			pygame.draw.rect(app_obj.display, GREEN, (0, y, 10, 10))
			pygame.draw.rect(app_obj.display, GREEN, (WIDTH - 10, y, 10, 10))
		
		# # grid
		# for x in range(0, WIDTH, 10): # Draw vertical lines
		# 	pygame.draw.line(app_obj.display, (40, 40, 40), (x, 0), (x, HEIGHT))
		
		# for y in range(0, HEIGHT, 10): # Draw vertical lines
		# 	pygame.draw.line(app_obj.display, (40, 40, 40), (0, y), (WIDTH, y))


		pygame.display.update()