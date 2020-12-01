from ds.relational import OneToMany
from ds.vecs import V2, R2
from ds.gensym import FastGensym
from enum import Enum
from typing import Dict, List, NamedTuple, Optional, Union
from io import StringIO

import random
from contextlib import contextmanager

from .recs import RoomHandle, RoomType


class CreateRoom(NamedTuple):
    room_type: RoomType


class CarveTile(NamedTuple):
    position: V2
    old_owner: RoomHandle
    new_owner: RoomHandle


class FreezeRoom(NamedTuple):
    room: RoomHandle


CarveOp = Union[CreateRoom, CarveTile, FreezeRoom]
