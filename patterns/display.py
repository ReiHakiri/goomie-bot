from typing import Optional
import patterns.game as game
from PIL import Image, ImageDraw

def draw_game(g: game.Patterns, first_player: Optional[bool], size: int, file_name: str) -> None:
    width = len(g.board[0])
    height = len(g.board)

    image = Image.new('RGBA', (width * size, height * size), 'white')

    image_drawer = ImageDraw.Draw(image)

    for j, row in enumerate(g.board):
        for i, e in enumerate(row):
            color = (255, 255, 255, 255)

            if e == True:
                color = (120, 170, 255, 255)

            elif e == False:
                color = (255, 160, 240, 255)

            image_drawer.rectangle((i * size, j * size, (i + 1) * size, (j + 1) * size), color, (50, 50, 50, 255), width = 1)

    if first_player is None:
        image.save(file_name)

        return

    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))

    overlay_drawer = ImageDraw.Draw(overlay)

    tiles = g.first_tiles
    color = (50, 70, 100, 150)

    if not first_player:
        tiles = g.second_tiles
        color = (170, 0, 140, 150)

    for tile in tiles:
        for j, i in game.get_subpatterns(g.board, tile):
            tile_width = len(tile[0])
            tile_height = len(tile)

            overlay_drawer.rectangle((i * size, j * size, (i + tile_width) * size, (j + tile_height) * size), outline = color, width = 8)

    image = Image.alpha_composite(image, overlay)

    image.save(file_name)