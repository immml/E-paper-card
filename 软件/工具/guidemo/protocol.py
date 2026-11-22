# SPDX-License-Identifier: AGPL-3.0-or-later
from dataclasses import dataclass
import struct

SOF = 0xA5
VERSION = 1
MAX_PAYLOAD = 64
HEADER_SIZE = 7

GET_POWER = 0x01
SET_POWER = 0x02
BUTTON_EVENT = 0x10
USB_EVENT = 0x11


class ProtocolError(ValueError):
    pass


def crc16(data: bytes) -> int:
    crc = 0xFFFF
    for value in data:
        crc ^= value
        for _ in range(8):
            crc = ((crc >> 1) ^ 0xA001) if crc & 1 else crc >> 1
    return crc


@dataclass(frozen=True)
class Frame:
    command: int
    sequence: int
    payload: bytes = b""


def encode(frame: Frame) -> bytes:
    if len(frame.payload) > MAX_PAYLOAD:
        raise ProtocolError("payload too large")
    header = bytes((SOF, VERSION, frame.command, frame.sequence)) + struct.pack("<H", len(frame.payload)) + b"\0"
    return header + frame.payload + struct.pack("<H", crc16(header[1:] + frame.payload))


def decode(data: bytes) -> Frame:
    if len(data) < HEADER_SIZE + 2 or data[0] != SOF or data[1] != VERSION:
        raise ProtocolError("invalid header")
    payload_length = struct.unpack_from("<H", data, 4)[0]
    if payload_length > MAX_PAYLOAD or len(data) != HEADER_SIZE + payload_length + 2:
        raise ProtocolError("invalid length")
    if crc16(data[1:-2]) != struct.unpack_from("<H", data, len(data) - 2)[0]:
        raise ProtocolError("invalid crc")
    return Frame(data[2], data[3], data[HEADER_SIZE:-2])
