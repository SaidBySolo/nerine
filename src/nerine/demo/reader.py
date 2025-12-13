import cramjam

from nerine.demo import Demo
from nerine.entities.message_type import (
    Message,
    MessageType,
    RawMessage,
    RawMessageType,
)
from nerine.proto.demo import *


class RawDemoReader:
    def __init__(self, demo: Demo):
        self.demo = demo
        # Move to the position after the header
        self.demo.io.seek(16)

    def read_raw_message_type(self):
        if self.demo.io.tell() >= self.demo.size:
            raise EOFError("End of stream")

        cmd_raw = self.demo.read_varint32()

        is_compressed = bool(cmd_raw & EDemoCommands.DEM_IsCompressed)

        cmd = cmd_raw & ~EDemoCommands.DEM_IsCompressed

        tick = self.demo.read_varint32()

        return RawMessageType(cmd, tick, is_compressed)

    def read_raw_message(self) -> RawMessage:
        msg_type = self.read_raw_message_type()

        data_size = self.demo.read_varint32()
        data = self.demo.io.read(data_size)

        if msg_type.is_compressed:
            data = cramjam.snappy.decompress_raw(data).read()

        return RawMessage(msg_type.cmd, msg_type.tick, data)

    def __iter__(self):
        while True:
            try:
                yield self.read_raw_message()
            except EOFError:
                break


class DemoReader:
    def __init__(self, demo: Demo):
        self.raw_reader = RawDemoReader(demo)

    def read_message_type(self) -> MessageType:
        raw_type = self.raw_reader.read_raw_message_type()
        return MessageType(
            cmd=EDemoCommands(raw_type.cmd),
            tick=raw_type.tick,
            is_compressed=raw_type.is_compressed,
        )

    def read_message(self) -> Message:
        raw_msg = self.raw_reader.read_raw_message()
        return Message(
            cmd=EDemoCommands(raw_msg.cmd),
            tick=raw_msg.tick,
            data=raw_msg.data,
        )

    def __iter__(self):
        while True:
            try:
                yield self.read_message()
            except EOFError:
                break
