from bearlibterminal import terminal as blt

QUIT_KEY = (41, 224)

def key_handling():
    while blt.has_input():
        key = blt.read()
        if key in QUIT_KEY:
            blt.close()
            return True

        print(key)

if __name__ == '__main__':
    blt.open()
    blt.set(f"window.size=10x10, window.cellsize=48x48")
    blt.set("font: res/tilesets/Curses_square_24.png, size=24x24, resize=48x48")
    blt.set("window.title='SimplyRL'")
    blt.set("input.filter={keyboard, mouse+}")
    blt.composition(True)
    blt.refresh()

    quit = False

    while not quit:
        quit = key_handling()
        blt.refresh()

