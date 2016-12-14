# -*- coding: utf-8 -*-
import binascii
import os
import random
import sys

from collections import OrderedDict
from PIL import Image

INVISIBLE_MODE = 1  # 0: render as an empty tile | 1: render in editor style | 2: render as touched

BASE_DIR = "C:\\Users\\Kevin\\Documents\\programming\\zzt2png\\"
MAX_SIGNED_INT = 0x7FFF

WHITE_TEXT_INDEX = 0x06
TEXT_LENGTH = 0x10

BG_COLORS = ("000000", "0000A8", "00A800", "00A8A8", "A80000", "A800A8", "A85400", "A8A8A8",
             "545454", "5454FC", "54FC54", "54FCFC", "FC5454", "FC54FC", "FCFC54", "FCFCFC")
ZZT_DATA = {
    "width": 60,
    "height": 25,
    "total_flags": 10,
    "board_start_location": 512,
    "board_name_size": 50,
    "board_property_padding": 16,
    "stat_padding": 8,
    "absent_elements": frozenset([]),
    "blank_elements": frozenset(["MESSENGER"])
}
ELEMENTS = OrderedDict([
    ("EMPTY", 32), ("EDGE", 32), ("MESSENGER", 2), ("MONITOR", 32), ("PLAYER", 2), ("AMMO", 132), ("TORCH", 157),
    ("GEM", 4), ("KEY", 12), ("DOOR", 10), ("SCROLL", 232), ("PASSAGE", 240), ("DUPLICATOR", 250), ("BOMB", 11),
    ("ENERGIZER", 127), ("STAR", 47), ("CLOCKWISE", 47), ("COUNTER", 47), ("BULLET", 248), ("WATER", 176),
    ("FOREST", 176), ("SOLID", 219), ("NORMAL", 178), ("BREAKABLE", 177), ("BOULDER", 254), ("SLIDERNS", 18),
    ("SLIDEREW", 29), ("FAKE", 178), ("INVISIBLE", 32), ("BLINKWALL", 206), ("TRANSPORTER", 94), ("LINE", 206),
    ("RICOCHET", 42), ("HORIZRAY", 205), ("BEAR", 153), ("RUFFIAN", 5), ("OBJECT", 2), ("SLIME", 42), ("SHARK", 94),
    ("SPINNINGGUN", 24), ("PUSHER", 31), ("LION", 234), ("TIGER", 227), ("VERTRAY", 186), ("HEAD", 233),
    ("SEGMENT", 79), ("UNUSED", 32), ("TEXTSTART", None)
])
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


def read1(world_file):
    """Read one byte as an int"""

    temp = ord(os.read(world_file, 1))
    return temp


def read2(world_file):
    """Read 2 bytes and convert to an integer"""

    part1 = binascii.hexlify(str(os.read(world_file, 1)))
    part2 = binascii.hexlify(str(os.read(world_file, 1)))
    return int(part2 + part1, 16)


def read4(world_file):
    """Read 4 bytes and convert to an integer"""

    part1 = binascii.hexlify(str(os.read(world_file, 1)))
    part2 = binascii.hexlify(str(os.read(world_file, 1)))
    part3 = binascii.hexlify(str(os.read(world_file, 1)))
    part4 = binascii.hexlify(str(os.read(world_file, 1)))
    return int(part4 + part3 + part2 + part1, 16)


def sread(world_file, num):
    """Read a string of characters"""
    array = []
    temp = ""
    for x in xrange(0, num):
        array.append(binascii.hexlify(str(os.read(world_file, 1))))
    for x in xrange(0, num):
        temp += chr(int(array[x], 16))
    return temp


def get_elements_dict(engine_data):
    result = {key: index for index, key in enumerate(
        filter(lambda element: element not in engine_data["absent_elements"], ELEMENTS.keys())
    )}
    result["WHITETEXT"] = result["TEXTSTART"] + WHITE_TEXT_INDEX
    result["TEXTEND"] = result["TEXTSTART"] + TEXT_LENGTH

    return result


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
    return ELEMENTS[next((key for key, value in elements.iteritems() if value == element), None)]


def parse_board(engine_data, world_file):
        board = {"tiles": [], "stats": []}

        board_name_length = read1(world_file)
        board["name"] = sread(world_file, engine_data["board_name_size"])[:board_name_length]

        parsed_tiles = 0
        while parsed_tiles < engine_data["height"]*engine_data["width"]:
            quantity = read1(world_file)
            if quantity == 0:  # Just in case some weird WiL or Chronos30 world uses this
                quantity = 256
            element_id = read1(world_file)
            color = read1(world_file)
            for tile_count in xrange(0, quantity):
                board["tiles"].append({"element": element_id, "color": color})
            parsed_tiles += quantity

        # Parse Stats
        board["max_player_shots"] = read1(world_file)
        board["is_dark"] = read1(world_file)
        board["exit_north"] = read1(world_file)
        board["exit_south"] = read1(world_file)
        board["exit_west"] = read1(world_file)
        board["exit_east"] = read1(world_file)
        board["restart_on_zap"] = read1(world_file)
        board["message_length"] = read1(world_file)
        board["message"] = sread(world_file, 58)[:board["message_length"]]
        board["player_enter_x"] = read1(world_file)
        board["player_enter_y"] = read1(world_file)
        board["time_limit"] = read2(world_file)
        os.lseek(world_file, engine_data["board_property_padding"], 1)  # Skip unused filler
        stat_count = read2(world_file)

        # byte missing in stats, I think

        parsed_stats = 0
        while parsed_stats <= stat_count:
            stat = {"x": read1(world_file), "y": read1(world_file),
                    "x-step": read2(world_file), "y-step": read2(world_file),

                    "cycle": read2(world_file),
                    "param1": read1(world_file), "param2": read1(world_file), "param3": read1(world_file),
                    "follower": read2(world_file), "leader": read2(world_file),
                    "under_element": read1(world_file), "under_color": read1(world_file),
                    "program_pointer": read4(world_file), "program_counter": read2(world_file)}

            oop_length = read2(world_file)
            os.lseek(world_file, engine_data["stat_padding"], 1)

            if oop_length > MAX_SIGNED_INT:  # Pre-bound element
                stat["program"] = oop_length - MAX_SIGNED_INT - 1
            elif oop_length:
                stat["program"] = sread(world_file, oop_length)

            board["stats"].append(stat)
            parsed_stats += 1

        return board


def parse_file(file_name):
    world = {"boards": [], "keys": [], "flags": []}

    try:
        world_file = open_binary(file_name)

        engine_identity = read2(world_file)  # What format is this file?
        world["board_count"] = read2(world_file)  # Boards in file (0 means just a title screen)
        world["ammo"] = read2(world_file)
        world["gems"] = read2(world_file)
        for count in xrange(0, 9):
            world["keys"].append(read1(world_file) != 0)
        world["health"] = read2(world_file)
        world["active_board"] = read1(world_file)

        if engine_identity == 0xFFFF:
            world["engine"] = ZZT_DATA

            world["torches"] = read2(world_file)
            world["torchlight_remaining"] = read2(world_file)
            world["energizer_remaining"] = read2(world_file)
            read2(world_file)  # unused data
            world["score"] = read2(world_file)
            name_length = read1(world_file)
            world["name"] = sread(world_file, 20)[:name_length]
            for count in xrange(0, 9):
                flag_length = read1(world_file)
                world["flags"].append(sread(world_file, 20)[:flag_length])
            world["time_passed"] = read2(world_file)
            world["time_passed2"] = read2(world_file)  # change name
            world["is_locked"] = read1(world_file)

            board_offset = 512  # parse boards
            for idx in xrange(0, world["board_count"] + 1):
                os.lseek(world_file, board_offset, 0)  # Jump to board data
                board_size = read2(world_file)

                # Boards don't get appended to the list until finished so incomplete boards aren't included
                world["boards"].append(parse_board(world["engine"], world_file))
                board_offset += board_size + 2
    except (TypeError, ValueError, OSError, EOFError):
        pass  # I thought this would catch superlocked files, but maybe not??

    return world


def render(tiles, stat_data, engine_data, render_num):
    canvas = Image.new("RGBA", (480, 350))
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
                    if stat["x-step"] > MAX_SIGNED_INT:
                        transporter_char = 60  # West
                    elif stat["x-step"] > 0:
                        transporter_char = 62  # East
                    elif stat["y-step"] <= MAX_SIGNED_INT:
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
            elif element in (elements[key] for key in engine_data["blank_elements"]):
                char = get_tile(32, fg_color, bg_color, True)

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

    world = parse_file(file_name)
    boards = world["boards"]

    if render_num == "A":
        for idx in xrange(0, len(boards) - 1):
            canvas = render(boards[idx]["tiles"], boards[idx]["stats"], world["engine"], idx)
            canvas.save(output + "-" + ("0" + str(idx))[-2:] + ".png")
            print boards[idx]["name"]
    else:
        if render_num == "?":
            render_num = random.randint(0, len(boards) - 1)
        else:
            render_num = int(render_num)
        canvas = render(boards[render_num]["tiles"], boards[render_num]["stats"], world["engine"], render_num)
        canvas.save(output + ".png")
        print boards[render_num]["name"]


if __name__ == "__main__":
    main()
