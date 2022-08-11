from actions.actions import StartGame
from ui.ui import UI, Button


class MenuUI(UI):
    def __init__(self, section):
        super().__init__(section)

        tiles = section.tiles["graphic"][12:19,14:18]
        self.start_button = Button(12,14,7,4, click_action=StartGame(self.section.engine), tiles=tiles, normal_bg=(191,191,191), highlight_bg=(128,128,128))
        self.elements.append(self.start_button)        