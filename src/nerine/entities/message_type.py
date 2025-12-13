from dataclasses import dataclass, field

from nerine.proto.demo import EDemoCommands


@dataclass
class RawMessageType:
    cmd: int
    tick: int
    is_compressed: bool


@dataclass
class RawMessage:
    cmd: int
    tick: int
    data: bytes


@dataclass
class MessageType:
    cmd: EDemoCommands
    tick: int
    is_compressed: bool


@dataclass
class Message:
    cmd: EDemoCommands
    tick: int
    data: bytes = field(repr=False)
