import random
import os
import time

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

import pygame
from pygame import Vector2



pygame.init()

SIZE_X = 1000
SIZE_Y = 500

GRAVITY = 1

FRAMECAP = 60
CHECK_VECTOR = Vector2(1,0)

screen = pygame.display.set_mode((SIZE_X,SIZE_Y))
pygame.display.set_caption("Trash Tosser")

done = False

clock = pygame.time.Clock()
class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy):
        super().__init__()
        # Position and velocity vectors
        self.pos = Vector2(x,y)
        self.vel = Vector2(vx,vy)
        # Random color for each ball
        self.color = (random.randint(0,255),random.randint(0,255),random.randint(0,128))

        self.paused = True

        self.initial_length = self.vel.magnitude()

        # Scalar for the ball so the launch power can be changed
        self.power = 1
        self.rect = pygame.Rect(self.pos.x + self.vel.x - 20, self.pos.y + self.vel.y - 20, 40, 40)

        self.TRAJECTORY_BALLS = 20

        self.trajectory = []
        self.old_trajectory = []

        self.scored = False


    def draw(self, surface):
        # Draw circle and line showing velocity vector
        #pygame.draw.line(screen, (255, 255, 255), self.pos, self.pos + (Vector2(self.vel.x,-self.vel.y) * 5), width=5)
        for dot in self.old_trajectory:
            pygame.draw.circle(surface,	(128,128,255), dot[0], dot[1])
        if self.paused:
            for dot in self.trajectory:
                pygame.draw.circle(surface,(255,255,255),dot[0],dot[1])

        pygame.draw.circle(surface, self.color, self.pos, 20)


    def update(self, dt):
        # Calculate the trajectory indicators
        if self.paused:
            self.trajectory = []
            for i in range(self.TRAJECTORY_BALLS):
                self.trajectory.append((self.pos+i*Vector2(self.vel.x,self.vel.y+0.5*GRAVITY*i), 5-i/4))

        # Only calculate if the ball is moving and not paused
        if not self.paused and self.vel != Vector2(0,0):
            # Apply velocity
            self.pos += Vector2(self.vel.x,self.vel.y) * dt
            # Apply gravity
            self.vel.y += GRAVITY * dt

            # If the ball is off screen
            if self.pos.y >= 480 - (self.vel.y * dt):
                # If the ball is going very slow then don't flip it and set the velocity to 0 instead
                if abs(self.vel.x) < 5 and abs(self.vel.y) < 5 and self.pos.y > 450:
                    self.vel = Vector2(0, 0)
                    self.pos.y = 480
                # Otherwise, flip the y velocity and times the velocity by 2/3 of it's current
                else:
                    self.flipy()
        self.rect = pygame.Rect(self.pos.x + self.vel.x - 20, self.pos.y + self.vel.y - 20, 40, 40)

    def reset(self):
        self.pos = Vector2(20, 400)
        self.vel = Vector2(10, -10)
        self.paused = True
        self.power = 1

    def flipx(self):
        if self.vel != Vector2(0,0):
            self.vel.x *= -1
            self.vel.scale_to_length(self.vel.magnitude()*0.66)
    def flipy(self):
        if self.vel != Vector2(0,0):
            self.vel.y *= -1
            self.vel.scale_to_length(self.vel.magnitude()*0.66)

class Bin:
    def __init__(self,x,y):
        self.pos = Vector2(x,y)
        self.rect = pygame.Rect(self.pos.x,self.pos.y,50,200)
        self.goal_rect = pygame.Rect(self.pos.x,self.pos.y-10,50,10)

    def draw(self, surface):
        pygame.draw.rect(surface,(255,0,0),[self.pos.x,self.pos.y,50,200])
        pygame.draw.rect(surface,(0,0,0),[self.pos.x,self.pos.y-10,50,10])
        pygame.draw.rect(surface,(0,255,0),self.goal_rect)

    def check_collision(self, ball: Ball):
        if self.rect.colliderect(ball.rect):
            ball.flipx()

        if self.goal_rect.colliderect(ball.rect):
            ball.scored = True
            ball.reset()


ball = Ball(20,400,10,-10)
trashcan = Bin(600,300)

last_frame = time.time()

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # If user clicked close
            done = True # Flag that we are done so we exit this loop
        if event.type == pygame.KEYDOWN:
            if event.key==pygame.K_SPACE:
                # Fire the ball
                ball.paused = False
                ball.old_trajectory = ball.trajectory
            if event.key==pygame.K_r:
                ball.reset()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LSHIFT]:
        mod = 0.3
    else:
        mod = 1

    if ball.paused:
        # Rotate with left and right arrows
        if keys[pygame.K_LEFT]:
            if ball.vel.angle_to(CHECK_VECTOR) < 90:
                ball.vel.rotate_ip(-mod)
        if keys[pygame.K_RIGHT]:
            if ball.vel.angle_to(CHECK_VECTOR) > 0:
                ball.vel.rotate_ip(mod)

        # Change power with up and down
        if keys[pygame.K_UP]:
            if ball.power < 2:
                ball.power += mod*0.02
                ball.vel.scale_to_length(ball.initial_length*ball.power)
        if keys[pygame.K_DOWN]:
            if ball.power > 0.5:
                ball.power -= mod*0.02
                ball.vel.scale_to_length(ball.initial_length * ball.power)


    now = time.time()
    dt = (now-last_frame) * FRAMECAP
    last_frame=now



    # Update and draw ball with blue background
    trashcan.check_collision(ball)
    ball.update(dt)

    screen.fill((0,0,255))
    ball.draw(screen)
    trashcan.draw(screen)
    # Flip display and limit to 60 fps
    pygame.display.update()

    clock.tick(FRAMECAP)


pygame.quit()
