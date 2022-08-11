
import json
from enum import Enum, auto

import numpy as np
import tcod
from actions.actions import StartGame,EscapeAction
from image import Image
from tcod import Console
import copy

from sections.section import Section


class MenuSection(Section):
    def __init__(self, engine, x: int, y: int, width: int, height: int, xp_filepath: str = "") -> None:
        super().__init__(engine, x, y, width, height, xp_filepath)

    def update(self):
        pass

    def render(self, console):
        super().render(console)

    def keydown(self, key):
        if key == tcod.event.K_e:
            StartGame(self.engine).perform()
        elif key == tcod.event.K_ESCAPE:
            EscapeAction(self.engine).perform()
