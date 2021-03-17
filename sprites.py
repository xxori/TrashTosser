import os
import pygame

RES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "res")

BASE_TILE_SIZE = 10
BASE_PLAYER_SIZE = 64

player = pygame.transform.scale(
    pygame.image.load(
        os.path.join(RES_DIR, "img", "PaperBall.png")
    ), (BASE_PLAYER_SIZE,BASE_PLAYER_SIZE)
)