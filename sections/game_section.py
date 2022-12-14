
import json
import random
from enum import Enum, auto
from sre_parse import State
from threading import Timer
from tkinter import RIGHT

import numpy as np
import tcod
from actions.actions import (EscapeAction, IntroEndAction, PlayMenuMusicAction,
                             PlayMusicFileAction)
from entities.man import Man
from entities.map_icon import MapIcon
from fonts.font_manager import FontManager
from image import Image
from pygame import mixer
from tcod import Console

from sections.section import Section


class LevelState(Enum):
    COUNTDOWN = auto()
    IN_GAME = auto()
    WIN = auto()
    LOSE = auto()

class Directions(Enum):
    UP = auto()
    LEFT = auto()
    RIGHT = auto()
    DOWN = auto()

class Difficulty(Enum):
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()

LevelData = {
	"countdown_number_position": {
		"x": 19,
		"y": 9
	},
	"countdown_start": 3,
	"countdown_number_length": 2,
    "play_area_width" : 16,
    "segment_time": 4.0,
    "timer_position": {
		"x": 14,
		"y": 19
	},
    "directions_start_position": {
		"x": 12,
		"y": 4
	},
    "directions":
    [
        {"segment":"→", "answer":tcod.event.K_f},
        {"segment":"↓", "answer":tcod.event.K_j},
        {"segment":"→", "answer":tcod.event.K_k},
        {"segment":"←", "answer":tcod.event.K_j},
        {"segment":"←", "answer":tcod.event.K_i},
        {"segment":"↑↑", "answer":tcod.event.K_a},
        {"segment":"→→", "answer":tcod.event.K_c},
        {"segment":"↓↓", "answer":tcod.event.K_k},
        {"segment":"→↑", "answer":tcod.event.K_h},
        {"segment":"←←", "answer":tcod.event.K_f},
        {"segment":"→↑", "answer":tcod.event.K_c},
        {"segment":"↓←", "answer":tcod.event.K_f},
        {"segment":"↑→→", "answer":tcod.event.K_d},
        {"segment":"↓↓←", "answer":tcod.event.K_k},
        {"segment":"↑↑↓", "answer":tcod.event.K_g},
        {"segment":"←↓←", "answer":tcod.event.K_i},
        {"segment":"↑→↑", "answer":tcod.event.K_b},
        {"segment":"↓→←", "answer":tcod.event.K_f},
        {"segment":"→→↑", "answer":tcod.event.K_d},
        {"segment":"↓←←↑", "answer":tcod.event.K_b},
        {"segment":"↓↓→↑", "answer":tcod.event.K_g},
        {"segment":"→↓↑↑", "answer":tcod.event.K_d},
        {"segment":"←←↓←", "answer":tcod.event.K_e},
        {"segment":"↓→←→", "answer":tcod.event.K_j},
        {"segment":"↑↑↓→", "answer":tcod.event.K_g},
        {"segment":"→↓←←", "answer":tcod.event.K_j},
        {"segment":"↑↑→↓↓", "answer":tcod.event.K_k},
        {"segment":"↑↑↓→↓", "answer":tcod.event.K_l},
        {"segment":"←←↑←↑", "answer":tcod.event.K_a},
        {"segment":"→↓↑↓→", "answer":tcod.event.K_g},
        {"segment":"↑↓↓←→", "answer":tcod.event.K_k},
        {"segment":"↑→↑←↓", "answer":tcod.event.K_g},
        {"segment":"←←↑→↓↓", "answer":tcod.event.K_j},
        {"segment":"→↑↓←→←", "answer":tcod.event.K_j},
        {"segment":"←↑→→←→", "answer":tcod.event.K_g},
        {"segment":"↑→↓↓←→", "answer":tcod.event.K_l},
        {"segment":"←←↑↑↓←↑", "answer":tcod.event.K_a},
        {"segment":"↓↑→↓↑→←", "answer":tcod.event.K_b},
        {"segment":"→←↓↓→←↑←", "answer":tcod.event.K_e},
        {"segment":"→→→↑↓←→←", "answer":tcod.event.K_g},
        {"segment":"↑→↓↓←←←→", "answer":tcod.event.K_j},   
    ],
    "board":
    [
        [tcod.event.K_a,tcod.event.K_b,tcod.event.K_c,tcod.event.K_d],
        [tcod.event.K_e,tcod.event.K_f,tcod.event.K_g,tcod.event.K_h],
        [tcod.event.K_i,tcod.event.K_j,tcod.event.K_k,tcod.event.K_l],
    ]
}
#← ↑ ↓ →

class GameSection(Section):
    def __init__(self, engine, x: int, y: int, width: int, height: int, xp_filepath: str = "") -> None:
        super().__init__(engine, x, y, width, height, xp_filepath = "")

        self.lose_sound = self.validate_sound('Sounds/game_over.wav')
        self.beep_sound = self.validate_sound('Sounds/beep.wav')
        self.pos_sound = self.validate_sound('Sounds/positive.wav')
        self.neg_sound = self.validate_sound('Sounds/negative.wav')
        self.win_sound = self.validate_sound('Sounds/win.wav')

    def reset(self, difficulty):
        self.current_countdown_number = LevelData["countdown_start"]
        self.current_countdown_time = 0

        self.state = LevelState.COUNTDOWN
        self.beep_sound.play()
        self.font = self.engine.font_manager.get_font("number_font")

        self.directions_index = 0

        self.misc_tiles = Image(self.width, self.height, "images/utils.xp")

        self.win_tiles = self.load_xp_data("win.xp")
        self.lose_tiles = self.load_xp_data("lose.xp")
        self.countdown_tiles = self.load_xp_data("game_countdown.xp")
        self.game_easy_tiles = self.load_xp_data("game_easy.xp")
        self.game_medium_tiles = self.load_xp_data("game_medium.xp")
        self.game_hard_tiles = self.load_xp_data("game_hard.xp")

        self.difficulty = difficulty
        self.directions = self.generate_route()
        
        self.load_tiles("game", self.countdown_tiles) 

        self.current_segment_time = LevelData["segment_time"]
        self.recently_correct = False
        self.recently_wrong = False

        self.entities.clear()
        self.add_entity(Man(self.engine, self, 14,1))
        self.time_in_end_screen = 0

        


    def update(self):
        
        if self.state == LevelState.IN_GAME:
            self.current_segment_time -= self.engine.get_delta_time()

            if self.current_segment_time <= 0:
                self.state = LevelState.LOSE
                self.load_tiles("lose", self.lose_tiles)
                self.engine.full_screen_effect.start()
                self.lose_sound.play()
        elif self.state == LevelState.WIN or self.state == LevelState.LOSE:
            self.time_in_end_screen += self.engine.get_delta_time()

            if self.time_in_end_screen >= 10:
                self.engine.open_menu()
            

    def render(self, console):
        super().render(console, True)

        if self.state == LevelState.COUNTDOWN:
            temp_console = Console(width = self.font.char_width, height = self.font.char_height, order="F")
            temp_console.tiles_rgb[0: self.font.char_width, 0:self.font.char_height] = self.font.get_character(str(self.current_countdown_number))

            x = LevelData["countdown_number_position"]["x"] - int(self.font.char_width / 2)
            y = LevelData["countdown_number_position"]["y"] - int(self.font.char_height / 2)
            temp_console.blit(console, src_x=0, src_y=0, dest_x = x, dest_y = y, width = self.font.char_width, height = self.font.char_height)

            self.current_countdown_time += self.engine.get_delta_time()
            if self.current_countdown_time > LevelData["countdown_number_length"]:
                self.current_countdown_number -= 1
                self.current_countdown_time = 0
                self.beep_sound.play()
                
                if self.current_countdown_number <= 0:
                    self.state = LevelState.IN_GAME
                    if self.difficulty == Difficulty.EASY:
                        self.load_tiles("game", self.game_easy_tiles)
                    if self.difficulty == Difficulty.MEDIUM:
                        self.load_tiles("game", self.game_medium_tiles)
                    if self.difficulty == Difficulty.HARD:
                        self.load_tiles("game", self.game_hard_tiles)        
                    self.add_icon()
            
            #Render start button hint   
            temp_console = Console(width=10, height=3, order="F")
            temp_console.tiles_rgb[0:10,0:3] = self.misc_tiles.tiles[0:10,0:3]["graphic"]
            temp_console.blit(console, 14,16,0,0,10,3)


        elif self.state == LevelState.IN_GAME:
            directions_string = ''
            for i in range(0, self.directions_index):
                directions_string +=  self.directions[i]["segment"]
                
            x = LevelData["directions_start_position"]["x"]
            y = LevelData["directions_start_position"]["y"]
            console.print_box(x, y, width=16, height=10, string=directions_string, alignment=tcod.LEFT, fg = (255,255,255))

            current_segment_start_x = x + int(len(directions_string) % LevelData["play_area_width"])
            current_segment_start_y = y + int(len(directions_string) / LevelData["play_area_width"])

            final_segment =  self.directions[self.directions_index]["segment"]
        
            overlap= (current_segment_start_x + len(final_segment)) - (x +LevelData["play_area_width"])
            if overlap > 0:
                console.print_box(current_segment_start_x, current_segment_start_y, width=16, height=10, string=final_segment[:len(final_segment) - overlap], alignment=tcod.LEFT, fg = (0,0,255))
                console.print_box(x, current_segment_start_y + 1, width=16, height=10, string=final_segment[abs(overlap - len(final_segment)):], alignment=tcod.LEFT, fg = (0,0,255)) 
            else:
                console.print_box(current_segment_start_x, current_segment_start_y, width=16, height=10, string=final_segment, alignment=tcod.LEFT, fg = (0,0,255))

            for entity in self.entities:
                if not entity.invisible:
                    console.print(entity.x, entity.y,entity.char, fg=entity.fg_color, bg=entity.bg_color)


            #Timer drawing!
            timer_string = ''
            if self.current_segment_time > 0:
                timer_string = "%.2f" % self.current_segment_time
                timer_string = timer_string[0]  + ':' + timer_string[2:]
            else:
                timer_string == "00:00"
            temp_console = Console(width = self.font.char_width*len(timer_string), height = self.font.char_height, order="F")
            for i in range(0,len(timer_string)):
                temp_console.tiles_rgb[(i *  self.font.char_width):  (i *  self.font.char_width) + self.font.char_width, 0:self.font.char_height] = self.font.get_character(timer_string[i])

            if self.recently_correct or self.recently_wrong:
                fg_colour = (0,255,0) if self.recently_correct else (255,0,0)
                for w in range(0, temp_console.width):
                    for h in range(0, temp_console.height):
                        temp_console.tiles_rgb[w][h][1] = fg_colour

            x = LevelData["timer_position"]["x"]
            y = LevelData["timer_position"]["y"] - int(self.font.char_height / 2)
            temp_console.blit(console, src_x=0, src_y=0, dest_x = x, dest_y = y, width = self.font.char_width * len(timer_string), height = self.font.char_height)        

        elif self.state == LevelState.WIN:
            pass

        elif self.state == LevelState.LOSE:
            pass

    def keydown(self, key):
        if self.state == LevelState.IN_GAME:
            if key ==   self.directions[self.directions_index]["answer"]:
                self.directions_index +=1

                if self.directions_index >= len(self.directions):
                    self.state = LevelState.WIN
                    self.load_tiles("win", self.win_tiles)
                    self.engine.full_screen_effect.start()
                    self.win_sound.play()

                self.current_segment_time = LevelData["segment_time"]
                self.recently_correct = True
                self.pos_sound.play()
                Timer(0.2, self.reset_recently_correct).start()
            else:
                self.recently_wrong = True
                self.current_segment_time -= 0.1
                self.neg_sound.play()
                Timer(0.2, self.reset_recently_wrong).start()

        elif self.state == LevelState.LOSE or self.state == LevelState.WIN:
            if key == tcod.event.K_e:
                self.reset(self.difficulty)

        if key == tcod.event.K_ESCAPE:
            EscapeAction(self.engine).perform()

    def reset_recently_correct(self):
        self.recently_correct = False

    def reset_recently_wrong(self):
        self.recently_wrong = False

    def add_icon(self):
        if self.state == LevelState.IN_GAME:
            self.add_entity(MapIcon(self.engine, self, 27,1))
            t = Timer((random.random() * 3 ) + 3, self.add_icon)
            t.daemon = True
            t.start()

    def generate_route(self):
        directions = []

        x = 0
        y = 1

        difficulty_schema = []
        if self.difficulty == Difficulty.EASY:
            direction_schema = [4,5,5,5,5,4,2,2]
        if self.difficulty == Difficulty.MEDIUM:
            direction_schema = [5,5,7,6,6,4,2,2]
        if self.difficulty == Difficulty.HARD:
            direction_schema = [5,7,7,7,6,4,2,3]

        for i in range(0, len(direction_schema)):

            while(direction_schema[i] > 0):
                route_string = ""

                for _ in range(0,i+1):
                    possible_directions = []
                    if x == 0 and y == 0:
                        possible_directions.append(Directions.DOWN)
                        possible_directions.append(Directions.RIGHT)
                    elif x == 0 and y == 2:
                        possible_directions.append(Directions.UP)
                        possible_directions.append(Directions.RIGHT)
                    elif x == 3 and y == 0:
                        possible_directions.append(Directions.DOWN)
                        possible_directions.append(Directions.LEFT)
                    elif x == 3 and y == 2:
                        possible_directions.append(Directions.UP)
                        possible_directions.append(Directions.LEFT)
                    elif y == 0:
                        possible_directions.append(Directions.DOWN)
                        possible_directions.append(Directions.RIGHT)
                        possible_directions.append(Directions.LEFT)
                    elif y == 2:
                        possible_directions.append(Directions.UP)
                        possible_directions.append(Directions.RIGHT)
                        possible_directions.append(Directions.LEFT)
                    elif x == 0:
                        possible_directions.append(Directions.UP)
                        possible_directions.append(Directions.DOWN)
                        possible_directions.append(Directions.RIGHT)
                    elif x == 3:
                        possible_directions.append(Directions.UP)
                        possible_directions.append(Directions.DOWN)
                        possible_directions.append(Directions.LEFT)
                    else:
                        possible_directions.append(Directions.UP)
                        possible_directions.append(Directions.DOWN)
                        possible_directions.append(Directions.LEFT)
                        possible_directions.append(Directions.RIGHT)

                    chosen_direction = possible_directions[random.randrange(0, len(possible_directions))]
                    
                    if chosen_direction == Directions.UP:
                        route_string = route_string + "↑"
                        x = x
                        y = y - 1
                    elif chosen_direction == Directions.DOWN:
                        route_string = route_string + "↓"
                        x = x
                        y = y + 1
                    elif chosen_direction == Directions.LEFT:
                        route_string = route_string + "←"
                        x = x - 1
                        y = y
                    elif chosen_direction == Directions.RIGHT:
                        route_string = route_string + "→"
                        x = x + 1
                        y = y

                directions.append({"segment":route_string, "answer":LevelData["board"][y][x]})
                direction_schema[i] -= 1
        
        return directions




