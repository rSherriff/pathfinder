
from threading import Timer
from typing import Tuple

import tcod.event
from application_path import get_app_path
from playsound import playsound
from utils.direction import Direction

from entities.entity import Entity


class Man(Entity):
    def __init__(self, engine, section, x: int, y: int):
        super().__init__(engine, section, x, y, chr(231), (255,255,255), (0,0,0))
        self.down()

    def update(self):
        pass

    def up(self):
        self.char = chr(234)
        t = Timer(0.75, self.down)
        t.daemon = True
        t.start()

    def down(self):
        self.char = chr(231)
        t = Timer(0.75, self.up)
        t.daemon = True
        t.start()
        
