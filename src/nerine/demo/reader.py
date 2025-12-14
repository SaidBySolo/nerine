from types import TracebackType
from typing import Iterator

import cramjam

from nerine.demo.io import DemoFileIO
from nerine.entities.message_type import (
    Message,
    MessageType,
    RawMessage,
    RawMessageType,
)
from nerine.proto.common.demo import *


class BaseDemoReader:
    def __init__(self, path: str):
        self.io = DemoFileIO(path)

    def read_varint32(self) -> int:
        result = 0
        count = 0
        while True:
            byte = self.io.read(1)
            if not byte:
                raise EOFError("Unexpected end of stream while reading varint")

            b = ord(byte)

            result |= (b & 0x7F) << (7 * count)
            count += 1

            if not (b & 0x80):
                return result

            if count >= 5:
                raise ValueError("Varint32 too long (corrupt data)")

    def __repr__(self) -> str:
        return f"<{self.__class__.__module__}.{self.__class__.__name__} file={self.io.name} object at {hex(id(self))}>"

    def read_raw_message_type(self):
        if self.io.tell() >= self.io.size:
            raise EOFError("End of stream")

        cmd_raw = self.read_varint32()

        is_compressed = bool(cmd_raw & EDemoCommands.DEM_IsCompressed)

        cmd = cmd_raw & ~EDemoCommands.DEM_IsCompressed

        tick = self.read_varint32()

        return RawMessageType(cmd, tick, is_compressed)

    def read_raw_message(self) -> RawMessage:
        msg_type = self.read_raw_message_type()

        data_size = self.read_varint32()
        data = self.io.read(data_size)

        if msg_type.is_compressed:
            data = cramjam.snappy.decompress_raw(data).read()

        return RawMessage(msg_type.cmd, msg_type.tick, data)


class RawDemoReader(BaseDemoReader):
    def __iter__(self) -> Iterator[RawMessage]:
        while True:
            try:
                yield self.read_raw_message()
            except EOFError:
                break

    def __next__(self) -> RawMessage:
        return self.read_raw_message()

    def __enter__(self) -> "RawDemoReader":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.io.close()


class DemoReader(BaseDemoReader):
    def read_message_type(self) -> MessageType:
        raw_type = self.read_raw_message_type()
        return MessageType(
            cmd=EDemoCommands(raw_type.cmd),
            tick=raw_type.tick,
            is_compressed=raw_type.is_compressed,
        )

    def read_message(self) -> Message:
        raw_msg = self.read_raw_message()
        return Message(
            cmd=EDemoCommands(raw_msg.cmd),
            tick=raw_msg.tick,
            data=raw_msg.data,
        )

    def __iter__(self) -> Iterator[Message]:
        while True:
            try:
                yield self.read_message()
            except EOFError:
                break

    def __next__(self) -> Message:
        return self.read_message()

    def __enter__(self) -> "DemoReader":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.io.close()
