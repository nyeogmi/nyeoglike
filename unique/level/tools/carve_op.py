import random
from contextlib import contextmanager
from enum import Enum
from io import StringIO
from typing import Dict, List, NamedTuple, Optional, Union

from ds.gensym import FastGensym
from ds.relational import OneToMany
from ds.vecs import R2, V2

from .recs import LinkType, RoomHandle, RoomType


class CreateRoom(NamedTuple):
    room_type: RoomType


class CarveTile(NamedTuple):
    position: V2
    old_owner: RoomHandle
    new_owner: RoomHandle


class FreezeRoom(NamedTuple):
    room: RoomHandle


class LinkRooms(NamedTuple):
    link_type: LinkType
    room0: RoomHandle
    room1: RoomHandle


CarveOp = Union[CreateRoom, CarveTile, FreezeRoom, LinkRooms]
