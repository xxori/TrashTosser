import os
import pygame


RES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "res")

BASE_TILE_SIZE = 10
BASE_PLAYER_SIZE = 64
BASE_BIN_SIZE = 128

player = pygame.transform.scale(
    pygame.image.load(
        os.path.join(RES_DIR, "img", "PaperBall.png")
    ), (BASE_PLAYER_SIZE,BASE_PLAYER_SIZE)
)

icon = pygame.transform.scale(
    pygame.image.load(
        os.path.join(RES_DIR,"img","icon.png")
    ), (64,64)
)

bin = lambda type: pygame.transform.scale(
    pygame.image.load(
        os.path.join(RES_DIR,"img",type+"bin.png")
    ), (BASE_BIN_SIZE,BASE_BIN_SIZE)
)