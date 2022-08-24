
import json
from enum import Enum, auto

import numpy as np
import tcod
from actions.actions import StartGame,EscapeAction
from image import Image
from tcod import Console
from sections.game_section import Difficulty
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
        if key == tcod.event.K_a:
            StartGame(self.engine, Difficulty.EASY).perform()
        elif key == tcod.event.K_e:
            StartGame(self.engine, Difficulty.MEDIUM).perform()
        elif key == tcod.event.K_i:
            StartGame(self.engine, Difficulty.HARD).perform()
        elif key == tcod.event.K_ESCAPE:
            EscapeAction(self.engine).perform()
