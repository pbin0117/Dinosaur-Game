import pygame
import neat
import time
import os
import random

pygame.font.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500

DINO_IMG = [pygame.image.load(os.path.join("sprites", "dino1.png")),
			pygame.image.load(os.path.join("sprites", "dino2.png")),
			pygame.image.load(os.path.join("sprites", "dino3.png")),
			pygame.image.load(os.path.join("sprites", "dino_duck1.png")),
			pygame.image.load(os.path.join("sprites", "dino_duck2.png"))]
GROUND_IMG = pygame.image.load(os.path.join("sprites", "ground.png"))
BIRD_IMG = [pygame.image.load(os.path.join("sprites", "bird1.png")),
			pygame.image.load(os.path.join("sprites", "bird2.png"))]
CACTUS_IMG = [pygame.image.load(os.path.join("sprites", "big_cacti2.png")),
			  pygame.image.load(os.path.join("sprites", "cacti1.png")),
			  pygame.image.load(os.path.join("sprites", "cacti2.png")),
			  pygame.image.load(os.path.join("sprites", "cacti3.png"))]
CLOUD_IMG = pygame.image.load(os.path.join("sprites", "cloud.png"))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Dino(object):
	IMGS = DINO_IMG
	ANIMATION_TIME = 5

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.jump_count = 20
		self.img_count = 0
		self.vel = 0
		self.height = y
		self.isJumping = False
		self.isDucking = False
		self.img = self.IMGS[0]

	def jump(self):
		if not self.isJumping and not self.isDucking:
			self.isJumping = True

	def duck(self):
		if not self.isJumping and not self.isDucking:
			self.isDucking = True

	def update(self):
		self.isDucking = False
		if not self.isJumping:
			self.y = self.height

		if self.isJumping:
			if self.jump_count >= -20:
					neg = 1
					if self.jump_count < 0:
						neg = -1
					self.y -= (self.jump_count**2) / 8 * neg
					self.jump_count -= 2
			else:
				self.jump_count = 20
				self.isJumping = False

	def draw(self, win):
		self.img_count += 1

		if self.img_count < self.ANIMATION_TIME:
			self.img = self.IMGS[1]
		elif self.img_count < self.ANIMATION_TIME*2:
			self.img = self.IMGS[2]
		elif self.img_count < self.ANIMATION_TIME*2+1:
			self.img_count = 0 
			self.img = self.IMGS[1]

		if self.isDucking:
			if self.img_count < self.ANIMATION_TIME:
				self.img = self.IMGS[3]
			elif self.img_count < self.ANIMATION_TIME*2:
				self.img = self.IMGS[4]
			elif self.img_count < self.ANIMATION_TIME*2+1:
				self.img_count = 0 
				self.img = self.IMGS[3]
			


		win.blit(self.img, (self.x, self.y))

	def get_mask(self):
		return pygame.mask.from_surface(self.img)

class Obstacle(object):
	
	IMG = [CACTUS_IMG, BIRD_IMG]
	ANIMATION_TIME = 5

	def __init__(self):
		self.x = 1000
		self.y = 400
		self.passed = False
		self.type = random.randint(0, 1)
		if self.type == 0:
			self.img = self.IMG[0][random.randint(0, 3)]
		else:
			self.img = self.IMG[1][0]
			self.y = 305
		self.width = self.img.get_width()
		self.img_count = 0 

	def move(self, VEL):
		self.x -= VEL

	def draw(self, win):
		win.blit(self.img, (self.x, self.y))

		if self.type == 1:
			self.img_count += 1

			if self.img_count < self.ANIMATION_TIME:
				self.img = self.IMG[1][0]
			elif self.img_count < self.ANIMATION_TIME*2:
				self.img = self.IMG[1][1]
			elif self.img_count < self.ANIMATION_TIME*2+1:
				self.img_count = 0 
				self.img = self.IMG[1][0]


	def collide(self,dino):
		dino_mask = dino.get_mask()
		cactus_mask = pygame.mask.from_surface(self.img)

		offset = (self.x - dino.x, self.y - round(dino.y))

		point = dino_mask.overlap(cactus_mask, offset)

		if point:
			return True

		return False




class Ground(object):
	WIDTH =GROUND_IMG.get_width()
	IMG = GROUND_IMG

	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH

	def move(self, VEL):
		self.x1 -= VEL
		self.x2 -= VEL

		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH
		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, win):
		win.blit(self.IMG, (self.x1, self.y))
		win.blit(self.IMG, (self.x2, self.y))

class Cloud(object):

	IMG = CLOUD_IMG

	def __init__(self, x):
		self.x = x
		self.y = random.randint(0, 400)

	def move(self, vel):
		self.x -= vel

		if self.x + self.IMG.get_width() < 0:
			self.x = 1000
			self.y = random.randint(0, 400)

	def draw(self, win):
		win.blit(self.IMG, (self.x, self.y))


def draw_window(win, dino, ground, cacti, clouds, score):
	win.fill((255, 255, 255))

	ground.draw(win)
	for c in cacti:
		c.draw(win)

	for cloud in clouds:
		cloud.draw(win)

	text = STAT_FONT.render("Score: " + str(score), 1,(0, 0, 0))
	win.blit(text, (800 - 10 - text.get_width(), 10))

	dino.draw(win)
	pygame.display.update()

def main():
	win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

	dino = Dino(100, 380)
	obs = [Obstacle()]
	ground = Ground(WINDOW_HEIGHT - 50)
	clouds = [Cloud(500), Cloud(925), (Cloud(212))]
	clock = pygame.time.Clock()

	MAX_VEL = 20
	vel = 11
	tick = 0

	score = 0

	run = True
	while run:
		clock.tick(50)

		tick += 1

		if vel < MAX_VEL:
			if tick % 700 == 0:
				vel += 1

		if tick%12 == 0:
			score += 1

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()

		for cloud in clouds:
			cloud.move(vel / 10)

		# Adding and removing Obstacles
		add_obs = False
		rem = []

		for c in obs:
			if not c.passed and c.x < dino.x:
				c.passed = True
				add_obs = True

			if c.x + c.width < 0:
				rem.append(c)

		if add_obs:
			obs.append(Obstacle())

		for r in rem:
			obs.remove(r)
		# Dino controls
		keys = pygame.key.get_pressed()

		if keys[pygame.K_UP]:
			dino.jump()
		

		

		ground.move(vel)

		dino.update()

		if keys[pygame.K_DOWN]:
			dino.duck()
			dino.y = dino.height + 30

		for c in obs:
			c.move(vel)
			if c.collide(dino):
				print("hit")

		draw_window(win, dino, ground, obs, clouds, score)

main()
		
