"""Local raster header parsing without pixel decoding."""

from struct import unpack


def image_size(data: bytes) -> tuple[int, int, str]:
    """Read dimensions from PNG IHDR or JPEG frame markers without decoding pixels."""
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 33 and data[12:16] == b"IHDR":
        width, height = unpack(">II", data[16:24])
        if width and height:
            return width, height, "png"
    if data.startswith(b"\xff\xd8"):
        offset = 2
        while offset + 3 < len(data):
            if data[offset] != 255:
                break
            while offset < len(data) and data[offset] == 255:
                offset += 1
            if offset >= len(data):
                break
            marker = data[offset]
            offset += 1
            if marker in (0xD9, 0xDA):
                break
            if marker == 0x01 or 0xD0 <= marker <= 0xD8:
                continue
            length = int.from_bytes(data[offset : offset + 2], "big")
            if length < 2 or offset + length > len(data):
                break
            if marker in (0xC0, 0xC1, 0xC2) and length >= 8:
                height, width = unpack(">HH", data[offset + 3 : offset + 7])
                if width and height:
                    return width, height, "jpeg"
            offset += length
    raise ValueError("Expected a PNG or baseline/progressive JPEG with valid dimensions.")
