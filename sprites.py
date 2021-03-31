import os
import pygame


RES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "res")
BASE_PLAYER_SIZE = 64
BASE_BIN_SIZE = 128

icon = pygame.transform.scale(
    pygame.image.load(
        os.path.join(RES_DIR,"img","icon.png")
    ), (64,64)
)

# Helper function
def bin(type: int):
    if type == 0:
        return bin_plastic
    elif type == 1:
        return bin_recycling
    elif type == 2:
        return bin_organic
    else:
        return pygame.Surface((0,0))


bin_plastic = pygame.transform.scale(pygame.image.load(
        os.path.join(RES_DIR,"img","plasticbin.png")
    ), (BASE_BIN_SIZE,BASE_BIN_SIZE))

bin_recycling = pygame.transform.scale(pygame.image.load(
        os.path.join(RES_DIR,"img","recyclingbin.png")
    ), (BASE_BIN_SIZE,BASE_BIN_SIZE))

bin_organic = pygame.transform.scale(pygame.image.load(
        os.path.join(RES_DIR,"img","organicbin.png")
    ), (BASE_BIN_SIZE,BASE_BIN_SIZE))

# Helper function
def trash(type: int):
    if type == 0:
        return chips
    elif type == 1:
        return paper
    elif type == 2:
        return apple
    else:
        return pygame.Surface((0,0))

apple = pygame.transform.scale(pygame.image.load(
    os.path.join(RES_DIR, "img", "apple.png")
), (BASE_PLAYER_SIZE, BASE_PLAYER_SIZE))

paper = pygame.transform.scale(pygame.image.load(
    os.path.join(RES_DIR, "img", "paperball.png")
), (BASE_PLAYER_SIZE, BASE_PLAYER_SIZE))

chips = pygame.transform.scale(pygame.image.load(
    os.path.join(RES_DIR, "img", "chipbag.png")
), (BASE_PLAYER_SIZE, BASE_PLAYER_SIZE))


