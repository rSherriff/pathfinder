
import random
from threading import Timer
from typing import Tuple

import tcod.event
from actions.actions import DeleteEntity
from application_path import get_app_path
from playsound import playsound
from utils.direction import Direction

from entities.entity import Entity

Icons = (chr(9827), chr(9824), chr(214), chr(163), chr(231), chr(163), chr(402))

class MapIcon(Entity):
    def __init__(self, engine, section, x: int, y: int):
        super().__init__(engine, section, x, y, chr(0), (255,255,255), (0,0,0))
        self.char = Icons[random.randrange(0, len(Icons))]
        self.life = 15
        self.move()

    def update(self):
        pass

    def move(self):
        self.x -= 1
        self.life -= 1
        if self.life <= 0:
            DeleteEntity(self.engine, self.section, self).perform()
        else:
            t = Timer(0.75, self.move)
            t.daemon = True
            t.start()

        
