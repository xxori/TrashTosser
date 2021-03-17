import random
import os
import time

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

import pygame
from pygame import Vector2

import sprites

pygame.init()

SIZE_X = 1120
SIZE_Y = 560

GRAVITY = 1

FRAMECAP = 60
CHECK_VECTOR = Vector2(1,0)

class GameObject(pygame.sprite.Sprite):
    """
    Base object template that will be inherited and extended by each specifc object

    Attributes:
        game: trashtosser.Game
            The game object of which this object is a child of, used to get important variables such as the screen

        draw_priority: int
            Determines the order of the object being drawn in relation to all other objects, used to put objects behind others

        pos: Vector2
            Top left corner position vector

        rect: pygame.Rect
            The local rectangle representing the sprite

        global_rect: pygame.Rect
            Global rect offset by global coordinates used for collision and other inter-object interactions
    """
    def __init__(self, parent, x, y, image=None, angle=0):
        super(GameObject, self).__init__()

        self.game = parent
        self.pos = Vector2(x,y)

        self.angle = angle

        self.image = image or pygame.Surface((0, 0))
        self.rect = self.image.get_rect()

        self.global_rect = pygame.Rect(self.rect.x+x,self.rect.y+y,self.rect.w,self.rect.h)

    def update(self, dt, keys):
        """
        Class-specific method to update position, check collision, etc.. that is run every frame
        On the base object it does nothing but should be overwritten for each object
        It exists here so an error is not raised if an object does not have it overwritten for whatever reason
        """
        pass

    def draw(self):
        """
        Rotates the sprite by appropriate angle and then draws to the game screen
        """
        if self.angle == 0:
            pos = (self.pos.x,self.pos.y)
            image = self.image
        else:
            width,height = self.image.get_size()

            boundary = [
                Vector2(0,0),
                Vector2(width,0),
                Vector2(width,-height),
                Vector2(0,-height)
            ]

            boundary = [vector.rotate(self.angle) for vector in boundary]

            min_x = min(boundary, key=lambda vec: vec.x)[0]

            max_y = max(boundary, key=lambda vec: vec.y)[1]

            center = Vector2(
                (width/2),
                -(height/2)
            )

            rotation_offset = center.rotate(self.angle) - center

            pos = (
                self.pos.x + min_x - rotation_offset.x,
                self.pos.y + max_y - rotation_offset.y
            )

            image = pygame.transform.rotate(self.image, self.angle)

        self.rect = image.get_rect()

        self.global_rect = pygame.Rect(
            pos[0], pos[1],
            self.rect.w, self.rect.h
        )

        self.game.surface.blit(image, pos)

    def log(self, *args):
        """Shorthand for GameObject.game.log"""
        self.game.log(*args)





class Ball(GameObject):
    def __init__(self, parent, x, y, vx, vy):
        super().__init__(parent, x, y, sprites.player)
        # Position and velocity vectors
        self.pos = Vector2(x,y)
        self.vel = Vector2(vx,vy)
        # Random color for each ball
        self.color = (random.randint(0,255),random.randint(0,255),random.randint(0,128))

        self.paused = True

        self.initial_length = self.vel.magnitude()

        # Scalar for the ball so the launch power can be changed
        self.power = 1

        self.TRAJECTORY_BALLS = 20

        self.trajectory = []
        self.old_trajectory = []

        self.scored = False

        self.collider = pygame.Rect(self.global_rect.x + self.vel.x,
                                    self.global_rect.y + self.vel.y,
                                    self.global_rect.w,
                                    self.global_rect.h)


    """def draw(self, surface):
        # Draw circle and line showing velocity vector
        #pygame.draw.line(screen, (255, 255, 255), self.pos, self.pos + (Vector2(self.vel.x,-self.vel.y) * 5), width=5)
        for dot in self.old_trajectory:
            pygame.draw.circle(surface,	(128,128,255), dot[0], dot[1])
        if self.paused:
            for dot in self.trajectory:
                pygame.draw.circle(surface,(255,255,255),dot[0],dot[1])

        pygame.draw.circle(surface, self.color, self.pos, 20)"""


    def update(self, dt, keys):
        # Calculate the trajectory indicators
        if self.paused:
            self.trajectory = []
            for i in range(self.TRAJECTORY_BALLS):
                self.trajectory.append((self.pos+i*Vector2(self.vel.x,self.vel.y+0.5*GRAVITY*i)+Vector2(self.global_rect.w/2,self.global_rect.h/2), 5-i/4))

        # Only calculate if the ball is moving and not paused
        if not self.paused and self.vel != Vector2(0,0):
            # Apply velocity
            self.pos += Vector2(self.vel.x,self.vel.y) * dt
            # Apply gravity
            self.vel.y += GRAVITY * dt

            # If the ball is off screen
            if self.pos.y >= (SIZE_Y-self.rect.h) - (self.vel.y * dt):
                # If the ball is going very slow then don't flip it and set the velocity to 0 instead
                if abs(self.vel.x) < 5 and abs(self.vel.y) < 5 and self.pos.y > (SIZE_Y-100):
                    self.vel = Vector2(0, 0)
                    self.pos.y = SIZE_Y-self.rect.h
                # Otherwise, flip the y velocity and times the velocity by 2/3 of it's current
                else:
                    self.flipy()

        if keys[pygame.K_LSHIFT]:
            mod = 0.3
        else:
            mod = 1

        if self.paused:
            # Rotate with left and right arrows
            if keys[pygame.K_LEFT]:
                if self.vel.angle_to(CHECK_VECTOR) < 90:
                    self.vel.rotate_ip(-mod * dt)
            if keys[pygame.K_RIGHT]:
                if self.vel.angle_to(CHECK_VECTOR) > 0:
                    self.vel.rotate_ip(mod * dt)

            # Change power with up and down
            if keys[pygame.K_UP]:
                if self.power < 2:
                    self.power += mod * 0.02 * dt
                    self.vel.scale_to_length(self.initial_length * self.power)
            if keys[pygame.K_DOWN]:
                if self.power > 0.5:
                    self.power -= mod * 0.02 * dt
                    self.vel.scale_to_length(self.initial_length * self.power)

        self.collider = pygame.Rect(self.global_rect.x + self.vel.x,
                                    self.global_rect.y + self.vel.y,
                                    self.global_rect.w,
                                    self.global_rect.h)

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

class Bin(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.pos = Vector2(x,y)
        self.rect = pygame.Rect(self.pos.x,self.pos.y,50,200)
        self.goal_rect = pygame.Rect(self.pos.x,self.pos.y-10,50,10)

    def draw(self, surface):
        pygame.draw.rect(surface,(255,0,0),[self.pos.x,self.pos.y,50,200])
        pygame.draw.rect(surface,(0,0,0),[self.pos.x,self.pos.y-10,50,10])
        pygame.draw.rect(surface,(0,255,0),self.goal_rect)

    def check_collision(self, ball: Ball):
        if self.rect.colliderect(ball.collider):
            ball.flipx()

        if self.goal_rect.colliderect(ball.collider):
            ball.scored = True
            ball.reset()

class Game:
    def __init__(self):
        self.running = False
        self.surface = pygame.display.set_mode((SIZE_X,SIZE_Y))
        pygame.display.set_caption("Trash Tosser")

        self.clock = pygame.time.Clock()

        self.ball = Ball(self, 20,400,10,-10)
        self.obstacles = []


        self.last_frame = time.time()

    def run_until_finished(self):
        self.running = True
        self.reset()
        while self.running:
            current_frame = time.time()
            dt = (current_frame-self.last_frame) * FRAMECAP
            self.last_frame = current_frame
            keys = self.handle_events(pygame.event.get())

            self.ball.update(dt, keys)

            self.surface.fill((0,0,128))

            for obstacle in self.obstacles:
                obstacle.check_collision(self.ball)
                obstacle.draw(self.surface)

            for dot in self.ball.old_trajectory:
                pygame.draw.circle(self.surface, (128, 128, 255), dot[0], dot[1])
            if self.ball.paused:
                for dot in self.ball.trajectory:
                    pygame.draw.circle(self.surface, (255, 255, 255), dot[0], dot[1])

            self.ball.draw()

            pygame.display.update()
            self.clock.tick(FRAMECAP)




    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.running=False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.ball.paused = False
                if event.key == pygame.K_r:
                    self.reset()

        return pygame.key.get_pressed()

    def reset(self):
        self.ball = Ball(self, 20,400,10,-10)
        self.obstacles= [Bin(600, SIZE_Y - 200)]

if __name__ == "__main__":
    game = Game()
    game.run_until_finished()
    pygame.quit()