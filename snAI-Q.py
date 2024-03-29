# -*- coding: utf-8 -*-
# @Author: pedrotorres
# @Date:   2019-08-07 14:04:45
# @Last Modified by:   Pedro Torres
# @Last Modified time: 2019-08-15 11:27:46

import sys
from random import randrange, randint
import pygame
from pygame.locals import *
from keras.utils import to_categorical
import Q
import numpy as np

RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

DOWN = 2
LEFT = 4
RIGHT = 6
UP = 8

WIDTH = 200
HEIGHT = 200

class app(object):
	
	def __init__(self):
		self.display_width = WIDTH
		self.display_height = HEIGHT
		self.display = pygame.display.set_mode((self.display_width, self.display_height))
		self.window_color = BLACK
		self.display.fill(self.window_color)
		self.clock = pygame.time.Clock()
		self.ended = False
		
		pygame.display.set_caption('snAI-Q')

	def collision(self, snake_pos, apple_pos):
		if (snake_pos == apple_pos):
			return True
		else:
			return False

	def game_over(self, snake_pos):
		if self.collision(snake_pos[1], 0):
			return True

		elif self.collision(snake_pos[1], HEIGHT - 10):
			return True

		elif self.collision(snake_pos[0], 0):
			return True

		elif self.collision(snake_pos[0], WIDTH - 10):
			return True

		else:
			return False

	def update(self, snake, apple):
			collision = self.collision(snake.structure[0], apple.pos)

			if collision:
				snake.food_score = snake.food_score + 1
				apple.pos = apple.generate_pos()
				# can be any value because the values will be copied after this point
				snake.structure.append((0, 0))

			# each cell i of snake receive cell i-1
			for i in range(len(snake.structure) - 1, 0, -1):
				snake.structure[i] = snake.structure[i-1]
			
			# move head of snake according to direction
			if snake.direction == UP:
				snake.structure[0] = (snake.structure[0][0], snake.structure[0][1] - 10)
			if snake.direction == DOWN:
				snake.structure[0] = (snake.structure[0][0], snake.structure[0][1] + 10)
			if snake.direction == LEFT:
				snake.structure[0] = (snake.structure[0][0] - 10, snake.structure[0][1])
			if snake.direction == RIGHT:
				snake.structure[0] = (snake.structure[0][0] + 10, snake.structure[0][1])
			
			# game over conditions
			if self.game_over(snake.structure[0]):
				self.ended = True

			if snake.hit_itself():
				self.ended = True

	def display_interface(self, snake, apple):
		app_obj.display.fill(app_obj.window_color)

		# draw snake
		for pos in snake.structure:
			self.display.blit(snake.skin, pos)

		# draw apple
		app_obj.display.blit(apple.skin, apple.pos)

		# draw boundaries
		for x in range(0, WIDTH, 10):
			pygame.draw.rect(self.display, GREEN, (x, 0, 10, 10))
			pygame.draw.rect(self.display, GREEN, (x, HEIGHT - 10, 10, 10))

		for y in range(0, HEIGHT, 10):
			pygame.draw.rect(self.display, GREEN, (0, y, 10, 10))
			pygame.draw.rect(self.display, GREEN, (WIDTH - 10, y, 10, 10))
		
		# grid
		for x in range(0, WIDTH, 10): # Draw vertical lines
			pygame.draw.line(self.display, (40, 40, 40), (x, 0), (x, HEIGHT))
		
		for y in range(0, HEIGHT, 10): # Draw vertical lines
			pygame.draw.line(self.display, (40, 40, 40), (0, y), (WIDTH, y))

		pygame.display.update()

class snake(object):
	def __init__(self):
		self.structure = [(100, 100), (110, 100), (120, 100)]
		self.direction = LEFT
		self.skin = pygame.Surface((10, 10))
		self.food_score = 0

		self.skin.fill(WHITE)

	def hit_itself(self):
		for i in range(1, len(self.structure)):
			if self.structure[0] == self.structure[i]:
				return True
		
		return False

def initialize_game(app, snake, apple, agent):
	initial_state = agent.get_state(snake, apple)
	inital_food_score = snake.food_score
	
	# left, right, up, down
	action = [1, 0, 0, 0]
	move(action, snake)
	app.update(snake, apple)
	app.display_interface(snake_obj, apple)

	second_state = agent.get_state(snake, apple)
	second_food_score = snake.food_score
	# print(second_state)

	reward = agent.set_reward(snake, apple, inital_food_score != second_food_score, app.ended)
	agent.remember(initial_state, action, reward, second_state, app.ended)
	agent.replay()

def move(action, snake):
	if action[0]:
		if snake_obj.direction == UP or snake_obj.direction == DOWN:
			snake_obj.direction = LEFT

	if action[1]:
		if snake_obj.direction == UP or snake_obj.direction == DOWN:
			snake_obj.direction = RIGHT

	elif action[2]:
		if snake_obj.direction == LEFT or snake_obj.direction == RIGHT:
			snake_obj.direction = UP

	elif action[3]:
		if snake_obj.direction == LEFT or snake_obj.direction == RIGHT:
			snake_obj.direction = DOWN

def manual_move(snake_obj):
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

class apple(object):
	def __init__(self):
		self.skin = pygame.Surface((10, 10))
		self.pos = self.generate_pos()
		self.skin.fill(RED)

	def generate_pos(self):
		# -1 to not spawn on horizontal and vertical bars
		return (randrange(1, (WIDTH // 10) - 1) * 10, randrange(1, (HEIGHT // 10) - 1) * 10)


if __name__ == "__main__":

	pygame.init()

	counter_games = 0
	agent_obj = Q.agent()

	max_score = 0

	while counter_games < 1000:
		app_obj = app()
		snake_obj = snake()
		apple_obj = apple()

		# snake_obj.structure.append((0,0))
		# snake_obj.structure.append((0,0))
		# snake_obj.structure.append((0,0))
		# snake_obj.structure.append((0,0))
		# snake_obj.structure.append((0,0))
		# snake_obj.structure.append((0,0))
		# snake_obj.structure.append((0,0))

		# initialize_game(app_obj, snake_obj, apple_obj, agent_obj)
		n_moves = 0
		flag_food = False

		while not app_obj.ended:
			# app_obj.clock.tick(8)
			
			# manual_move(snake_obj)
			# app_obj.update(snake_obj, apple_obj)
			# app_obj.display_interface(snake_obj, apple_obj)
			# print(agent_obj.get_state(snake_obj, apple_obj)[-4:])
		

			agent_obj.epsilon = 90 - counter_games
			
			if (agent_obj.epsilon < 0):
				agent_obj.epsilon = 0

			#get old state
			state_old = agent_obj.get_state(snake_obj, apple_obj)
			# print('old: {}'.format(state_old))
			inital_food_score = snake_obj.food_score
				
			if randint(0, 100) < agent_obj.epsilon:
				final_move = to_categorical(randint(0, 2), num_classes=4)
			else:
				prediction = agent_obj.model.predict(np.array(state_old).reshape((1, 16)))
				final_move = to_categorical(np.argmax(prediction[0]), num_classes=4)

			move(final_move, snake_obj)
			n_moves += 1
			app_obj.update(snake_obj, apple_obj)

			# print(agent_obj.get_state(snake_obj, apple_obj))
			# print(agent_obj.get_state(snake_obj, apple_obj)[-4:])

			app_obj.display_interface(snake_obj, apple_obj)
			new_state = agent_obj.get_state(snake_obj, apple_obj)
			second_food_score = snake_obj.food_score

			flag_food = inital_food_score != second_food_score

			if (n_moves == 250):
				app_obj.ended = True
				print('loop?')

			if flag_food:
				n_moves = 0

			reward = agent_obj.set_reward(snake_obj, apple_obj, flag_food, app_obj.ended)

			agent_obj.train_short_memory(state_old, final_move, reward, new_state, app_obj.ended)

			agent_obj.remember(state_old, final_move, reward, new_state, app_obj.ended)

		agent_obj.replay()
		agent_obj.ended = False
		counter_games += 1
		print('gn: {} | gamescore: {}'.format(counter_games, snake_obj.food_score))		
		if (max_score < snake_obj.food_score):
			max_score = snake_obj.food_score
	
	print(max_score)
	agent_obj.model.save_weights('weights.hdf5')
			