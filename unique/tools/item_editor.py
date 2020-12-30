from display import Colors, ItemColors, IO, DoubleWide, Key, Keycodes, Screen, transact
from unique.item import Resource
from unique.sitemode.window import draw_window, Window


def main(io: IO):
    possible_glyphs = set(range(256))
    possible_glyphs.remove(ord("\n"))  # not a glyph
    possible_glyphs.remove(ord("\r"))  # not a glyph
    possible_glyphs.remove(ord("\t"))  # not a glyph

    class GlyphSelector(object):
        def __init__(self):
            self.sel_x = 0
            self.sel_y = 0

        @property
        def sel_i(self):
            return self.sel_y * 16 + self.sel_x

        def draw(self, lhs_x, lhs_y):
            for i in range(256):
                if i not in possible_glyphs:
                    continue
                grid_x = i % 16
                grid_y = i // 16

                drawer = io.draw().goto_xy(lhs_x + grid_x * 2, lhs_y + grid_y)
                if i == self.sel_i:
                    drawer.bg(Colors.TermHighlightBG)
                    drawer.fg(Colors.TermBG)
                drawer.puts(chr(i))

        def handle_key(self, key: Key):
            if key.match(Key.new(Keycodes.Up)):
                self.sel_y -= 1
            elif key.match(Key.new(Keycodes.Down)):
                self.sel_y += 1
            elif key.match(Key.new(Keycodes.Left)):
                self.sel_x -= 1
            elif key.match(Key.new(Keycodes.Right)):
                self.sel_x += 1
            else:
                return False

            self.sel_x %= 16
            self.sel_y %= 16
            return True

    class ColorSelector(object):
        def __init__(self):
            self.sel_x = 1
            self.sel_y = 1

        @property
        def sel_i(self):
            return self.sel_y * 3 + self.sel_x

        def handle_key(self, key: Key):
            if key.match(Key.new(Keycodes.Up)):
                self.sel_y -= 1
            elif key.match(Key.new(Keycodes.Down)):
                self.sel_y += 1
            elif key.match(Key.new(Keycodes.Left)):
                self.sel_x -= 1
            elif key.match(Key.new(Keycodes.Right)):
                self.sel_x += 1
            else:
                return False

            self.sel_x %= 3
            self.sel_y %= 3
            return True

        def draw(self, lhs_x, lhs_y):
            for i in range(9):
                if i not in possible_glyphs:
                    continue
                grid_x = i % 3
                grid_y = i // 3

                drawer = io.draw().goto_xy(lhs_x + grid_x * 2, lhs_y + grid_y)
                if i == self.sel_i:
                    drawer.bg(ItemColors.ALL[i]).putdw(DoubleWide.Grid)
                else:
                    drawer.bg(ItemColors.ALL[i]).fg(Colors.White1).putdw(
                        DoubleWide.Blank
                    )

    # TODO: Allow resource selection
    resource = Resource.Snack
    color = ColorSelector()
    glyph = GlyphSelector()

    state_glyph = True

    while True:
        io.draw().clear()

        fg, resource_glyph = resource.display()
        io.draw().goto_xy(80 // 2 - 1, 3).fg(fg).puts(resource_glyph)
        io.draw().goto_xy(80 // 2, 3).fg(ItemColors.ALL[color.sel_i]).puts(
            chr(glyph.sel_i)
        )

        lhs_x = 80 // 2 - 16
        lhs_y = 5
        glyph.draw(lhs_x, lhs_y)

        lhs_x = 80 // 2 - 24
        lhs_y = 8
        color.draw(lhs_x, lhs_y)
        key = io.getch()

        if state_glyph:
            if glyph.handle_key(key):
                continue
        else:
            if color.handle_key(key):
                continue

        if key.match(Key.new(Keycodes.Tab)):
            state_glyph = not state_glyph

        elif key.match(Key.new(Keycodes.Enter)):
            # TODO: Check resource type?
            window = draw_window(io.draw().goto(5, 14).box(75, 15).zeroed(), False)
            window.title_bar.copy().puts("Name item")

            name = ""
            while True:
                window.content.clear()
                window.content.copy().puts(name)
                key = io.getch()

                if key.match(Key.new(Keycodes.Enter)):
                    break
                elif key.match(Key.new(Keycodes.Backspace)):
                    name = name[:-1]
                elif key.match(Key.new(Keycodes.Escape)):
                    name = None
                    break
                elif key.text():
                    name += key.text()

            if name is None:
                continue

            with open("dumped_items.ascii", "at") as f:
                f.write(
                    """("{}", "\\x{:02x}", IC.{})\n""".format(
                        name, glyph.sel_i, ItemColors.name(ItemColors.ALL[color.sel_i])
                    )
                )
