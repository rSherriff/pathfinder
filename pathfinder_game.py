import json
from collections import OrderedDict
from threading import Timer

from pygame import mixer

from engine import Engine, GameState
from sections.intro_section import IntroSection
from sections.menu_section import MenuSection
from sections.game_section import GameSection


class PathfinderGame(Engine):
    def __init__(self, teminal_width: int, terminal_height: int):
        super().__init__(teminal_width, terminal_height)

    def setup_sections(self):
        self.intro_sections = OrderedDict()
        self.intro_sections["introSection"] = IntroSection(self,0,0,self.screen_width, self.screen_height)

        self.menu_sections = OrderedDict()
        self.menu_sections["menu"] = MenuSection(self,0,0,self.screen_width, self.screen_height, "menu.xp")

        self.game_sections = OrderedDict()
        self.game_sections["gameSection"] = GameSection(self, 0,0,self.screen_width, self.screen_height, "game.xp")
        
        self.disabled_sections = []


    def create_new_save_data(self):
        super().create_new_save_data()

    def load_initial_data(self, data):
        pass

    def load_fonts(self):
        self.font_manager.add_font("number_font")

    def start_game(self):
        self.change_state(GameState.IN_GAME)


