# -*- coding: utf-8 -*-
# @Author: Pedro Torres
# @Date:   2019-08-08 13:40:11
# @Last Modified by:   Pedro Torres
# @Last Modified time: 2019-08-13 18:26:30

import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.optimizers import SGD, Adam
import random
from scipy.spatial import distance

DOWN = 2
LEFT = 4
RIGHT = 6
UP = 8

WIDTH = 200
HEIGHT = 200

class agent(object):
	def __init__(self):
		self.learning_rate = 0.00005
		self.gamma = 0.9
		self.epsilon = 0
		self.memory = []
		self.model = self.network()
		
		# boundaries above or below
		self.b_above = []
		self.b_below = []

		for x in range(10, WIDTH, 10):
			self.b_above.append((x, 10))
			self.b_below.append((x, HEIGHT - 20))

		# boundaries left or right
		self.b_left = []
		self.b_right = []

		for y in range(10, HEIGHT, 10):
			self.b_left.append((10, y))
			self.b_right.append((WIDTH - 20, y))

	def get_state(self, snake, apple):

		state = [
					snake.direction == DOWN,
					snake.direction == LEFT,
					snake.direction == RIGHT,
					snake.direction == UP,
					snake.structure[0][0] > apple.pos[0], # food on left
					snake.structure[0][0] < apple.pos[0], # food on right
					snake.structure[0][1] > apple.pos[1], # food above
					snake.structure[0][1] < apple.pos[1], # food below
					snake.structure[0] in self.b_left, # boundarie on left
					snake.structure[0] in self.b_right, # boundarie on right
					snake.structure[0] in self.b_above, # boundarie above
					snake.structure[0] in self.b_below, # boundarie below
				]

		state = list(map(float, state))

		return state

	# def get_state(self, snake, apple):
	# 	state = [
	# 		snake.direction == DOWN,
	# 		snake.direction == LEFT,
	# 		snake.direction == RIGHT,
	# 		snake.direction == UP,
	# 		distance.euclidean(snake.structure[0], apple.pos),
	# 		distance.euclidean(snake.structure[0][0], 10),
	# 		distance.euclidean(snake.structure[0][0], WIDTH-20),
	# 		distance.euclidean(snake.structure[0][1], 10),
	# 		distance.euclidean(snake.structure[0][0], HEIGHT-20),
	# 	]

	# 	state = list(map(float, state))

	# 	return state

	def set_reward(self, snake, apple, flag, ended):

		# [0-1] values according to distance
		d = distance.euclidean(snake.structure[0], apple.pos)
		
		if d == 0:
			self.reward = 1.0
		else:
			self.reward = 1 / (d // 10)
			# self.reward = (1 / d) * 75

		if ended:
			self.reward = -500
			return self.reward
		if flag:
			self.reward += 150
			print(self.reward)

		return self.reward
	
	def remember(self, state, action, reward, next_state, ended):
		self.memory.append((state, action, reward, next_state, ended))

	def replay(self):
		if len(self.memory) > 1000:
			minibatch = self.memory[-1000:]
		else:
			minibatch = self.memory

		for state, action, reward, next_state, ended in minibatch:
			target = reward

			if not ended:
				target = reward + self.gamma * np.amax(self.model.predict(np.array([next_state]))[0])
			
			target_f = self.model.predict(np.array([state]))
			target_f[0][np.argmax(action)] = target
			self.model.fit(np.array([state]), target_f, epochs=1, verbose=0)

	def train_short_memory(self, state, action, reward, next_state, ended):
		target = reward
		# print(np.array(next_state).reshape((1, 12)))
		if not ended:
			target = reward + self.gamma * np.amax(self.model.predict(np.array([next_state]))[0])
		target_f = self.model.predict(np.array(state).reshape((1, 12)))
		target_f[0][np.argmax(action)] = target
		# print(target_f[0][np.argmax(action)])
		
		self.model.fit(np.array([state]), target_f, epochs=1, verbose=0)

	def network(self, weights=None):
		# output left, right, up, down
		model = Sequential()
		model.add(Dense(output_dim=32, activation='relu', input_dim=12))
		model.add(Dropout(0.15))
		model.add(Dense(output_dim=32, activation='relu'))
		model.add(Dropout(0.15))
		model.add(Dense(output_dim=16, activation='relu'))
		model.add(Dropout(0.15))
		model.add(Dense(output_dim=4, activation='softmax'))
		opt = Adam(self.learning_rate)
		model.compile(loss='mse', optimizer=opt)

		return model