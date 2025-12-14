from os import fstat
from types import TracebackType


class DemoFileIO:
    def __init__(self, path: str) -> None:
        self.io = open(path, "rb")
        try:
            header = self.io.read(8)
            # Validate demo header
            if header != b"PBDEMS2\x00":
                raise ValueError("Demo header mismatch")
            self.size = fstat(self.io.fileno()).st_size
            # Skip the next 8 bytes (No reference found for these bytes)
            self.io.seek(16)
        except Exception:
            self.io.close()
            raise

    def read(self, size: int) -> bytes:
        return self.io.read(size)

    def tell(self) -> int:
        return self.io.tell()

    def close(self) -> None:
        self.io.close()

    @property
    def name(self) -> str:
        return self.io.name

    def seek(self, offset: int, whence: int = 0) -> int:
        return self.io.seek(offset, whence)

    def __enter__(self) -> "DemoFileIO":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.io.close()
