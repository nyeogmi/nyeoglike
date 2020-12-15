from typing import NamedTuple, Optional

from display import IO, Color, Colors, Drawer


class Window(NamedTuple):
    content: Drawer
    border: Drawer
    title_bar: Drawer
    button_bar: Drawer


def draw_window(
    base: Drawer, double=False, bg: Optional[Color] = None, fg: Optional[Color] = None
) -> Window:
    content = base.copy().zeroed().goto(0, 0)
    border = content.copy().expand(2, 1).zeroed()

    border.bg(Colors.TermBG).fg(Colors.TermFG).fillc(" ")
    border.bg(bg or Colors.TermBG).fg(fg or Colors.TermFG).goto(0, 0).etch(
        double=double
    )

    title_bar = (
        border.copy()
        .zeroed()
        .goto(2, 0)
        .box(border.bounds.size.x - 2, 1)
        .zeroed()
        .goto(0, 0)
    )
    button_bar = border.copy().zeroed()
    button_bar.goto(2, border.bounds.size.y - 1).box(
        border.bounds.size.x - 2, border.bounds.size.y
    )
    button_bar.zeroed().goto(0, 0)

    return Window(
        content=content, border=border, title_bar=title_bar, button_bar=button_bar
    )
