import pygame
import neat
import time
import os
import random

pygame.font.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500

gen = -1
alive = 100

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


def draw_window(win, dinos, ground, cacti, clouds, score, gen, alive):
	win.fill((255, 255, 255))

	ground.draw(win)
	for c in cacti:
		c.draw(win)

	for cloud in clouds:
		cloud.draw(win)

	text = STAT_FONT.render("Score: " + str(score), 1,(0, 0, 0))
	win.blit(text, (800 - 10 - text.get_width(), 10))

	text = STAT_FONT.render("Gen: " + str(gen), 1,(0, 0, 0))
	win.blit(text, (10, 10))

	text = STAT_FONT.render("alive: " + str(alive), 1,(0, 0, 0))
	win.blit(text, (10, 60))

	for dino in dinos:
		dino.draw(win)
	pygame.display.update()

def main(genomes, config):
	global gen, alive
	gen += 1
	alive = 50

	nets = []
	ge = []
	dinos = []

	for _, g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		dinos.append(Dino(100, 380))
		g.fitness = 0
		ge.append(g)

	win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

	obs = [Obstacle()]
	ground = Ground(WINDOW_HEIGHT - 50)
	clouds = [Cloud(500), Cloud(925), (Cloud(212))]
	clock = pygame.time.Clock()

	MAX_VEL = 25
	vel = 11
	tick = 0

	score = 0

	run = True
	while run:
		clock.tick(50)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()

		# Speed, Score
		tick += 1

		if vel < MAX_VEL:
			if tick % 500 == 0:
				vel += 1

		if tick%10 == 0:
			score += 1

		

		# Clouds
		for cloud in clouds:
			cloud.move(vel / 10)


		obs_ind = 0
		if len(dinos) > 0:
			if len(obs) > 1 and dinos[0].x > obs[0].x + obs[0].width:
				obs_ind = 1
		else:
			run = False
			break

		for x, dino in enumerate(dinos):
			ge[x].fitness += 0.1

			output = nets[x].activate((obs[obs_ind].type, 
									  abs(dino.x - obs[obs_ind].x),
									  vel))

			if output[0] > 0.7:
				dino.jump()

			dino.update()

			if output[1] > 0.5:
				dino.duck()
				if dino.isDucking:
					dino.y = dino.height + 30

		# Adding and removing Obstacles
		add_obs = False
		rem = []

		for c in obs:
			for x, dino in enumerate(dinos):
				if c.collide(dino):
					ge[x].fitness -= 1
					dinos.pop(x)
					nets.pop(x)
					ge.pop(x)

					alive -= 1

			if not c.passed and c.x < dino.x:
				c.passed = True
				add_obs = True

			c.move(vel)

			if c.x + c.width < 0:
				rem.append(c)

		if add_obs:
			obs.append(Obstacle())

			for g in ge:
				g.fitness += 5

		for r in rem:
			obs.remove(r)

		ground.move(vel)


		draw_window(win, dinos, ground, obs, clouds, score, gen, alive)

def run(config_path):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
						 neat.DefaultSpeciesSet, neat.DefaultStagnation, 
						 config_path)

	p = neat.Population(config)

	# optional (stats)
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)

	winner = p.run(main ,50)
		
if __name__ == "__main__":
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, "config-feedforward.txt")
	run(config_path)