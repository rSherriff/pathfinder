import json
from threading import Timer

from pygame import mixer

from engine import Engine, GameState
from sections.intro_section import IntroSection
from sections.confirmation import Confirmation

class Game(Engine):
    def __init__(self, teminal_width: int, terminal_height: int):
        super().__init__(teminal_width, terminal_height)

    def create_new_save_data(self):
        pass

    def load_initial_data(self, data):
        pass

    def load_fonts(self):
        pass

    def setup_sections(self):
        self.intro_sections = {}
        self.intro_sections["introSection"] = IntroSection(self,0,0,self.screen_width, self.screen_height)

        self.menu_sections = {}

        self.game_sections = {}
        self.game_sections["confirmationDialog"] = Confirmation(self, 7, 9, 36, 10)


        self.disabled_sections = ["confirmationDialog"]