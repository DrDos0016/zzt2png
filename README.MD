# zzt2png

zzt2png is a command-line script to create PNG renders of boards in ZZT worlds.

## Usage

Either run without any command-line arguments and follow the prompts, or specify all arguments from the command-line.

python zzt2png.py <filename> <board> <output>

<filename> is the ZZT or Super ZZT world (or save) you wish to process.
<board> is the board number to use, starting with 0 for the title screen. Additionally use ? for a random board or A to render all boards.
<output> is the filename for the screenshot without a .png extension. If all boards are being rendered a numeric suffix is applied.

Additionally the INVISIBLE_MODE constant can be manually edited to change how invisible walls appear.

## License

Licensed under [Creative Commons Attribution-NonCommercial-ShareAlike 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/us/)
