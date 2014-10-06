import pygame
from pygame.locals import KEYDOWN

import base


class Screen(base.Screen):
    def __init__(self, height, width):
        super(Screen, self).__init__(height, width)

        pygame.init()
        self.clock = pygame.time.Clock()

        self.fg_color = pygame.Color('white')
        self.bg_color = pygame.Color('black')

        self.font = pygame.font.SysFont('monospace', 10)
        _width, self.fontheight = self.font.size(' ' * self.width)
        _height = height * self.fontheight

        self.pygame_screen = pygame.display.set_mode((_width, _height))

    def getch(self):
        while True:
            event = pygame.event.wait()
            if event.type == KEYDOWN:
                return event.key

    def refresh(self):
        self.pygame_screen.fill(self.bg_color)

        for y in range(self.height):
            s = ''.join(self.data[y])
            rendered = self.font.render(s, True, self.fg_color, self.bg_color)
            self.pygame_screen.blit(rendered, (0, y * self.fontheight))

        self.clock.tick()
        pygame.display.flip()

    def cleanup(self):
        pygame.quit()
