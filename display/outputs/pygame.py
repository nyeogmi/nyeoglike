import pygame
import pygame.image
from display import Interactor, Key, Keycodes
from ds.vecs import V2

import os.path
import time

from typing import Optional
from ..palette import Colors

#  N_TILES = 256

class Font(object):
    def __init__(self, font_images, tile_size: V2, res_in_tiles: V2):
        assert isinstance(font_images, list) and len(font_images) == Colors.N
        assert isinstance(tile_size, V2)
        assert isinstance(res_in_tiles, V2)

        self._font_images = font_images
        self._tile_size = tile_size
        self._res_in_tiles = res_in_tiles
        self._n_tiles = self._res_in_tiles.x * self._res_in_tiles.y

    @property
    def tile_size(self) -> V2:
        return self._tile_size

    @classmethod
    def load(cls, filename: str, tile_size: V2):
        assert isinstance(filename, str)
        assert isinstance(tile_size, V2)

        font_image = pygame.image.load(os.path.join("images/fonts", filename)).convert_alpha()
        tile_width, tile_height = tile_size
        full_width, full_height = font_image.get_size()

        width_in_tiles = full_width//tile_width
        height_in_tiles = full_height//tile_height

        #  assert width_in_tiles * height_in_tiles == N_TILES

        font_images = [font_image.convert_alpha() for i in range(Colors.N)]
        for i in range(Colors.N):
            font_images[i].fill((*Colors.SWATCH[i], 255), special_flags=pygame.BLEND_MULT)
            font_images[i] = font_images[i].convert_alpha()

        return Font(font_images, tile_size, V2.new(width_in_tiles, height_in_tiles))

    def draw(self, screen, xy: V2, bg: int, fg: int, character: str):
        assert 0 <= bg < Colors.N
        assert 0 <= fg < Colors.N
        assert len(character) == 1

        # TODO: Use the right code page for an old machine: http://nerdlypleasures.blogspot.com/2015/04/ibm-character-fonts.html
        v = ord(character)
        ntiles_x = self._res_in_tiles.x
        if 0 <= v < self._n_tiles:
            xy0_src = V2.new(v % ntiles_x, v // ntiles_x) * self._tile_size
            xy0_dest = xy * self._tile_size

            src = [*xy0_src, *self._tile_size]
            dest = [*xy0_dest, *self._tile_size]
            screen.fill(Colors.SWATCH[bg], dest)
            screen.blit(self._font_images[fg], dest, area=src)


def start(interactor: Interactor):
    assert isinstance(interactor, Interactor)

    pygame.init()

    tile_size = V2(8, 16)

    screen, _ = interactor.view()
    pygame_screen = pygame.display.set_mode(list(screen.bounds.size * tile_size), flags=pygame.SCALED)
    font = Font.load("vga_8x16.png", tile_size)

    interactor.mark_updated()
    while not interactor.should_quit():
        screen, changed = interactor.view()

        old_cells = {}
        if changed:  # TODO: For now, always redraw
            with screen.lock():
                for xy in screen.bounds:
                    new_cell = screen[xy]
                    old_cell = old_cells.get(xy)
                    old_cells[xy] = new_cell
                    if old_cell != new_cell:
                        # pygame_screen.fill(Colors.SWATCH[Colors.TermBG.color])
                        font.draw(pygame_screen, xy, new_cell.bg, new_cell.fg, new_cell.character)

                pygame.display.flip()

        keys = []
        quit = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
                break
            elif event.type == pygame.KEYDOWN:
                key = identify_key(event)
                if key:
                    keys.append(key)
            else:
                # TODO: What other events do we care oabut?
                pass

        if quit:
            break

        interactor.handle_keys(keys)


_GENERIC_KEYS = set(map(ord, "abcdefghijklmnopqrstuvwxyz`0123456789-=[]\\;',./"))

# the other side of the tuple is shift
_SPECIAL_KEYS = {
    **{ord(k): (v, True) for k, v in [
        "~`", "!1", "@2", "#3", "$4", "%5", "^6", "&7", "*8", "(9", ")0", "_-", "+=",
        "{[", "}]", "|\\", ":;", "\"'", "<,", ">.", "?/",
    ]},

    **{k: (v, False) for k, v in {
        pygame.K_SPACE: Keycodes.Space,

        pygame.K_ESCAPE: Keycodes.Escape,
        pygame.K_TAB: Keycodes.Tab,
        pygame.K_RETURN: Keycodes.Enter,

        pygame.K_BACKSPACE: Keycodes.Backspace,
        pygame.K_DELETE: Keycodes.Delete,

        pygame.K_UP: Keycodes.Up,
        pygame.K_DOWN: Keycodes.Down,
        pygame.K_LEFT: Keycodes.Left,
        pygame.K_RIGHT: Keycodes.Right,
    }.items()}
}


def identify_key(event: pygame) -> Optional[Key]:
    control = bool(event.mod & pygame.KMOD_CTRL)
    shift = bool(event.mod & pygame.KMOD_SHIFT)
    alt = bool(event.mod & pygame.KMOD_ALT)
    caps = bool(event.mod & pygame.KMOD_CAPS)

    if event.key in _GENERIC_KEYS:
        code = chr(event.key)
    elif event.key in _SPECIAL_KEYS:
        code, force_shift = _SPECIAL_KEYS[event.key]
        if force_shift:
            shift = True
    else:
        return None

    return Key.new(
        keycode=code,
        control=control,
        shift=shift,
        alt=alt,
        caps_lock=caps
    )
