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
ZZT_DATA = {
    "width": 60,
    "height": 25
}
CHARACTERS = {
    "EMPTY": 32, "EDGE": 32, "MESSENGER": 32, "MONITOR": 32, "PLAYER": 2, "AMMO": 132, "TORCH": 157,
    "GEM": 4, "KEY": 12, "DOOR": 10, "SCROLL": 232, "PASSAGE": 240, "DUPLICATOR": 250, "BOMB": 11,
    "ENERGIZER": 127, "STAR": 47, "CLOCKWISE": 47, "COUNTER": 47, "BULLET": 248, "WATER": 176,
    "FOREST": 176, "SOLID": 219, "NORMAL": 178, "BREAKABLE": 177, "BOULDER": 254, "SLIDERNS": 18,
    "SLIDEREW": 29, "FAKE": 178, "INVISIBLE": 32, "BLINKWALL": 206, "TRANSPORTER": 94, "LINE": 206,
    "RICOCHET": 42, "HORIZRAY": 205, "BEAR": 153, "RUFFIAN": 5, "OBJECT": 2, "SLIME": 42, "SHARK": 94,
    "SPINNINGGUN": 24, "PUSHER": 31, "LION": 234, "TIGER": 227, "VERTRAY": 186, "HEAD": 233,
    "SEGMENT": 79, "UNUSED": 32
}
FG_GRAPHICS = (Image.open(BASE_DIR + "gfx/black.png"), Image.open(BASE_DIR + "gfx/darkblue.png"),
               Image.open(BASE_DIR + "gfx/darkgreen.png"), Image.open(BASE_DIR + "gfx/darkcyan.png"),
               Image.open(BASE_DIR + "gfx/darkred.png"), Image.open(BASE_DIR + "gfx/darkpurple.png"),
               Image.open(BASE_DIR + "gfx/darkyellow.png"), Image.open(BASE_DIR + "gfx/gray.png"),
               Image.open(BASE_DIR + "gfx/darkgray.png"), Image.open(BASE_DIR + "gfx/blue.png"),
               Image.open(BASE_DIR + "gfx/green.png"), Image.open(BASE_DIR + "gfx/cyan.png"),
               Image.open(BASE_DIR + "gfx/red.png"), Image.open(BASE_DIR + "gfx/purple.png"),
               Image.open(BASE_DIR + "gfx/yellow.png"), Image.open(BASE_DIR + "gfx/white.png"))
LINE_CHARACTERS = {"----": 249, "---W": 181, "--E-": 198, "--EW": 205, "-S--": 210, "-S-W": 187, "-SE-": 201,
                   "-SEW": 203, "N---": 208, "N--W": 188, "N-E-": 200, "N-EW": 202, "NS--": 186, "NS-W": 185,
                   "NSE-": 204, "NSEW": 206}


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


def get_elements_dict(data):
    return {
        "EMPTY": 0x00, "EDGE": 0x01, "MESSENGER": 0x02, "MONITOR": 0x03, "PLAYER": 0x04, "AMMO": 0x05, "TORCH": 0x06,
        "GEM": 0x07, "KEY": 0x08, "DOOR": 0x09, "SCROLL": 0x0A, "PASSAGE": 0x0B, "DUPLICATOR": 0x0C, "BOMB": 0x0D,
        "ENERGIZER": 0x0E, "STAR": 0x0F, "CLOCKWISE": 0x10, "COUNTER": 0x11, "BULLET": 0x12, "WATER": 0x13,
        "FOREST": 0x14, "SOLID": 0x15, "NORMAL": 0x16, "BREAKABLE": 0x17, "BOULDER": 0x18, "SLIDERNS": 0x19,
        "SLIDEREW": 0x1A, "FAKE": 0x1B, "INVISIBLE": 0x1C, "BLINKWALL": 0x1D, "TRANSPORTER": 0x1E, "LINE": 0x1F,
        "RICOCHET": 0x20, "HORIZRAY": 0x21, "BEAR": 0x22, "RUFFIAN": 0x23, "OBJECT": 0x24, "SLIME": 0x25, "SHARK": 0x26,
        "SPINNINGGUN": 0x27, "PUSHER": 0x28, "LION": 0x29, "TIGER": 0x2A, "VERTRAY": 0x2B, "HEAD": 0x2C,
        "SEGMENT": 0x2D, "UNUSED": 0x2E, "TEXTSTART": 0x2F, "WHITETEXT": 0x35, "TEXTEND": 0x45
    }


def get_tile(char, fg_color, bg_color, opaque):
    ch_x = char % 0x10
    ch_y = int(char / 0x10)
    tile_bg = Image.new("RGBA", (8, 14), color="#" + BG_COLORS[bg_color % 0x8])
    tile_fg = FG_GRAPHICS[fg_color].crop((ch_x * 8, ch_y * 14, ch_x * 8 + 8, ch_y * 14 + 14))

    result = Image.alpha_composite(tile_bg, tile_fg)

    if not opaque:
        result = Image.blend(tile_bg, result, 0.7)

    return result


def get_stats(x, y, stat_data):
    return next((stat for stat in stat_data if x == stat["x"] - 1 and y == stat["y"] - 1), None)


def get_element_character(elements, element):
    return CHARACTERS[next((key for key, value in elements.iteritems() if value == element), None)]


def parse(file_name):
    boards = []

    try:
        world_file = open_binary(file_name)

        read2(world_file)  # ZZT Bytes - Not needed
        engine_data = ZZT_DATA

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
            while parsed_tiles < engine_data["height"]*engine_data["width"]:
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

    engine_data = ZZT_DATA
    elements = get_elements_dict(engine_data)

    tile_dispenser = (tile for tile in tiles)
    for y in xrange(0, engine_data["height"]):
        for x in xrange(0, engine_data["width"]):
            tile = tile_dispenser.next()
            element = tile["element"]
            color = tile["color"]

            fg_color = color % 0x10
            bg_color = int(color / 0x10)

            char = None
            if element == elements["EMPTY"]:
                char = get_tile(color, 0x0, 0x0, True)
            elif element == elements["PLAYER"] and render_num == 0 \
                    and stat_data[0]["x"] - 1 == x and stat_data[0]["y"] - 1 == y:
                # On the title screen, replace the true player with a monitor
                char = get_tile(32, 0x0, 0x0, True)
            elif element == elements["DUPLICATOR"]:  # Duplicator
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
                    char = get_tile(duplicator_char, fg_color, bg_color, True)
            elif element == elements["BOMB"]:
                stat = get_stats(x, y, stat_data)
                if stat is not None and 2 <= stat["param1"] <= 9:  # Countdown
                    char = get_tile(stat["param1"] + 48, fg_color, bg_color, True)
            elif element == elements["INVISIBLE"] and INVISIBLE_MODE != 0:  # Invisible wall
                if INVISIBLE_MODE == 1:
                    char = get_tile(176, fg_color, bg_color, False)
                else:
                    char = get_tile(178, fg_color, bg_color, False)
            elif element == elements["TRANSPORTER"]:
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
                    char = get_tile(transporter_char, fg_color, bg_color, True)
            elif element == elements["LINE"]:
                line_key = ""

                # Is a line or board edge to the north?
                line_key += ("N" if y == 0 or tiles[(y - 1) * 60 + x]["element"] == 31 else "-")

                # Is a line or board edge to the south?
                line_key += ("S" if y == 24 or tiles[(y + 1) * 60 + x]["element"] == 31 else "-")

                # Is a line or board edge to the east?
                line_key += ("E" if x == 59 or tiles[y * 60 + (x + 1)]["element"] == 31 else "-")

                # Is a line or board edge to the west?
                line_key += ("W" if x == 0 or tiles[y * 60 + (x - 1)]["element"] == 31 else "-")

                char = get_tile(LINE_CHARACTERS[line_key], fg_color, bg_color, True)
            elif element == elements["OBJECT"]:
                stat = get_stats(x, y, stat_data)
                if stat is not None:
                    char = get_tile(stat["param1"], fg_color, bg_color, True)
            elif element == elements["PUSHER"]:
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
                    char = get_tile(pusher_char, fg_color, bg_color, True)
            elif elements["TEXTSTART"] <= element <= elements["TEXTEND"]:  # (includes malformed text)
                if element == elements["WHITETEXT"]:
                    char = get_tile(color, 0xF, 0x0, True)
                else:
                    char = get_tile(color, 0xF, int(element - 0x2F + 1), True)
            elif element > elements["TEXTEND"]:  # Invalid
                char = get_tile(168, fg_color, bg_color, True)

            if char is None:
                char = get_tile(get_element_character(elements, element), fg_color, bg_color, True)

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
