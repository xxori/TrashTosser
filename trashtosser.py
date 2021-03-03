import pygame
import random
from pygame import Vector2

pygame.init()

SIZE_X = 1000
SIZE_Y = 500

GRAVITY = 1


screen = pygame.display.set_mode((SIZE_X,SIZE_Y))
pygame.display.set_caption("Trash Tosser")

done = False

clock = pygame.time.Clock()
trail=[]
class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy):
        super().__init__()
        # Position and velocity vectors
        self.pos = Vector2(x,y)
        self.vel = Vector2(vx,vy)
        # Random color for each ball
        self.color = (random.randint(0,255),random.randint(0,255),random.randint(0,128))
        self.paused = True
        # Scalar for the ball so the launch power can be changed
        self.scalar = 15


    def draw(self, surface):
        # Draw circle and line showing velocity vector
        pygame.draw.circle(surface, self.color, self.pos, 20)
        #pygame.draw.line(screen, (255, 255, 255), self.pos, self.pos + (Vector2(self.vel.x,-self.vel.y) * 5), width=5)
        if self.paused:
            for i in range(20):
                pygame.draw.circle(surface,(255,255,255),(self.pos+i*Vector2(self.vel.x,-self.vel.y+0.5*i*GRAVITY)), 5-i/4)

    def update(self):
        # Only calculate if the ball is moving and not paused

        if not self.paused and self.vel != Vector2(0,0):
            # Apply velocity
            self.pos += Vector2(self.vel.x,-self.vel.y)
            # Apply gravity
            self.vel.y -= GRAVITY

            # If the ball is off screen
            if self.pos.y >= 480 + self.vel.y:
                # If the ball is going very slow then don't flip it and set the velocity to 0 instead
                if abs(self.vel.x) < 5 and abs(self.vel.y) < 5 and self.pos.y > 450:
                    self.vel = Vector2(0, 0)
                    self.pos.y = 480
                # Otherwise, flip the y velocity and times the velocity by 2/3 of it's current
                else:
                    self.vel.y *= -1
                    self.vel.scale_to_length(self.vel.magnitude()*0.66)

    def reset(self):
        self.pos = Vector2(20, 400)
        self.vel = Vector2(10, 10)
        self.vel.scale_to_length(15)
        self.paused = True
        self.scalar = 15



ball = Ball(20,400,10,10)
ball.vel.scale_to_length(15)

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # If user clicked close
            done = True # Flag that we are done so we exit this loop
        if event.type == pygame.KEYDOWN:
            if event.key==pygame.K_SPACE:
                # Fire the ball
                ball.paused = False
            if event.key==pygame.K_r:
                ball.reset()

    keys = pygame.key.get_pressed()
    if ball.paused:
        # Rotate with left and right arrows
        if keys[pygame.K_LEFT]:
            if ball.vel.angle_to(ball.pos) > 0:
                ball.vel.rotate_ip(1)
        if keys[pygame.K_RIGHT]:
            if ball.vel.angle_to(ball.pos) < 80:
                ball.vel.rotate_ip(-1)

        # Change power with up and down
        if keys[pygame.K_UP]:
            if ball.scalar < 20:
                ball.scalar += 0.1
                ball.vel.scale_to_length(ball.scalar)
        if keys[pygame.K_DOWN]:
            if ball.scalar > 10:
                ball.scalar -= 0.1
                ball.vel.scale_to_length(ball.scalar)

    # Update and draw ball with blue background
    ball.update()

    screen.fill((0,0,255))
    ball.draw(screen)
    # Flip display and limit to 60 fps
    pygame.display.update()

    clock.tick(60)

pygame.quit()
