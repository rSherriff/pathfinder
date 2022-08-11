#!/usr/bin/env python3
import tcod

from application_path import get_app_path
from pathfinder_game import PathfinderGame


def main() -> None:
    screen_width = 40
    screen_height = 23

    terminal_height = screen_height * 3
    terminal_width = screen_width * 3

    tileset = tcod.tileset.load_tilesheet(
        get_app_path() + "/fonts/polyducks_12x12.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )

    with tcod.context.new_terminal(
        terminal_width,
        terminal_height,
        tileset=tileset,
        title="Folk2D",
        vsync=True,
        sdl_window_flags=tcod.context.SDL_WINDOW_RESIZABLE
    ) as root_context:

        root_console = tcod.Console(screen_width, screen_height, order="F")
        engine = PathfinderGame(screen_width, screen_height)

        cycle = 0
        while True:
            root_console.clear()

            engine.event_handler.on_render(root_console=root_console)

            root_context.present(root_console)

            engine.handle_events(root_context)

            cycle += 1
            if cycle % 2 == 0:
                engine.update()


if __name__ == "__main__":
    main()
