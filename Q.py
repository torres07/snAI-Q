# -*- coding: utf-8 -*-
# @Author: Pedro Torres
# @Date:   2019-08-08 13:40:11
# @Last Modified by:   Pedro Torres
# @Last Modified time: 2019-08-08 23:54:05

import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.optimizers import Adam

DOWN = 2
LEFT = 4
RIGHT = 6
UP = 8

WIDTH = 400
HEIGHT = 500


class agent(object):
	def __init__(self):
		self.learning_rate = 0.0005
		self.gamma = 0.9
		self.epsilon = 0
		self.state = []
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

		state = list(map(int, state))

		return state

	def set_reward(self, flag, ended):
		self.reward = 0

		if ended:
			self.reward = -10
		if flag:
			self.reward = 10

		return self.reward
	
	def remember(self, state, action, reward, next_state, ended):
		self.memory.append((state, action, reward, next_state, ended))

	def replay(self):
		for state, action, reward, next_state, ended in self.memory:
			target = reward

			if not ended:
				target = reward + self.gamma * np.amax(self.model.predict(np.array([next_state]))[0])
			

			target_f = self.model.predict(np.array([state]))
			# print(target_f)
			# print(np.argmax(action))
			target_f[0][np.argmax(action)] = target
			# print(target_f)
			self.model.fit(np.array([state]), target_f, epochs=1, verbose=0)

	def train_short_memory(self, state, action, reward, next_state, ended):
		target = reward
		if not ended:
			target = reward + self.gamma * np.amax(self.model.predict(np.array(next_state).reshape((1, 12)))[0])
		target_f = self.model.predict(np.array(state).reshape((1, 12)))
		target_f[0][np.argmax(action)] = target
		self.model.fit(np.array(state).reshape((1, 12)), target_f, epochs=1, verbose=0)

	def network(self, weights=None):
		# output left, right, up, down
		model = Sequential()
		model.add(Dense(output_dim=128, activation='relu', input_dim=12))
		model.add(Dropout(0.15))
		model.add(Dense(output_dim=128, activation='relu'))
		model.add(Dropout(0.15))
		model.add(Dense(output_dim=128, activation='relu'))
		model.add(Dropout(0.15))
		model.add(Dense(output_dim=4, activation='softmax'))
		opt = Adam(self.learning_rate)
		model.compile(loss='mse', optimizer=opt)

		return model