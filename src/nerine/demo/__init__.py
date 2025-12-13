from io import FileIO


class Demo:
    def __init__(self, path: str):
        self.io = FileIO(path, "rb")
        # Calculate file size
        self.io.seek(0, 2)
        self.size = self.io.tell()
        # Validate header so start read bytes at 8th byte
        self.validate_header()

    def validate_header(self) -> None:
        self.io.seek(0)
        header = self.io.read(8)
        if header != b"PBDEMS2\x00":
            raise ValueError("Demo header mismatch")

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
