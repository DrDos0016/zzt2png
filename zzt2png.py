# -*- coding: utf-8 -*-
import binascii
import os
import random
import sys

from PIL import Image

INVISIBLE_MODE = 1  # 0: render as an empty tile | 1: render in editor style | 2: render as touched

BASE_DIR = "C:\\Users\\Kevin\\Documents\\programming\\zzt2png\\"
BG_COLORS = ("000000", "0000A8", "00A800", "00A8A8", "A80000", "A800A8", "A85400", "A8A8A8",
             "545454", "5454FC", "54FC54", "54FCFC", "FC5454", "FC54FC", "FCFC54", "FCFCFC")
CHARACTERS = (32, 32, 63, 32, 2, 132, 157, 4, 12, 10, 232, 240, 250, 11, 127, 47, 47, 47, 248, 176, 176, 219, 178, 177,
              254, 18, 29, 178, 32, 206, 94, 249, 42, 205, 153, 5, 2, 42, 94, 24, 31, 234, 227, 186, 233, 79, 63, 63,
              63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63)
FG_GRAPHICS = (Image.open(BASE_DIR + "gfx/black.png"), Image.open(BASE_DIR + "gfx/darkblue.png"),
               Image.open(BASE_DIR + "gfx/darkgreen.png"), Image.open(BASE_DIR + "gfx/darkcyan.png"),
               Image.open(BASE_DIR + "gfx/darkred.png"), Image.open(BASE_DIR + "gfx/darkpurple.png"),
               Image.open(BASE_DIR + "gfx/darkyellow.png"), Image.open(BASE_DIR + "gfx/gray.png"),
               Image.open(BASE_DIR + "gfx/darkgray.png"), Image.open(BASE_DIR + "gfx/blue.png"),
               Image.open(BASE_DIR + "gfx/green.png"), Image.open(BASE_DIR + "gfx/cyan.png"),
               Image.open(BASE_DIR + "gfx/red.png"), Image.open(BASE_DIR + "gfx/purple.png"),
               Image.open(BASE_DIR + "gfx/yellow.png"), Image.open(BASE_DIR + "gfx/white.png"))
LINE_CHARACTERS = {"0000": 249, "0001": 181, "0010": 198, "0011": 205, "0100": 210, "0101": 187, "0110": 201,
                   "0111": 203, "1000": 208, "1001": 188, "1010": 200, "1011": 202, "1100": 186, "1101": 185,
                   "1110": 204, "1111": 206}


def open_binary(path):
    flags = os.O_RDONLY
    if hasattr(os, 'O_BINARY'):
        flags = flags | os.O_BINARY
    return os.open(path, flags)


def read(world_file):
    """Read one byte as an int"""

    temp = ord(os.read(world_file, 1))
    return temp


def read2(world_file):
    """Read 2 bytes and convert to an integer"""

    part1 = binascii.hexlify(str(os.read(world_file, 1)))
    part2 = binascii.hexlify(str(os.read(world_file, 1)))
    return int(part2 + part1, 16)


def sread(world_file, num):
    """Read a string of characters"""
    array = []
    temp = ""
    for x in xrange(0, num):
        array.append(binascii.hexlify(str(os.read(world_file, 1))))
    for x in xrange(0, num):
        temp += chr(int(array[x], 16))
    return temp


def get_tile(char, fg_color, bg_color=0x0):
    ch_x = char % 0x10
    ch_y = int(char / 0x10)
    tile = Image.new("RGBA", (8, 14), color="#" + BG_COLORS[bg_color % 0x8])
    temp = FG_GRAPHICS[fg_color].crop((ch_x * 8, ch_y * 14, ch_x * 8 + 8, ch_y * 14 + 14))

    tile = Image.alpha_composite(tile, temp)
    return tile


def get_stats(x, y, stat_data):
    return next((stat for stat in stat_data if stat["x"] - 1 == x and stat["y"] - 1 == y), None)


def parse(file_name):
    boards = []

    try:
        world_file = open_binary(file_name)

        read2(world_file)  # ZZT Bytes - Not needed
        board_count = read2(world_file)  # Boards in file (0 means just a title screen)
        board_offset = 512

        # Parse Board
        for idx in xrange(0, board_count + 1):
            os.lseek(world_file, board_offset, 0)  # Jump to board data
            board_size = read2(world_file)
            board_name_length = read(world_file)
            board_name = sread(world_file, 50)[:board_name_length]

            parsed_tiles = 0
            tiles = []
            while parsed_tiles < 1500:
                quantity = read(world_file)
                if quantity == 0:  # Just in case some weird WiL or Chronos30 world uses this
                    quantity = 256
                element_id = read(world_file)
                color = read(world_file)
                for tile_count in xrange(0, quantity):
                    tiles.append({"element": element_id, "color": color})
                    parsed_tiles += 1

            # Parse Stats
            os.lseek(world_file, 86, 1)  # Skip 86 bytes of board + message info that we don't care about
            stat_count = read2(world_file)
            stat_data = []
            parsed_stats = 0

            while parsed_stats <= stat_count:
                stat = {"x": read(world_file), "y": read(world_file), "x-step": read2(world_file),
                        "y-step": read2(world_file)}

                os.lseek(world_file, 2, 1)
                stat["param1"] = read(world_file)
                stat["param2"] = read(world_file)
                stat["param3"] = read(world_file)
                os.lseek(world_file, 12, 1)
                oop_length = read2(world_file)
                os.lseek(world_file, 8, 1)

                if oop_length > 32767:  # Pre-bound element
                    oop_length = 0

                if oop_length:
                    sread(world_file, oop_length)

                stat_data.append(stat)
                parsed_stats += 1

            # Boards don't get appended to the list until finished so incomplete boards aren't included
            boards.append({
                "name": board_name,
                "tiles": tiles,
                "stats": stat_data
            })
            board_offset += board_size + 2
    except (TypeError, ValueError, OSError, EOFError):
        pass  # I thought this would catch superlocked files, but maybe not??

    return boards


def render(tiles, stat_data, render_num):
    canvas = Image.new("RGBA", (480, 350))

    tile_dispenser = (tile for tile in tiles)
    for y in xrange(0, 25):
        for x in xrange(0, 60):
            tile = tile_dispenser.next()
            element = tile["element"]
            color = tile["color"]

            fg_color = color % 0x10
            bg_color = int(color / 0x10)

            char = None
            if element == 0x00:  # Empty
                char = get_tile(color, 0x0, 0x0)
            elif element == 0x04 and render_num == 0 and stat_data[0]["x"] - 1 == x and stat_data[0]["y"] - 1 == y:
                # On the title screen, replace the true player with a monitor
                char = get_tile(32, 0x0, 0x0)
            elif element == 0x0C:  # Duplicator
                stat = get_stats(x, y, stat_data)
                if stat is not None:
                    if stat["param1"] is 2:
                        duplicator_char = 249  # ∙
                    elif stat["param1"] is 3:
                        duplicator_char = 248  # °
                    elif stat["param1"] is 4:
                        duplicator_char = 111  # o
                    elif stat["param1"] is 5:
                        duplicator_char = 79  # O
                    else:  # Includes malformed param1
                        duplicator_char = 250  # ·
                    char = get_tile(duplicator_char, fg_color, bg_color)
            elif element == 0x0D:  # Bomb
                stat = get_stats(x, y, stat_data)
                if stat is not None and 2 <= stat["param1"] <= 9:  # Countdown
                    char = get_tile(stat["param1"]+48, fg_color, bg_color)
            elif element == 0x1C and INVISIBLE_MODE != 0:  # Invisible wall
                if INVISIBLE_MODE == 1:
                    char = get_tile(176, fg_color, bg_color)
                else:
                    char = get_tile(219, fg_color, bg_color)
            elif element == 0x1E:  # Transporter
                stat = get_stats(x, y, stat_data)
                if stat is not None:
                    if stat["x-step"] > 32767:
                        transporter_char = 60  # West
                    elif stat["x-step"] > 0:
                        transporter_char = 62  # East
                    elif stat["y-step"] <= 32767:
                        transporter_char = 118  # South
                    else:
                        transporter_char = 94  # North (or Idle)
                    char = get_tile(transporter_char, fg_color, bg_color)
            elif element == 0x1F:  # Line Wall
                line_key = ""

                # Is a line or board edge to the north?
                line_key += ("1" if y == 0 or tiles[(y - 1) * 60 + x]["element"] == 31 else "0")

                # Is a line or board edge to the south?
                line_key += ("1" if y == 24 or tiles[(y + 1) * 60 + x]["element"] == 31 else "0")

                # Is a line or board edge to the west?
                line_key += ("1" if x == 59 or tiles[y * 60 + (x + 1)]["element"] == 31 else "0")

                # Is a line or board edge to the east?
                line_key += ("1" if x == 0 or tiles[y * 60 + (x - 1)]["element"] == 31 else "0")

                char = get_tile(LINE_CHARACTERS[line_key], fg_color, bg_color)
            elif element == 0x24:  # Object
                stat = get_stats(x, y, stat_data)
                if stat is not None:
                    char = get_tile(stat["param1"], fg_color, bg_color)
            elif element == 0x28:  # Pusher
                stat = get_stats(x, y, stat_data)
                if stat is not None:
                    if stat["x-step"] == 65535:
                        pusher_char = 17  # West
                    elif stat["x-step"] == 1:
                        pusher_char = 16  # East
                    elif stat["y-step"] == 65535:
                        pusher_char = 30  # North
                    else:
                        pusher_char = 31  # South (or Idle)
                    char = get_tile(pusher_char, fg_color, bg_color)
            elif 0x2F <= element <= 0x45:  # Text (includes malformed text)
                if element != 0x35:
                    char = get_tile(color, 0xF, int(((element - 0x2F) * 0x10 + 0x0F) / 0x10))
                else:  # White text
                    char = get_tile(color, 0xF, 0x0)
            elif element > 0x45:  # Invalid
                char = get_tile(168, fg_color, bg_color)

            if char is None:
                char = get_tile(CHARACTERS[element], fg_color, bg_color)

            canvas.paste(char, (x * 8, y * 14))

    return canvas


def main():
    if len(sys.argv) == 1:
        print "Enter ZZT (or sav) file to process"
        file_name = raw_input("Choice: ")
        print "Enter board number to export."
        print " - Board numbers start at 0 (the title screen)"
        print " - Enter ? for a random board"
        print " - Enter A for all boards"
        render_num = raw_input("Choice: ")
        print "Enter filename for output"
        print " - Do not include the .png extension"
        print " - If exporting all boards, the files will be suffixed with a two-digit board number"
        output = raw_input("Choice: ")
    else:
        file_name = sys.argv[1]
        render_num = sys.argv[2]
        output = sys.argv[3]

    boards = parse(file_name)

    if render_num == "A":
        for idx in xrange(0, len(boards) - 1):
            canvas = render(boards[idx]["tiles"], boards[idx]["stats"], idx)
            canvas.save(output + "-" + ("0" + str(idx))[-2:] + ".png")
            print boards[idx]["name"]
    else:
        if render_num == "?":
            render_num = random.randint(0, len(boards) - 1)
        else:
            render_num = int(render_num)
        canvas = render(boards[render_num]["tiles"], boards[render_num]["stats"], render_num)
        canvas.save(output + ".png")
        print boards[render_num]["name"]


if __name__ == "__main__":
    main()
