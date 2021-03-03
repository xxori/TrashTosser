import pygame
import random
from pygame import Vector2

pygame.init()

SIZE_X = 1000
SIZE_Y = 500


screen = pygame.display.set_mode((SIZE_X,SIZE_Y))
pygame.display.set_caption("Trash Tosser")

done = False

clock = pygame.time.Clock()

class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy):
        super().__init__()
        self.pos = Vector2(x,y)
        self.vel = Vector2(vx,vy)
        # Random color for each ball
        self.color = (random.randint(0,255),random.randint(0,255),random.randint(0,128))
        self.paused = True


    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.pos, 20)

    def update(self):
        # Apply velocity
        self.pos += Vector2(self.vel.x,-self.vel.y)
        # Apply gravity
        self.vel.y -= 1


ball = Ball(20,400,10,10)

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # If user clicked close
            done = True # Flag that we are done so we exit this loop
        if event.type == pygame.KEYDOWN:
            if event.key==pygame.K_SPACE:
                # Fire the ball
                ball.paused = False
            if event.key==pygame.K_r:
                # Reset ball pos
                ball = Ball(20,400,10,10)

    screen.fill((0,0,255))
    ball.draw(screen)

    # Update ball position if it's in motion and don't calculate if it has no velocity
    if not ball.paused and ball.vel != Vector2(0,0):
        ball.update()

    # If the ball is off the screen then half its velocity and flip the y value
    if ball.pos.y >= 480 and ball.pos.magnitude() > 0:
        ball.vel.y *= -1
        ball.vel.y /= 2
        ball.vel.x /= 2

    # Set the ball's velocity to to zero if it's really small to stop dividing infinitely
    if ball.vel.x < 1 and ball.vel.y < 1:
        ball.vel = Vector2(0,0)

    # Flip display and limit to 60 fps
    pygame.display.update()

    clock.tick(60)

pygame.quit()
