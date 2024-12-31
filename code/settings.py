import pygame
from os.path import join 
from os import walk
pygame.init()

DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT = 1280,720

COLORS = {
    'table_1': '#007639',
    'table_2': '#2F0C28',
    'table_3': '#0e1665',
    'table_4': '#330413',
    'table_5': '#000000',
    'black': '#000000',
    'red': '#ee1a0f',
    'gray': 'gray',
    'white': '#ffffff',
    'dark_gray': '#001400',
    'green': 'green',
    'gold':'#Ffd700'
}

FONT_FILE = join('fonts','dmserif.ttf')