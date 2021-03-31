import random
import os
import time
import logging

# Hide the pygame support prompt
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

import pygame
from pygame import Vector2

import sprites

# Using the C API to change the app ModelID
# This changes the taskbar icon from the python one to the game-specific one
import ctypes
appid = "pthompson.trashtosser.1.0" # Arbitrary app string that is arbitrary
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

pygame.init()
pygame.font.init()

font = lambda size: pygame.font.Font(pygame.font.get_default_font(), size) # Font helper function that returns font of given size

# Game window dimensions
SIZE_X = 1120
SIZE_Y = 560

# Constant rate of gravity which is applied by moving the trash object down each frame
GRAVITY = 1

FRAMECAP = 60 # Target framerate
CHECK_VECTOR = Vector2(1,0) # Horizontal vector so overall angle of objects can be measured

class GameObject(pygame.sprite.Sprite):
    """
    Base object template that will be inherited and extended by each specific object

    Attributes:
        game: trashtosser.Game
            The game object of which this object is a child of, used to get important variables such as the screen

        pos: Vector2
            Top left corner position vector

        rect: pygame.Rect
            The local rectangle representing the sprite

        global_rect: pygame.Rect
            Global rect offset by global coordinates used for collision and other inter-object interactions

    Methods:
        update(dt: float, keys: list)
            A function to process game logic taking deltatime and currently pressed down keys and arguments
            Has no effects on the base class but will be overridden in each game object

        draw()
            Draws the objects sprite to the screen, calculating rotations and position

    """
    def __init__(self, parent, x, y, image=None, angle=0):
        super(GameObject, self).__init__() # Initialise the parent object

        self.game = parent
        self.pos = Vector2(x,y)

        self.angle = angle

        self.image = image or pygame.Surface((0, 0))
        self.rect = self.image.get_rect()

        self.global_rect = pygame.Rect(self.rect.x+x,self.rect.y+y,self.rect.w,self.rect.h) # Add the objects position to its local rect

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
        if self.angle == 0: # Skip rotation calculations if there is no rotation
            pos = (self.pos.x,self.pos.y)
            image = self.image
        else:
            width,height = self.image.get_size()

            # Calculating and rotating the bounding boxes for the new sprite
            boundary = [
                Vector2(0,0),
                Vector2(width,0),
                Vector2(width,-height),
                Vector2(0,-height)
            ]
            boundary = [vector.rotate(self.angle) for vector in boundary]

            min_x = min(boundary, key=lambda vec: vec.x)[0] # Getting the lowest x value of each vector in the bounding box using an anonymous function as the key
            max_y = max(boundary, key=lambda vec: vec.y)[1] # Same thing but finding the max y value

            center = Vector2(
                (width/2),
                -(height/2)
            )

            rotation_offset = center.rotate(self.angle) - center

            pos = (
                self.pos.x + min_x - rotation_offset.x,
                self.pos.y + max_y - rotation_offset.y
            )

            # Rotating the image before blitting it to the screen below
            image = pygame.transform.rotate(self.image, self.angle)

        # Reassigning rect and global_rect with new positions
        self.rect = image.get_rect()

        self.global_rect = pygame.Rect(
            pos[0], pos[1],
            self.rect.w, self.rect.h
        )
        # Rendering to screen the newly calculated image and position
        self.game.surface.blit(image, pos)

class TrashObject(GameObject):
    """
    Object representing a piece of trash and inheriting the GameObject class

    Attributes:
        pos: Vector2
            The position vector of the objects top left corner relative to the origin

        vel: Vector2
            A relative vector representing the velocity. Coordinates are relative to TrashObject.pos as they are added each frame

        initial_length: int
            The initial magnitude of the velocity vector, used to calculate the scaling of the power used to launch the object

        TRAJECTORY_BALLS: int
            A constant value representing the amount of trajectory prediction orbs are to be calculated and drawn

        trajectory: list[Vector2], old_trajectory: list[Vector2]
            Lists of position vectors representing the predicted trajectory of the object
            The trajectory for the last launch is also stored and shown in a lighter colour so the player can compare them

        collider: pygame.Rect
            A pygame rectangle effectively equal to the global rect plus the objects velocity. Used to calculate collisions with obstacles

        Methods:
            draw()
                Overrides the GameObject draw function as this trash object also requires the trajectories to be drawn.
                Calls super().draw() at the end of the function so the sprite is still drawn as normal

            update(dt: float, keys: list)
                Overrides the GameObject update function with logic to calculate position, velocity, gravity, and aiming

            flipy()
                Flip the velocity vertically. Used in collision and bouncing calculations
                Also lower the velocity by a factor of 1/3 as objects lose speed when they bounce
    """
    def __init__(self, parent, x, y, vx, vy, type):
        super().__init__(parent, x, y, sprites.trash(type))

        self.type = type

        # Position and velocity vectors
        self.pos = Vector2(x,y)
        self.vel = Vector2(vx,vy)

        self.paused = True

        self.initial_length = self.vel.magnitude()

        # Scalar for the object so the launch power can be changed
        self.power = 1

        self.TRAJECTORY_BALLS = 15 # Amount of trajectory preciction orbs to display

        self.trajectory = []
        self.old_trajectory = []

        self.collider = pygame.Rect(self.global_rect.x + self.vel.x,
                                    self.global_rect.y + self.vel.y,
                                    self.global_rect.w,
                                    self.global_rect.h) # Collision rect made by adding the velocity to the global rect

    def draw(self):
        for dot in self.old_trajectory:
            pygame.draw.circle(self.game.surface,(128,128,255), dot[0], dot[1])
        if self.paused:
            for dot in self.trajectory:
                pygame.draw.circle(self.game.surface,(255,255,255),dot[0],dot[1])

        super().draw() # Calling parent draw to draw sprite

    def update(self, dt, keys):

        # Set the velocity to zero if the object is outside the game frame so the game can reset quicker
        if 0 > self.pos.x or self.pos.x > SIZE_X:
            self.vel = Vector2(0,0)


        # Calculate the trajectory indicators
        if self.paused:
            self.trajectory = []
            for i in range(self.TRAJECTORY_BALLS):
                # Some long calculations for finding the predicted location for each of the trajectory orbs
                # Involves adding the number of the ball multiplied by the velocity plus the gravity to the position of the ball
                # The size of the orb is also calculated using the number of the ball (5-i/4)
                self.trajectory.append((self.pos+i*Vector2(self.vel.x,self.vel.y+0.5*GRAVITY*i)+Vector2(self.global_rect.w/2,self.global_rect.h/2), 5-i/4))

        # Only calculate if the object is moving and not paused
        if not self.paused and self.vel != Vector2(0,0):
            self.angle -= 1 if self.vel.x > 0 else -1
            # Apply velocity
            self.pos += Vector2(self.vel.x,self.vel.y) * dt
            # Apply gravity
            self.vel.y += GRAVITY * dt

            # If the object is off screen
            if self.pos.y >= (SIZE_Y-self.rect.h) - (self.vel.y * dt):
                # If the object is going very slow then don't flip it and set the velocity to 0 instead so it doesn't jitter up and down
                if abs(self.vel.x) < 5 and abs(self.vel.y) < 5 and self.pos.y > (SIZE_Y-100):
                    self.vel = Vector2(0, 0)
                    self.pos.y = SIZE_Y-self.rect.h
                # Otherwise, flip the y velocity and times the velocity by 2/3 of it's current
                else:
                    self.flipy()

        # Make the modifier lower if shift is held down so the aiming can be more fine-tuned
        if keys[pygame.K_LSHIFT]:
            mod = 0.3
        else:
            mod = 1

        if self.paused:
            # Rotate with left and right arrows and restricting rotation to 180 degrees to the right
            # Rotating using deltatime so the rotation is framerate independent
            if keys[pygame.K_LEFT]:
                if self.vel.angle_to(CHECK_VECTOR) < 90:
                    self.vel.rotate_ip(-mod * dt)
            if keys[pygame.K_RIGHT]:
                if self.vel.angle_to(CHECK_VECTOR) > -90:
                    self.vel.rotate_ip(mod * dt)

            # Change power with up and down by scaling the velocity magnitude by the initial length times the scalar
            if keys[pygame.K_UP]:
                if self.power < 3:
                    self.power += mod * 0.02 * dt
                    self.vel.scale_to_length(self.initial_length * self.power)
            if keys[pygame.K_DOWN]:
                if self.power > 0.5:
                    self.power -= mod * 0.02 * dt
                    self.vel.scale_to_length(self.initial_length * self.power)

        # Recalculate the collider rect each update
        self.collider = pygame.Rect(self.pos.x + self.vel.x,
                                    self.pos.y + self.vel.y,
                                    self.global_rect.w,
                                    self.global_rect.h)
    def reset(self):
        # Reset all attributes of the object and generate a new type
        self.pos = Vector2(20, 400)
        self.vel = Vector2(10, -10)
        self.paused = True
        self.power = 1
        self.angle = 0
        self.type = random.randint(0,2)
        self.image = sprites.trash(self.type)

    # Only flip if the object is moving
    def flipy(self):
        if self.vel != Vector2(0,0):
            self.vel.y *= -1
            self.vel.y *= 0.8
            self.vel.x *= 0.66

class Bin(GameObject):
    """
    Object representing a rubbish bin, the goal for the player to shoot the trash object into

    Attributes:
        pos: Vector2
            Position vector of the top left corner relative to the origin

        type: int
            Used to represent what type of bin this object is.
            0 represents a landfill bin, 1 represents a recycling bin and 2 represents and organic bin.
            This dictates what objects can and can't be thrown into the bin
            !!! WARNING: This might not be implemented in time

    Methods:
        check_collision(trash: TrashObject)
            Checks the collision of the bin and the trash object. If the trash hits the main body then it bounces, if it hits the goal then a point is scored.

    """
    def __init__(self, parent, x, bin_type: int):
        super().__init__(parent, x, SIZE_Y-sprites.BASE_BIN_SIZE,sprites.bin(bin_type))
        self.pos = Vector2(x,SIZE_Y-sprites.BASE_BIN_SIZE)

        self.type = bin_type

    def check_collision(self, trash: TrashObject):
        collider = pygame.Rect(self.global_rect.x+10,self.global_rect.y+10,self.global_rect.w-20,self.global_rect.h-20)

        if collider.colliderect(trash.collider):
            if self.type == trash.type:
                return 1
            else:
                return 2

class Game:
    def __init__(self):
        self.running = False
        self.surface = pygame.display.set_mode((SIZE_X,SIZE_Y)) # The window for all objects to be drawn to

        # Window title and icon
        pygame.display.set_caption("Trash Tosser")
        pygame.display.set_icon(sprites.icon)

        # Clock used to regular framerate
        self.clock = pygame.time.Clock()

        self.trash = TrashObject(self, 20,400,10,-10, random.randint(0,2))
        self.obstacles = []

        self.score = 0
        self.lives = 3

        # Used to wait a second after the ball stops before restarting
        self.ball_stopped = False
        self.ball_stopped_at = 0

        # Will be overwritten in the game loop
        self.wrong_bin = (False, False)

        self.state = 0
        # 0 = Playing
        # 1 = Game over

        self.last_frame = time.time() # The time of the previous frame, used to calculate deltatime


    def run_until_finished(self):
        self.running = True
        # Initialise stage
        self.reset()
        while self.running:
            # Calculate the time since last frame and setting the last frame to now
            current_frame = time.time()
            dt = (current_frame-self.last_frame) * FRAMECAP
            self.last_frame = current_frame

            # Handle keypresses and get currently pressed down keys
            keys = self.handle_events(pygame.event.get())

            # Only calculate game logic if game is running (e.g. not in menu)
            if self.state == 0:
                scored = False

                # Check the trash objects collision with each bin. Lose a life if the bin type is incorrect and gain a point if it is correct
                for obstacle in self.obstacles:
                    result = obstacle.check_collision(self.trash)
                    # Represents a point scored and 2 represents a life lost
                    if result == 1:
                        self.score += 1
                        scored = True # Make it so you can't lose a life if you scored already
                        self.reset()
                    elif result == 2 and not scored:
                        if self.lives != 0:
                            self.reset()
                        self.lives -= 1
                        # Display the wrong bin message for three seconds only
                        self.wrong_bin = (True, time.time())

                # If the ball isn't moving, wait 1 second before resetting and losing a life
                if self.trash.vel == Vector2(0,0):
                    if not self.ball_stopped:
                        self.ball_stopped_at = time.time()
                        self.ball_stopped = True
                    if time.time() - self.ball_stopped_at > 1: # Wait 1 second
                        self.ball_stopped = False
                        self.lives -= 1
                        if self.lives != 0:
                            self.reset()

                self.trash.update(dt, keys)

                # Set state to gameover screen if no lives remain
                if self.lives <= 0:
                    self.state = 1

                # Fill background in blue before rendering life and score information
                self.surface.fill((0, 0, 128))

                score_text = font(36).render(f"Score: {self.score}", True,(255,255,255))
                self.surface.blit(score_text, (SIZE_X-200,50))

                lives_text = font(36).render(f"Lives: {self.lives}", True, (255,255,255))
                self.surface.blit(lives_text, (50, 50))

                # Check the wrong bin message is being displayed. If it is and it has been 3 seconds since it was shown, stop showing it
                if self.wrong_bin[0]:
                    if time.time() - self.wrong_bin[1] > 3:
                        self.wrong_bin = (False, False)
                    else:
                        wrong_bin_text = font(36).render("Wrong Bin!", True, (255,255,255))
                        self.surface.blit(wrong_bin_text,(300,50))

                for obstacle in self.obstacles:
                    obstacle.draw()

                self.trash.draw()

            # Draw game over screen if state = 1
            elif self.state == 1:
                self.surface.fill((0, 0, 128))

                score_text = font(36).render(f"Score: {self.score}", True,(255,255,255))
                self.surface.blit(score_text, (SIZE_X-200,50))

                gameover_text = font(72).render("GAME OVER", True, (255,255,255))
                self.surface.blit(gameover_text, gameover_text.get_rect(center=(SIZE_X/2,SIZE_Y/2)))

                restart_text = font(36).render("Press R to restart", True, (255,255,255))
                self.surface.blit(restart_text,restart_text.get_rect(center=(SIZE_X/2,SIZE_Y/2+100)))

            # Update display and cap the framerate
            pygame.display.update()
            self.clock.tick(FRAMECAP)

    def handle_events(self, events):
        """
        :param events: list:
        List of pygame events such as keyups, keydowns

        :return keys: list:
        List of currently pressed down keys

        Handles all pygame events, such as quitting the game, restarting the game if on the game over screen, etc..
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.running=False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.trash.paused = False
                    self.trash.old_trajectory = self.trash.trajectory
                if event.key == pygame.K_r and self.state == 1:
                    self.reset()
                    self.state = 0
                    self.score = 0
                    self.lives = 3

        return pygame.key.get_pressed()

    def gen_bins(self):
        """Generates bin objects and continually regenerates them until none of them are overlapping"""
        obstacles = []

        # One bin for each type
        for type in range(3):
            collided = False
            new_bin = Bin(self, random.randint(400,SIZE_X-sprites.BASE_BIN_SIZE*2), type)

            # Check collision with each other existing bin
            for bin in obstacles:
                if bin.global_rect.colliderect(new_bin.global_rect):
                    collided = True

            # Keep regenerating and checking until it doesnt overlap any other bin
            while collided:
                new_bin = Bin(self, random.randint(400, SIZE_X - sprites.BASE_BIN_SIZE * 2), type)
                collided = False
                for bin in obstacles:
                    if bin.global_rect.colliderect(new_bin.global_rect):
                        collided = True
            obstacles.append(new_bin)
        self.obstacles = obstacles

    def reset(self):
        self.trash.reset()
        self.gen_bins()


# Only start game if file is directly run rather than imported.
if __name__ == "__main__":
    game = Game()
    game.run_until_finished()
    pygame.quit()